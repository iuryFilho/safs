import pandas as pd
from services import simulation_utils as sus


class DataCompiler:
    def __init__(self, metric_type: str, load_points: list[str]):
        if metric_type == "individual":
            self.filter_func = lambda: sus.filter_result_list_by_metric(
                self.metrics[0], self.simulation_results
            )
            self.length_func = lambda: len(self.simulation_results)
        elif metric_type == "grouped":
            self.filter_func = lambda: sus.filter_result_by_metric_list(
                self.metrics, self.simulation_results[0]
            )
            self.length_func = lambda: len(self.metrics)
        else:
            raise ValueError(f"Tipo de métrica não suportado: {metric_type}")
        self.load_points = load_points
        self.simulation_results = []
        self.metrics = []

    def compile_data(self) -> list[pd.DataFrame]:
        """
        Compiles data from simulation results and metrics.
        Returns:
            list[pd.DataFrame]: A list of DataFrames containing the compiled data.
        """
        length = self.length_func()
        metric_results = self.filter_func()
        if not metric_results:
            return [pd.DataFrame()] * length

        if self.load_points is not None and len(self.load_points) > 0:
            load_points_set = {str(l) for l in self.load_points}
            for i in range(len(metric_results)):
                loadpoint_col = metric_results[i]["LoadPoint"]
                first = loadpoint_col.iloc[0]
                if isinstance(first, float) and first.is_integer():
                    loadpoint_str = loadpoint_col.astype(int).astype(str)
                else:
                    loadpoint_str = loadpoint_col.astype(str)
                metric_results[i] = metric_results[i][
                    loadpoint_str.isin(load_points_set)
                ]

        final_results = sus.extract_repetitions(metric_results)
        del metric_results

        number_of_reps = sus.get_number_of_repetitions(final_results)
        average = sus.calculate_average(final_results)
        error = sus.calculate_standard_error(final_results, number_of_reps)
        del final_results

        dataframes = [pd.DataFrame() for _ in range(length)]

        for i in range(length):
            dataframes[i]["mean"] = average[i]
            dataframes[i]["error"] = error[i]

        return dataframes

    def set_simulation_results(self, simulation_results: list[pd.DataFrame]):
        """
        Sets the simulation results for the DataCompiler instance.
        Args:
            simulation_results (list[pd.DataFrame]): The simulation results to set.
        """
        self.simulation_results = simulation_results
        return self

    def set_metrics(self, metrics: list[str]):
        """
        Sets the metrics for the DataCompiler instance.
        Args:
            metrics (list[str]): The metrics to set.
        """
        self.metrics = metrics
        return self

    def reset_data(self):
        """
        Resets the simulation results and metrics to empty lists.
        This method clears the current state of the DataCompiler instance.
        """
        self.simulation_results = []
        self.metrics = []
        return self
