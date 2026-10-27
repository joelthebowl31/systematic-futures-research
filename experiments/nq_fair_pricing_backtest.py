#!/usr/bin/env python3
"""JJ Simon Fair Pricing Theory: preregistered exploratory NQ tick backtest.
Exploratory fixed matrix; optional AVWAP features without post-hoc selection.
"""
import argparse, csv, gzip, io, math, re, json
from pathlib import Path
from datetime import time
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

NY='America/New_York'; MT='America/Denver'; TICK=.25
TFS=(1,2,3,5); EXTENSIONS=(25,50,75,100); STOPS=(15,25,37.5,50,75); RRS=(1.5,2.,2.36)

def parse_time(s):
    s=str(s).strip().strip('"')
    m=re.fullmatch(r'(\d{8})\s+(\d{6})(?:[\s.]+(\d{1,9}))?',s)
    if m:
        base=pd.to_datetime(m[1]+m[2],format='%Y%m%d%H%M%S',errors='coerce')
        return base+pd.Timedelta(int(m[3].ljust(9,'0')),unit='ns') if m[3] and not pd.isna(base) else base
    return pd.to_datetime(s,errors='coerce')

def reverse_lines(path,block_size=1048576):
    with open(path,'rb') as f:
        f.seek(0,2); pos=f.tell(); pending=b''
        while pos:
            take=min(pos,block_size);pos-=take;f.seek(pos)
            parts=(f.read(take)+pending).split(b'\n');pending=parts[0]
            for line in reversed(parts[1:]):
                if line.strip():yield line.decode('utf-8-sig',errors='replace').rstrip('\r')
        if pending.strip():yield pending.decode('utf-8-sig',errors='replace')

def read_lines(path):
    op=gzip.open if str(path).lower().endswith('.gz') else open
    with op(path,'rt',encoding='utf-8-sig',errors='replace') as f:
        head=[next(f,'') for _ in range(25)]
    sample=''.join(head);delim=max((';',',','\t'),key=sample.count)
    first=next((s for s in head if s.strip()),'')
    header=bool(re.search(r'(?i)date|time|last|price|volume',first))
    def get_ts(line):
        row=next(csv.reader([line],delimiter=delim));ts=parse_time(row[0])
        if pd.isna(ts) and len(row)>1:ts=parse_time(row[0]+' '+row[1])
        return ts
    data=[s for s in head[1 if header else 0:] if s.strip()]
    times=[get_ts(s) for s in data[:20]];times=[x for x in times if not pd.isna(x)]
    descending=len(times)>1 and times[-1]<times[0]
    if descending and str(path).lower().endswith('.gz'):
        raise ValueError('Newest-first gz not supported; use original text export')
    print('Detected tick order:', 'newest-first' if descending else 'oldest-first',flush=True)
    if descending:it=reverse_lines(path)
    else:
        def gen():
            with op(path,'rt',encoding='utf-8-sig',errors='replace') as f:
                yield from f
        it=gen()
    for line in it:
        if not line.strip() or (header and line.strip()==first.strip()):continue
        try:
            fields=next(csv.reader([line],delimiter=delim))
            ts=parse_time(fields[0]); offset=0
            if pd.isna(ts) and len(fields)>2:
                ts=parse_time(fields[0]+' '+fields[1]);offset=1
            if pd.isna(ts):continue
            px=float(fields[offset+1])
            vol=float(fields[-1]) if len(fields)>=offset+5 else 1.0
            if not np.isfinite(px) or px<=0:continue
            yield ts,px,max(0.0,vol)
        except (ValueError,IndexError):continue

def iter_days(path,tz_name):
    tz=ZoneInfo(tz_name); last=None; day=None; times=[]; prices=[]; volumes=[]
    for naive,px,volume in read_lines(path):
        t=pd.Timestamp(naive)
        if t.tzinfo is None:t=t.tz_localize(tz,ambiguous='NaT',nonexistent='shift_forward')
        if pd.isna(t):continue
        t=t.tz_convert(NY)
        if last is not None and t<last:
            raise ValueError(f'Nonmonotonic timestamps: {last}, {t}. Check data format/order.')
        last=t;d=t.date()
        if day is None:day=d
        if d!=day:
            yield day,pd.DataFrame({'ts':pd.DatetimeIndex(times),'price':prices,'volume':volumes})
            day=d;times=[];prices=[];volumes=[]
        times.append(t);prices.append(px);volumes.append(volume)
    if times:yield day,pd.DataFrame({'ts':pd.DatetimeIndex(times),'price':prices,'volume':volumes})

def bars_for(ticks,tf):
    if ticks.empty:return pd.DataFrame()
    x=ticks.set_index('ts')
    o=x.price.resample(f'{tf}min',closed='left',label='right').ohlc()
    o['volume']=x.volume.resample(f'{tf}min',closed='left',label='right').sum()
    o['pv']=(x.price*x.volume).resample(f'{tf}min',closed='left',label='right').sum()
    return o.dropna(subset=['open','close'])

def pivots(b,wing=2):
    close=b.close.to_numpy();a=[]
    for i in range(wing,len(b)-wing):
        window=close[i-wing:i+wing+1]
        if close[i]==np.max(window) and np.count_nonzero(window==close[i])==1:
            a.append((b.index[i+wing],float(close[i]),1))
        if close[i]==np.min(window) and np.count_nonzero(window==close[i])==1:
            a.append((b.index[i+wing],float(close[i]),-1))
    return sorted(a,key=lambda x:x[0])

def roundtick(value):return round(value/TICK)*TICK

def avwap_at(b, t, anchor, include_anchor=False):
    """VWAP of completed bars since the anchor; exclude current signal bar's future."""
    if anchor is None or t < anchor:return float('nan')
    sl=b[(b.index>=anchor if include_anchor else b.index>anchor)&(b.index<=t)]
    vol=float(sl.volume.sum())
    return float(sl.pv.sum()/vol) if vol>0 else float('nan')

def signals_for_day(ticks,day,tf,exts,lookback,limit_time):
    b=bars_for(ticks,tf)
    if b.empty:return []
    ds=pd.Timestamp(day,tz=NY);open_t=ds.replace(hour=9,minute=30)
    news_t=ds.replace(hour=8,minute=30)  # 06:30 MT on standard AND daylight time
    end=open_t+pd.Timedelta(minutes=limit_time)
    rth=ticks[ticks.ts>=open_t]
    if rth.empty:return []
    fair=float(rth.price.iloc[0]);pivs=pivots(b)
    pi=0;hi=None;lo=None;out=[];last_displacement_anchor=None
    # 6h/12h directional bias from information that existed BEFORE the NY open
    past=b[b.index<=open_t]
    context_bias={}
    for hours in (6,12):
        past_window=past[past.index>=open_t-pd.Timedelta(hours=hours)]
        context_bias[hours]=int(np.sign(float(past_window.close.iloc[-1]-past_window.open.iloc[0]))) if len(past_window) else 0
    bodies=(b.close-b.open).abs().to_numpy()
    for i in range(1,len(b)):
        t=b.index[i];bar=b.iloc[i];prev=b.iloc[i-1]
        while pi<len(pivs) and pivs[pi][0]<t:
            conf,level,side=pivs[pi];pi+=1
            if side==1:hi=level
            else:lo=level
        body=abs(bar.close-bar.open);prevbody=abs(prev.close-prev.open)
        up=bool(bar.close>bar.open)
        displace=(body>prevbody and up!=(prev.close>prev.open) and
                  (bar.close>prev.high if up else bar.close<prev.low))
        # Historical displacement anchor may only activate at a completed bar close.
        # Anchor at this signal's close, but don't compute/use it for THIS signal.
        vwap_630=avwap_at(b,t,news_t)
        vwap_open=avwap_at(b,t,open_t)
        vwap_disp=avwap_at(b,t,last_displacement_anchor,include_anchor=True)
        if open_t<t<=end:
            extension_distance=abs(float(bar.close)-fair)
            for family in ('continuation','reversion'):
                move_direction=np.sign(bar.close-fair)
                if move_direction==0:continue
                side=int(move_direction if family=='continuation' else -move_direction)
                condition_displace=displace and (1 if up else -1)==side
                if side==1:condition_bos=(hi is not None and bar.close>hi and prev.close<=hi)
                else:condition_bos=(lo is not None and bar.close<lo and prev.close>=lo)
                for method,ok in (('displacement',condition_displace),('bos',condition_bos)):
                    if not ok:continue
                    for ext in (exts if family=='reversion' else (0,)):
                        if extension_distance<ext:continue
                        avs={'avwap_630':vwap_630,'avwap_open':vwap_open,'avwap_displacement':vwap_disp}
                        # compare same trading signals, with/without AVWAP (avoid claiming VWAP is fair value)
                        features={name+'_distance':round(side*(float(bar.close)-v),4) if np.isfinite(v) else np.nan for name,v in avs.items()}
                        features.update({name+'_aligned':(int(side*(float(bar.close)-v)>0) if np.isfinite(v) else np.nan) for name,v in avs.items()})
                        out.append({'date':str(day),'tf':tf,'family':family,'trigger':method,'extension':ext,
                                    'signal_time':t,'side':side,'fair':fair,'signal_close':float(bar.close),
                                    'opening_extension_points':round(extension_distance,2),
                                    'bias_6h':context_bias[6],'bias_12h':context_bias[12],
                                    'displacement_anchor_time_mt':str(last_displacement_anchor.tz_convert(MT)) if last_displacement_anchor is not None else '',
                                    **features})
        # Finished-bar displacement threshold set using past bodies only.
        hist=bodies[max(0,i-20):i]
        reference=max(15.0,1.5*float(np.median(hist))) if len(hist) else 15.0
        if displace and body>=reference:last_displacement_anchor=t
    seen=set();selected=[]
    for x in sorted(out,key=lambda z:z['signal_time']):
        k=(x['tf'],x['family'],x['trigger'],x['extension'])
        if k not in seen:seen.add(k);selected.append(x)
    return selected

def execute(ticks,sig,stop,rr,fee,slippage):
    # Next tick entry, directional slippage; market stops conservatively slipped.
    times=ticks.ts.astype('int64').to_numpy();px=ticks.price.to_numpy(dtype=float)
    i=np.searchsorted(times,sig['signal_time'].value,side='right')
    if i>=len(px):return None
    # stop accepting entries after 11:00 ET
    if pd.Timestamp(int(times[i]),tz='UTC').tz_convert(NY).time()>time(11,0):return None
    side=sig['side'];entry=px[i]+side*slippage*TICK
    dist=stop;target_dist=roundtick(stop*rr)
    target=entry+side*target_dist;stoplevel=entry-side*stop
    # reversion fair-price cap is another independently reported exit model
    modes=['fixed_R']+(['fair_price'] if sig['family']=='reversion' and side*(sig['fair']-entry)>0 else [])
    results=[]
    for mode in modes:
        actual_target=sig['fair'] if mode=='fair_price' else target
        # Vectorized first-touch search avoids a Python loop over millions of ticks.
        remaining=px[i+1:];
        hits_stop=np.flatnonzero(side*(remaining-stoplevel)<=0)
        hits_target=np.flatnonzero(side*(remaining-actual_target)>=0)
        idx_stop=int(hits_stop[0])+i+1 if len(hits_stop) else len(px)
        idx_target=int(hits_target[0])+i+1 if len(hits_target) else len(px)
        # One date per streamed tick chunk; close at last available tick for the session.
        end_index=min(idx_stop,idx_target,len(px)-1)
        if end_index==idx_stop:
            status='stop';exitpx=px[end_index]-side*slippage*TICK
        elif end_index==idx_target:
            status='target';exitpx=actual_target
        else:
            status='end_of_day';exitpx=px[end_index]-side*slippage*TICK
        gross=(exitpx-entry)*side*20
        net=gross-fee
        results.append(dict(**{k:v for k,v in sig.items() if k!='signal_time' and not (k.startswith('avwap_') or k.startswith('bias_') or k.startswith('opening_extension_') or k=='displacement_anchor_time_mt')},
             signal_time_mt=str(sig['signal_time'].tz_convert(MT)),
             entry_time_mt=str(pd.Timestamp(int(times[i]),tz='UTC').tz_convert(MT)),
             exit_time_mt=str(pd.Timestamp(int(times[end_index]),tz='UTC').tz_convert(MT)),
             entry=entry,exit=exitpx,stop_points=stop,target_R=rr,exit_model=mode,
             exit_reason=status,gross_usd=round(gross,2),net_usd=round(net,2),
             net_R=round(net/(stop*20),4),holding_ticks=end_index-i,
             **{k:v for k,v in sig.items() if k.startswith('avwap_') or k.startswith('bias_') or k.startswith('opening_extension_') or k=='displacement_anchor_time_mt'}))
    return results

def stats(df):
    if df.empty:return pd.DataFrame()
    keys=['tf','family','trigger','extension','stop_points','target_R','exit_model']
    rows=[]
    for k,g in df.groupby(keys,dropna=False):
        daily=g.groupby('date').net_usd.sum().sort_index(); equity=daily.cumsum()
        dd=(equity.cummax().clip(lower=0)-equity).max()
        rows.append(dict(zip(keys,k),trades=len(g),wins=int((g.net_usd>0).sum()),
             win_pct=round(100*(g.net_usd>0).mean(),2),net_usd=round(g.net_usd.sum(),2),
             mean_R=round(g.net_R.mean(),4),profitable_days=int((daily>0).sum()),
             trading_days=len(daily),closed_day_dd=round(float(dd),2)))
    return pd.DataFrame(rows).sort_values(['family','trigger','tf','extension','stop_points','target_R'])

def main():
    p=argparse.ArgumentParser(description='NQ Fair Pricing Theory event-study and backtest')
    p.add_argument('--input',nargs='+',required=True);p.add_argument('--out',default='results_NQ_FairPricing')
    p.add_argument('--input-tz',default=MT);p.add_argument('--max-days',type=int,default=0)
    p.add_argument('--fee',type=float,default=5.,help='Round-trip NQ commission per contract ($)')
    p.add_argument('--slippage-ticks',type=float,default=1.0);p.add_argument('--max-signals-minute',type=int,default=90)
    args=p.parse_args();dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    pd.DataFrame([vars(args)]).to_json(dest/'run_config.json',orient='records',indent=2)
    all_signals=[];all_trades=[];day_seen=set();days=0
    for path in args.input:
        print('\nCONTRACT:',Path(path).name,flush=True)
        # collect overnight + morning bars from previous calendar day for structure and bias
        prev=None
        for day,ticks in iter_days(path,args.input_tz):
            if day in day_seen:prev=ticks;continue
            if not (day.weekday()<5):prev=ticks;continue
            day_seen.add(day);days+=1
            context=pd.concat([prev,ticks],ignore_index=True) if prev is not None else ticks
            signals=[]
            for tf in TFS:signals.extend(signals_for_day(context,day,tf,EXTENSIONS,12,args.max_signals_minute))
            for s in signals:
                s['contract']=Path(path).stem
                all_signals.append({**{k:v for k,v in s.items() if k!='signal_time'},'signal_time_mt':str(s['signal_time'].tz_convert(MT))})
                for stop in STOPS:
                    for rr in RRS:
                        r=execute(ticks,s,stop,rr,args.fee,args.slippage_ticks)
                        if r:
                            for rec in r:rec['contract']=Path(path).stem
                            all_trades.extend(r)
            print(f'{day} sessions={days} signals={len(signals)} trade_rows={len(all_trades)}',flush=True)
            prev=ticks
            if args.max_days and days>=args.max_days:break
        if args.max_days and days>=args.max_days:break
    sig=pd.DataFrame(all_signals);tr=pd.DataFrame(all_trades)
    sig.to_csv(dest/'signals.csv',index=False)
    tr.to_csv(dest/'trades.csv.gz',index=False,compression='gzip')
    summary=stats(tr);summary.to_csv(dest/'summary.csv',index=False)
    if len(tr):
        contract_stats=tr.groupby(['contract','tf','family','trigger','extension','stop_points','target_R','exit_model']).agg(
            trades=('net_usd','size'),wins=('net_usd',lambda a:int((a>0).sum())),net_usd=('net_usd','sum'),mean_R=('net_R','mean')).reset_index()
        contract_stats.to_csv(dest/'by_contract.csv',index=False)
        av_rows=[]
        for name in ('avwap_630','avwap_open','avwap_displacement'):
            flag=name+'_aligned'
            if flag not in tr:continue
            subset=tr[tr[flag].notna()].copy()
            for (tf,fam,trigger,ext,stop,rr,ex,aligned),g in subset.groupby(
                ['tf','family','trigger','extension','stop_points','target_R','exit_model',flag]):
                av_rows.append({'anchor':name,'aligned':int(aligned),'tf':tf,'family':fam,'trigger':trigger,
                    'extension':ext,'stop_points':stop,'target_R':rr,'exit_model':ex,
                    'trades':len(g),'wins':int((g.net_usd>0).sum()),'win_pct':round(100*(g.net_usd>0).mean(),2),
                    'net_usd':round(g.net_usd.sum(),2),'mean_R':round(g.net_R.mean(),4),
                    'contracts':g.contract.nunique(),'days':g.date.nunique()})
        pd.DataFrame(av_rows).to_csv(dest/'avwap_comparison.csv',index=False)
        tr[[c for c in tr.columns if c.startswith('avwap_') or c in ('contract','date','tf','family','trigger','extension','stop_points','target_R','exit_model','net_R','net_usd')]].to_csv(dest/'avwap_trade_tags.csv.gz',index=False,compression='gzip')
        # Preregistered primary report: first setup chronologically across ALL families, per day/stop/rr/mode
        primary=tr[tr.exit_model=='fixed_R'].copy()
        primary['when']=pd.to_datetime(primary.signal_time_mt,format='ISO8601',utc=True)
        first=primary.sort_values(['date','stop_points','target_R','when']).drop_duplicates(['date','stop_points','target_R'],keep='first')
        first.to_csv(dest/'first_signal_portfolio.csv',index=False)
        stats(first).to_csv(dest/'first_signal_summary.csv',index=False)
    print('DONE:',dest,'days',days,'signals',len(sig),'trade rows',len(tr),flush=True)
    print('NOTE: Opening-price reversion and continuation are hypotheses, not verified JJ Simon trade performance.')
    print('NOTE: This first implementation is a daily-session model; news calendar/news-event testing is NOT included.')
if __name__=='__main__':main()
