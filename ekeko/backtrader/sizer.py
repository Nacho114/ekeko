import backtrader as bt 

class FractionOfPorfolioSizer(bt.Sizer):
    """

    """
    params = (('percents', 0.05),)

    def _getsizing(self, comminfo, cash, data, isbuy):
      if isbuy:
        portfolio_value = self.strategy.broker.getvalue()
        max_size_value = portfolio_value * self.params.percents 
        working_capital = min(max_size_value, cash)
        stock_price = data[0]
        size = working_capital / stock_price

        #print(f'portfolio value {portfolio_value}')
        #print(f'cash {cash}')
        #print(f'working capital {working_capital}')
        #print(f'size {size}')
        #print('-'*10)
      else:
        size = self.broker.getposition(data).size
      return size
