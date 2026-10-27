# Variational: when growth metrics hide a product constraint
**Joel Hugentobler | Portfolio adaptation of October 12–13, 2026 research**

## Question
Can treasury receipts grow while the economics of the market maker supporting them weaken?

My original Variational research examined the distinction between treasury allocations and the residual profitability of the Omni Liquidity Provider (OLP). This case study preserves the analytical framework. It does not reproduce the original financial dataset or claim a current investment recommendation.

## Model
Under the 20% treasury-share assumption used in that research:

```text
Gross spreads = trading volume × realized spread capture
Treasury receipts = gross spreads × treasury share
OLP profit = gross spreads − market-making costs − rewards − treasury receipts
```

A dollar saved on market-making costs improves OLP profit, with other terms fixed. It does not automatically increase treasury receipts. Any token benefit requires another mechanism, such as additional trading activity or a changed allocation.

## A useful sensitivity
A 20% reduction in spread capture requires 25% more volume just to maintain gross spreads:

```text
Required volume multiplier = 1 / (1 − 0.20) = 1.25
```

If rewards grow with volume, holding gross spreads constant can still reduce OLP profit. The cost reduction needed to preserve profit depends on the starting cost and reward mix.

The [cost-hurdle calculator](../experiments/variational_cost_hurdle.py) implements the algebra from the original report's technical appendix. Its command-line example uses explicitly synthetic inputs, not Variational financial observations.

## Product implications
These are implications I would investigate, not claims that I shipped changes for Variational:
- **Pricing:** evaluate tighter spreads against both additional volume and contribution economics.
- **Capacity:** distinguish economically offset exposure from capital actually available to support new positions.
- **Metrics:** track treasury receipts alongside residual profit, committed capital, and capacity constraints.
- **Discovery:** ask what limits additional customer activity: price, funding, eligibility, or operational capacity.
- **Decision:** establish the evidence needed before treating growth as financially sustainable.

## What would change the conclusion?
Reconciled reporting windows, demonstrated capital productivity, durable financing arrangements, and evidence that pricing improvements produce sufficient incremental activity.

## Evidence boundary
The original drafts examined published financial disclosures and protocol documentation, but noted unresolved reporting-window alignment and source reconciliation. This compact case therefore omits their historical figures, forecasts, valuation outputs, and launch recommendation. It is an analytical work sample, not a current description of protocol policy. The full investment draft requires further source verification before publication.

