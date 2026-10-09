"""Moving-average long/cash signal."""
def moving_average_signal(close, fast=20, slow=50):
    if not 0 < fast < slow:
        raise ValueError("Expected 0 < fast < slow")
    fast_ma = close.rolling(fast).mean()
    slow_ma = close.rolling(slow).mean()
    return (fast_ma > slow_ma).astype(int).where(slow_ma.notna(), 0)
