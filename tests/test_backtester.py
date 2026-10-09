import unittest
import pandas as pd
from strategy import moving_average_signal
from backtester import backtest
from performance import summarize

class BacktestTests(unittest.TestCase):
    def test_no_signal_during_warmup(self):
        signal = moving_average_signal(pd.Series([1., 2., 3., 4.]), 2, 3)
        self.assertEqual(signal.tolist()[:2], [0, 0])

    def test_lagged_position(self):
        prices = pd.Series([100., 110., 121.])
        signals = pd.Series([0, 1, 1])
        result = backtest(prices, signals, cost_bps=0)
        self.assertEqual(result["position"].tolist(), [0., 0., 1.])
        self.assertAlmostEqual(result["strategy_return"].iloc[1], 0)
        self.assertAlmostEqual(result["strategy_return"].iloc[2], .1)

    def test_entry_cost_once(self):
        result = backtest(pd.Series([100., 100., 100.]),
                          pd.Series([1, 1, 1]), cost_bps=5)
        self.assertAlmostEqual(result["strategy_return"].sum(), -.0005)

    def test_no_drawdown_for_positive_constant_returns(self):
        self.assertAlmostEqual(summarize(pd.Series([.01, .01, .01]))["max_drawdown"], 0)

if __name__ == "__main__":
    unittest.main()
