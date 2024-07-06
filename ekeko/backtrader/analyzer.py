import backtrader as bt
from collections import OrderedDict

class EkekoTradeTracker(bt.Analyzer):
    def __init__(self):
        self.trades = OrderedDict()

    def notify_trade(self, trade: bt.trade.Trade):
        if trade.isclosed:
            trade_info = {
                'ticker': trade.data._name, #type: ignore
                'pnl': trade.pnl,
                'pnlcomm': trade.pnlcomm
            }
            close_datetime = bt.num2date(trade.dtclose)
            if close_datetime in self.trades:
                self.trades[close_datetime].append(trade_info)
            else:
                self.trades[close_datetime] = [trade_info]

    def get_analysis(self) -> OrderedDict:
        return self.trades
