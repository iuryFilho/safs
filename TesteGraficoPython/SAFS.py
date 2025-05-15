# -*- coding: utf-8 -*-

import pandas as pd  # for csv manipulation
import glob  # for filtering
import scipy.stats as st  # for statistics
import matplotlib.pyplot as plt
import extraction as ex  # for extracting data from csv files


metrics = {
    "BBP": ("BitRate blocking probability", "BitRateBlockingProbability.csv"),
    "GRB": ("General requested bitRate", "BitRateBlockingProbability.csv"),
}

# aux
markers = ["o", "v", "^", "s", "P", "x", "D", "_", "*", "2"]
linestyles = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-", "--"]


# def extractDFS(base_directory, metric):
#     metric_name, file_suffix = metrics[metric]
#     file_paths = get_csv_paths(base_directory, file_suffix)
#     labels = extract_labels_from_paths(file_paths)
#     simulation_results = load_simulation_results(file_paths)
#     del file_paths

#     metric_results = filter_metric(metric_name, simulation_results)
#     del simulation_results

#     loads = extract_load_points(metric_results)
#     repetitions_data = extract_repetitions(metric_results)
#     del metric_results

#     number_of_replicas = get_number_of_repetitions(repetitions_data)
#     average = calculate_average(repetitions_data)
#     error = calculate_standard_error(repetitions_data, number_of_replicas)
#     del repetitions_data

#     dfs = [pd.DataFrame() for i in range(len(average))]

#     for i in range(len(average)):
#         dfs[i]["loads"] = loads
#         dfs[i]["mean"] = average[i]
#         dfs[i]["error"] = error[i]
#     return dfs, labels


# def calculate_standard_error(repetitions_data, number_of_replicas):
#     return [st.sem(d, axis=1, ddof=number_of_replicas - 1) for d in repetitions_data]


# def get_number_of_repetitions(repetitions_data: list[pd.DataFrame]) -> int:
#     """
#     Returns the number of repetitions in the replicate data.
#     Args:
#         repetitions_data (list[DataFrame]): List of DataFrames containing the replicate data.
#     Returns:
#         int: The number of repetitions.
#     """
#     return len(repetitions_data[0].columns)


# def calculate_average(replicate_data: list[pd.DataFrame]) -> list:
#     """
#     Calculates the average of the replicate data.
#     Args:
#         replicate_data (list[DataFrame]): List of DataFrames containing the replicate data.
#     Returns:
#         list: A list of averages for each DataFrame.
#     """

#     return [d.mean(axis=1).tolist() for d in replicate_data]


# def extract_repetitions(simulation_results: list[pd.DataFrame]) -> list:
#     """
#     Extracts the repetitions data from the simulation results.
#     Args:
#         simulation_results (list[DataFrame]): List of DataFrames containing the simulation results.
#     Returns:
#         list: A list of DataFrames containing the repetitions data.
#     """

#     return [d.filter(like="rep", axis=1) for d in simulation_results]


# def extract_load_points(simulation_results: list[pd.DataFrame]) -> list:
#     """
#     Extracts the load points from the simulation results.
#     Args:
#         simulation_results (list[DataFrame]): List of DataFrames containing the simulation results.
#     Returns:
#         list: A list of load points.
#     """

#     return simulation_results[0]["LoadPoint"].tolist()


# def plot_line_graph(path, chosen_metrics, loads=[]):
#     filename_prefix = path.split("/")[-1] + "_Line_"
#     # BBP
#     x_label = "Carga na rede (Erlangs)"
#     for metric in chosen_metrics:
#         dfs, labels = extractDFS(path, metric)
#         if loads == []:
#             loads = dfs[0]["loads"].tolist()
#         a = f"{path}/{filename_prefix}{metric}.png"
#         auxPlotLine(
#             dfs,
#             loads,
#             sol=labels,
#             x_label=x_label,
#             y_label=metrics[metric][0],
#             show=True,
#             arq=a,
#         )


# def auxPlotLine(dfs, loads, sol, x_label, y_label, show, arq, lp="lower center", nc=5):
#     print(dfs)
#     fs = 27
#     plt.figure(figsize=(10, 7))
#     for i in range(len(dfs)):
#         x = dfs[i]["loads"]
#         y = dfs[i]["mean"]
#         e = dfs[i]["error"]
#         plt.errorbar(
#             x,
#             y,
#             xerr=0,
#             yerr=e,
#             linestyle=linestyles[i],
#             marker=markers[i],
#             label=sol[i],
#         )
#         plt.xticks(x, loads)

#     plt.xlabel(x_label, fontsize=fs)
#     plt.ylabel(y_label, fontsize=fs)
#     plt.xticks(fontsize=fs)
#     plt.yticks(fontsize=fs)
#     plt.grid(axis="y")
#     if len(sol) < nc:
#         nc = len(sol)

#     plt.legend(loc=lp, ncol=nc, fontsize=fs, bbox_to_anchor=(0.5, -0.43))
#     if arq != "":
#         plt.savefig(arq, dpi=150, bbox_inches="tight")
#     if show:
#         plt.show()
#     plt.close()


if __name__ == "__main__":
    simulation_path = "./TesteGraficoPython/simulations"
    x = ex.get_simulations_directories(simulation_path)
    # x = get_csv_suffixes(simulation_path)
    print(x)
    # plot_line_graph(simulation_path, ["BBP"], ["1", "2", "3", "4", "5"])
