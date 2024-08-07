import backtrader as bt
import pandas as pd
import ekeko


class EkekoCerebro:
    def __init__(self):
        self.cerebro = bt.Cerebro()
        self.tickers: list[str] = []

    def adddatas(self, stock_dfs: dict[str, pd.DataFrame]):
        for ticker, stock_df in stock_dfs.items():
            self.adddata(stock_df, ticker)

    def adddata(self, df: pd.DataFrame, name: str):
        data = bt.feeds.PandasData(dataname=df)  # type: ignore
        self.cerebro.adddata(data, name=name)
        self.tickers.append(name)

    def format_analysis_results(self, results) -> dict:
        transactions = results.analyzers.transactions.get_analysis()
        transactions = _format_transactions(transactions)

        trades = results.analyzers.tradetracker.get_analysis()
        trades = _format_trade_tracker(trades)

        stacked_trades = _stack_trades(trades)

        trade_analysis = results.analyzers.tradeanalyzer.get_analysis()
        trade_analysis = _format_trade_analyzer_results(trade_analysis)

        drawdown = results.analyzers.drawdown.get_analysis()

        positionsvalue = results.analyzers.positionsvalue.get_analysis()
        positionsvalue = _format_positions_value(positionsvalue, self.tickers)

        analysis_results = {
            "transactions": transactions,
            "trades": trades,
            "stacked_trades": stacked_trades,
            "drawdown": drawdown,
            "trade_analysis": trade_analysis,
            "positionsvalue": positionsvalue,
        }

        return analysis_results

    def run(self):
        self.cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="tradeanalyzer")
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        self.cerebro.addanalyzer(
            bt.analyzers.PositionsValue, _name="positionsvalue", cash=True
        )
        self.cerebro.addanalyzer(
            ekeko.backtrader.EkekoTradeTracker, _name="tradetracker"
        )

        results = self.cerebro.run()[0]
        analysis_results = self.format_analysis_results(results)

        return results, analysis_results


def _stack_trades(trades) -> pd.DataFrame:
    dfs = []
    for ticker, trade in trades.items():
        df = trade.copy()
        df.insert(loc=0, column="ticker", value=ticker)
        dfs.append(df)

    stacked_trades = pd.concat(dfs)

    return stacked_trades.sort_values(by=["pnl_norm"], ascending=False)


def _format_trade_tracker(trade_analysis) -> dict[str, pd.DataFrame]:
    result = {}

    for date, trades in trade_analysis.items():
        for trade in trades:
            ticker = trade["ticker"]
            if ticker not in result:
                result[ticker] = []
            trade_data = {
                "date": date,
                "price": trade["price"],
                "pnl": trade["pnl"],
                "pnlcomm": trade["pnlcomm"],
                "pnl_norm": trade["pnl"] / trade["price"],
                "pnlcomm_norm": trade["pnlcomm"] / trade["price"],
            }
            result[ticker].append(trade_data)

    # Convert lists to DataFrames
    for ticker, trade_list in result.items():
        df = pd.DataFrame(trade_list)
        df.set_index("date", inplace=True)
        result[ticker] = df

    return result


def _format_transactions(transactions_analysis):
    result = {}

    for date, trades in transactions_analysis.items():
        for trade in trades:
            size, price, _, ticker, value = trade
            if ticker not in result:
                result[ticker] = []
            trade_data = {"date": date, "size": size, "price": price, "value": value}
            result[ticker].append(trade_data)

    # Convert lists to DataFrames
    for ticker, trade_list in result.items():
        df = pd.DataFrame(trade_list)
        df.set_index("date", inplace=True)
        result[ticker] = df

    return result


def _format_trade_analyzer_results(trade_analysis):
    max_drawdown = trade_analysis.get("drawdown", {}).get("max", 0)
    num_trades = trade_analysis.get("total", {}).get("total", 0)
    num_winners = trade_analysis.get("won", {}).get("total", 0)
    num_losers = trade_analysis.get("lost", {}).get("total", 0)

    total_pnl = trade_analysis.get("pnl", {}).get("net", {}).get("total", 0)
    avg_pnl = trade_analysis.get("pnl", {}).get("net", {}).get("average", 0)

    avg_winner_pnl = trade_analysis.get("won", {}).get("pnl", {}).get("average", 0)
    avg_loser_pnl = trade_analysis.get("lost", {}).get("pnl", {}).get("average", 0)

    metrics = {
        "max_drawdown": max_drawdown,
        "num_trades": num_trades,
        "num_winners": num_winners,
        "num_losers": num_losers,
        "avg_pnl_per_trade": avg_pnl,
        "avg_pnl_winning_trades": avg_winner_pnl,
        "avg_pnl_losing_trades": avg_loser_pnl,
    }

    return metrics


def _format_positions_value(positions_value, tickers: list[str]):

    columns = tickers + ["cash"]

    df = pd.DataFrame.from_dict(positions_value, orient="index", columns=columns)
    df["equity"] = df[list(df.columns)].sum(axis=1)
    initial_cash = df["equity"].iloc[0]
    df["normalized equity"] = df["equity"] / initial_cash

    return df
