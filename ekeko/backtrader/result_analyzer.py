class EkekoResultAnalyzer:

    def __init__(self, analysis_result):
        self.analysis_result = analysis_result
        self.transactions = analysis_result['transactions']
        self.trades = analysis_result['trades']
        self.drawdown_dict = analysis_result['drawdown']
        self.trade_analysis = analysis_result['trade_analysis']

    def print(self):
        _print_header('Transactions')
        self.show_transactions()
        _print_header('Trades')
        self.show_trades()
        _print_header('Drawdown')
        self.show_drawdown()
        _print_header('Trade Analysis')
        self.show_trade_analysis()

    def show_drawdown(self):
        drawdown_dict = self.drawdown_dict
        def format_number(num):
            return f"{num:.2f}"

        def format_percentage(num):
            return f"{num}%"

        print("Drawdown Analysis:")
        print("\nCurrent Drawdown:")
        print(f"  Length: {drawdown_dict['len']} periods")
        print(f"  Percentage: {format_percentage(drawdown_dict['drawdown'])}")
        print(f"  Monetary Value: {format_number(drawdown_dict['moneydown'])} $nits")

        print("\nMaximum Drawdown:")
        print(f"  Length: {drawdown_dict['max']['len']} periods")
        print(f"  Percentage: {format_percentage(drawdown_dict['max']['drawdown'])}")
        print(f"  Monetary Value: {format_number(drawdown_dict['max']['moneydown'])} $")

    def show_transactions(self):
        for ticker, df in self.transactions.items():
            print(f"Ticker: {ticker}")
            _print_dataframe(df)

    def show_trades(self):
        for ticker, df in self.trades.items():
            print(f"Ticker: {ticker}")
            _print_dataframe(df)\

    def show_trade_analysis(self):
        _print_nested_dict(self.trade_analysis)


###############################################################################
###############################################################################
### Utilities
###############################################################################
###############################################################################

def _print_header(title):
    print("-"*6, " ", title, " ", "-"*6)

def _print_dataframe(df):
    print(df.to_string())
    print()

def _print_nested_dict(d, indent=0):
    for key, value in d.items():
        print('  ' * indent + str(key) + ':')
        if isinstance(value, dict):
            _print_nested_dict(value, indent+1)
        else:
            print('  ' * (indent+1) + str(value))

