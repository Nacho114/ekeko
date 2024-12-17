from itertools import product
from typing import Dict, List, Tuple, Callable, Any
import pandas as pd

from ekeko.backtrader.engine import Engine, Strategy, Trader
from ekeko.backtrader.report import Report

# Optimizer Class
class Optimizer:
    def __init__(
        self,
        strategy: Strategy,
        trader: Trader,
        stock_dfs: Dict[str, pd.DataFrame],
        broker_builder,
        param_grid: Dict[str, List],
    ) -> None:
        """
        Args:
            strategy: The strategy instance to optimize.
            trader: The trading logic.
            stock_dfs: A dictionary of stock data.
            broker_builder: Builder for the broker class.
            param_grid: A dictionary with parameter names as keys and a list of values to try.
        """
        self.strategy = strategy
        self.trader = trader
        self.stock_dfs: Dict[str, pd.DataFrame] = stock_dfs
        self.broker_builder = broker_builder
        self.param_grid: Dict[str, List] = param_grid

    def _evaluate(self, params: Dict) -> Tuple[Dict, Report]:
        """Run the strategy with given params and return a Report."""
        # Reset strategy with new params
        self.strategy.set_params(**params)

        # Run the engine with the current strategy
        engine = Engine(self.trader, self.strategy, self.broker_builder)
        report = engine.run()

        return params, report

    def optimize(self) -> "OptimizationReport":
        """Perform grid search over the parameter grid."""
        param_combinations: List[Dict] = [
            dict(zip(self.param_grid.keys(), values))
            for values in product(*self.param_grid.values())
        ]

        results: List[Tuple[Dict, Report]] = []

        print(f"Testing {len(param_combinations)} parameter combinations...")

        for params in param_combinations:
            result = self._evaluate(params)
            results.append(result)

        return OptimizationReport(results, self.param_grid)



class OptimizationReport:
    def __init__(self, optimization_results: List[Tuple[Dict, Report]], param_grid: Dict[str, List]) -> None:
        """
        Args:
            optimization_results: List of parameter combinations and their corresponding Reports.
            param_grid: The grid of parameters tested.
        """
        self.grid_results = optimization_results
        self.param_grid = param_grid

    def get_metric_matrix(self, metric_fn: Callable[[Any], float] | None = None) -> pd.DataFrame:
        """
        Generate a matrix (DataFrame) for a given metric function.

        Args:
            metric_fn: A lambda or callable function to compute the metric from a Report.
                       Defaults to portfolio percentage growth.

        Returns:
            A pandas DataFrame representing the metric across all combinations.
        """
        if metric_fn is None:
            metric_fn = lambda report: report.portfolio_statistics['percentage_growth']

        # Flatten results and extract metrics
        records = []
        param_names = list(self.param_grid.keys())  # Extract the parameter names

        for params, report in self.grid_results:
            record = {name: params[name] for name in param_names}
            record["metric_value"] = metric_fn(report)
            records.append(record)

        # Create a DataFrame of results
        result_df = pd.DataFrame(records)
        return result_df

    def get_max_metric_report(self, metric_fn: Callable[[Any], float] | None = None) -> Tuple[Dict, Any]:
        """
        Find the parameters and Report corresponding to the maximum value of the given metric.

        Args:
            metric_fn: A lambda or callable function to compute the metric from a Report.
                       Defaults to portfolio percentage growth.

        Returns:
            A tuple containing the parameters and the corresponding Report.
        """
        if metric_fn is None:
            metric_fn = lambda report: report.portfolio_statistics['percentage_growth']

        # Evaluate the metric and find the maximum
        best_params = None
        best_report = None
        max_metric_value = float("-inf")

        for params, report in self.grid_results:
            metric_value = metric_fn(report)
            if metric_value > max_metric_value:
                max_metric_value = metric_value
                best_params = params
                best_report = report

        print(f"\nMax Metric Value: {max_metric_value:.4f} at Parameters: {best_params}")
        return best_params, best_report
