import matplotlib
import matplotlib.pyplot as plt
import scipy.stats as st
import pandas as pd
import os.path as op
from typing import TypeAlias

from control.utils import Logger
import control.extraction as ex


GroupedMetricT: TypeAlias = dict[str, list[str]]

matplotlib.use("agg")

LOG_ENABLE = True
log = Logger(LOG_ENABLE, __name__).log

markers = ["o", "v", "^", "s", "P", "x", "D", "_", "*", "2"]
linestyles = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-", "--"]
hatches = ["", "/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]


def calculate_standard_error(repetitions_data, number_of_reps):
    return [
        st.sem(d, axis=1, ddof=number_of_reps - 1).tolist() for d in repetitions_data
    ]


def get_number_of_repetitions(results_data: list[pd.DataFrame]) -> int:
    """
    Returns the number of repetitions in the results data.
    Args:
        results_data (list[DataFrame]): List of DataFrames containing the results data.
    Returns:
        int: The number of repetitions.
    """
    return len(results_data[0].columns)


def calculate_average(results_data: list[pd.DataFrame]) -> list:
    """
    Calculates the average of the results data.
    Args:
        results_data (list[DataFrame]): List of DataFrames containing the results data.
    Returns:
        list: A list of averages for each DataFrame.
    """
    return [d.mean(axis=1).tolist() for d in results_data]


def compile_individual_data(
    simulation_results: list[pd.DataFrame],
    metric: str,
    loads_filter: list = None,
) -> list[pd.DataFrame]:
    """
    Compiles the simulation results for the given metric and filters by load points if provided.
    Args:
        simulation_results (list[pd.DataFrame]): The list of simulations results to be compiled.
        metric (str): The specific metric to filter by.
        loads_filter (list, optional): List of load points to filter. Defaults to None.
    Returns:
        list: A list of DataFrames containing the compiled simulation results.
    """
    length = len(simulation_results)
    metric_results = ex.filter_result_list_by_metric(metric, simulation_results)

    if loads_filter is not None and len(loads_filter) > 0:
        loads_filter_set = set(str(l) for l in loads_filter)
        for i in range(len(metric_results)):
            metric_results[i] = metric_results[i][
                metric_results[i]["LoadPoint"].astype(str).isin(loads_filter_set)
            ]

    loads = ex.extract_load_points(metric_results)
    final_results = ex.extract_repetitions(metric_results)
    del metric_results

    number_of_reps = get_number_of_repetitions(final_results)
    average = calculate_average(final_results)
    error = calculate_standard_error(final_results, number_of_reps)
    del final_results

    dataframes = [pd.DataFrame() for _ in range(length)]

    for i in range(length):
        dataframes[i]["loads"] = loads
        dataframes[i]["mean"] = average[i]
        dataframes[i]["error"] = error[i]
    return dataframes


def compile_grouped_data(
    simulation_result: pd.DataFrame,
    metrics: list[str],
    loads_filter: list = None,
) -> list[pd.DataFrame]:
    """
    Compiles the simulation results for the given metrics and filters by load points if provided.
    This function is used when multiple metrics are grouped together.
    Args:
        simulation_result (pd.DataFrame): The simulation result to be compiled.
        metrics (list[str]): The list of metrics to filter by.
        loads_filter (list, optional): List of load points to filter. Defaults to None.
    Returns:
        list: A list of DataFrames containing the compiled simulation results.
    """
    length = len(metrics)
    metric_results = ex.filter_result_by_metric_list(metrics, simulation_result)

    if loads_filter is not None and len(loads_filter) > 0:
        loads_filter_set = set(str(l) for l in loads_filter)
        for i in range(len(metric_results)):
            metric_results[i] = metric_results[i][
                metric_results[i]["LoadPoint"].astype(str).isin(loads_filter_set)
            ]

    loads = ex.extract_load_points(metric_results)
    final_results = ex.extract_repetitions(metric_results)
    del metric_results

    number_of_reps = get_number_of_repetitions(final_results)
    average = calculate_average(final_results)
    error = calculate_standard_error(final_results, number_of_reps)
    del final_results

    dataframes = [pd.DataFrame() for _ in range(length)]

    for i in range(length):
        dataframes[i]["loads"] = loads
        dataframes[i]["mean"] = average[i]
        dataframes[i]["error"] = error[i]
    return dataframes


def export_results(
    dataframes: list[pd.DataFrame], labels: list[str], output_name: str, overwrite=True
) -> None:
    """
    Exports the compiled results to an Excel file with each DataFrame in a separate sheet.
    Args:
        dataframes (list[pd.DataFrame]): List of DataFrames containing the compiled results.
        labels (list[str]): List of labels for each DataFrame.
        base_directory (str): The base directory where the Excel file will be saved.
        output_name (str): The name of the output Excel file (without extension).
    """
    if not overwrite and op.exists(f"{output_name}.xlsx"):
        i = 0
        while True:
            if op.exists(f"{output_name}_{i}.xlsx"):
                i += 1
            else:
                with pd.ExcelWriter(f"{output_name}_{i}.xlsx") as writer:
                    for label, df in zip(labels, dataframes):
                        df.to_excel(writer, sheet_name=label, index=False)
                break
    else:
        with pd.ExcelWriter(f"{output_name}.xlsx") as writer:
            for label, df in zip(labels, dataframes):
                df.to_excel(writer, sheet_name=label, index=False)


def generate_graph(
    base_directory,
    directories,
    grouped_metrics: GroupedMetricT,
    labels=[],
    loads=[],
    chosen_loads=[],
    fontsize="large",
    figsize=(10, 5),
    overwrite=True,
    metric_type="individual",
    graph_type="line",
):
    if graph_type == "line":
        plot_graph = plot_line_graph

    elif graph_type == "bar":
        plot_graph = plot_bar_graph
    elif graph_type == "stacked-bar":
        plot_graph = plot_stacked_bar_graph
    filename_prefix = op.join(
        base_directory, f"{ex.get_basename(base_directory)}_{graph_type}"
    )
    x_label = "Carga na rede (Erlangs)"
    if not labels:
        labels = directories
    full_directories = [op.join(base_directory, d) for d in directories]
    if metric_type == "individual":
        for metric_group, metrics in grouped_metrics.items():
            csv_paths = ex.get_csv_paths_by_metric_group(full_directories, metric_group)
            simulation_results = ex.load_simulation_results(csv_paths)
            del csv_paths
            for metric in metrics:
                dataframes = compile_individual_data(
                    simulation_results,
                    metric,
                    loads_filter=chosen_loads,
                )
                if not loads:
                    loads = dataframes[0]["loads"].tolist()
                output_file = f"{filename_prefix}_{metric.replace(' ', '_')}"
                plot_graph(
                    dataframes,
                    loads,
                    labels,
                    x_label,
                    y_label=metric,
                    fontsize=fontsize,
                    figsize=figsize,
                    output_file=output_file,
                    overwrite=overwrite,
                )
    elif metric_type == "grouped":
        for metric_group, metrics in grouped_metrics.items():
            csv_paths = ex.get_csv_paths_by_metric_group(full_directories, metric_group)
            simulation_results = ex.load_simulation_results(csv_paths)
            del csv_paths
            for label, simulation_result in zip(labels, simulation_results):
                dataframes = compile_grouped_data(
                    simulation_result,
                    metrics,
                    loads_filter=chosen_loads,
                )
                if loads == []:
                    loads = dataframes[0]["loads"].tolist()
                output_file = f"{filename_prefix}_{metric_group}_{label}"
                plot_graph(
                    dataframes,
                    loads,
                    labels=get_metrics_components(metrics),
                    x_label=x_label,
                    y_label=metric_group,
                    fontsize=fontsize,
                    figsize=figsize,
                    output_file=output_file,
                    overwrite=overwrite,
                )


def get_metrics_components(metrics: list[str]) -> list[str]:
    """
    Extracts the components of the metrics from a list of metric strings.
    Args:
        metrics (list[str]): List of metric strings.
    Returns:
        list[str]: List of components extracted from the metric strings.
    """
    components = []
    for metric in metrics:
        components.append(metric.split("by", 1)[1].strip())
    return components


def plot_line_graph(
    dataframes,
    loads,
    labels,
    x_label,
    y_label,
    fontsize,
    figsize,
    output_file,
    legend_position="upper center",
    bbox_to_anchor=(0.5, -0.15),
    max_columns=5,
    overwrite=True,
    frameon=True,
):
    plt.figure(figsize=figsize)
    load_positions = list(range(len(loads)))
    for i in range(len(dataframes)):
        y = dataframes[i]["mean"]
        e = dataframes[i]["error"]
        plt.errorbar(
            load_positions,
            y,
            xerr=0,
            yerr=e,
            linestyle=linestyles[i % len(linestyles)],
            marker=markers[i % len(markers)],
            label=labels[i],
            fillstyle="none",
            ecolor="black",
        )
        plt.xticks(load_positions, loads)

    plt.xlabel(x_label, fontsize=fontsize)
    plt.ylabel(y_label, fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.grid(axis="y")
    if len(labels) < max_columns:
        max_columns = len(labels)

    plt.legend(
        loc=legend_position,
        bbox_to_anchor=bbox_to_anchor,
        ncol=max_columns,
        fontsize=fontsize,
        frameon=frameon,
    )
    if output_file != "":
        if not overwrite and op.exists(f"{output_file}.png"):
            i = 0
            while True:
                if op.exists(f"{output_file}_{i}.png"):
                    i += 1
                else:
                    plt.savefig(f"{output_file}_{i}.png", dpi=150, bbox_inches="tight")
                    break
        else:
            plt.savefig(f"{output_file}.png", dpi=150, bbox_inches="tight")
    plt.close()


def plot_bar_graph(
    dataframes,
    loads,
    labels,
    x_label,
    y_label,
    fontsize,
    figsize,
    output_file,
    legend_position="upper center",
    bbox_to_anchor=(0.5, -0.15),
    max_columns=5,
    overwrite=True,
    frameon=True,
):
    plt.figure(figsize=figsize)
    bar_width = 0.15

    load_positions = list(range(len(loads)))
    for i in range(len(dataframes)):
        y = dataframes[i]["mean"]
        e = dataframes[i]["error"]
        plt.bar(
            [p + i * bar_width for p in load_positions],
            y,
            width=bar_width,
            label=labels[i],
            yerr=e,
            capsize=5,
            hatch=hatches[i % len(hatches)],
            edgecolor="black",
        )
        plt.xticks(
            [p + (len(dataframes) - 1) * bar_width / 2 for p in load_positions], loads
        )

    plt.xlabel(x_label, fontsize=fontsize)
    plt.ylabel(y_label, fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.grid(axis="y")

    if len(labels) < max_columns:
        max_columns = len(labels)

    # Place the legend below the y-axis label
    plt.legend(
        loc=legend_position,
        bbox_to_anchor=bbox_to_anchor,
        ncol=max_columns,
        fontsize=fontsize,
        frameon=frameon,
    )

    if output_file != "":
        if not overwrite and op.exists(f"{output_file}.png"):
            i = 0
            while True:
                if op.exists(f"{output_file}_{i}.png"):
                    i += 1
                else:
                    plt.savefig(f"{output_file}_{i}.png", dpi=150, bbox_inches="tight")
                    break
        else:
            plt.savefig(f"{output_file}.png", dpi=150, bbox_inches="tight")

    plt.close()


def plot_stacked_bar_graph(
    dataframes,
    loads,
    labels,
    x_label,
    y_label,
    fontsize,
    figsize,
    output_file,
    legend_position="upper center",
    bbox_to_anchor=(0.5, -0.15),
    max_columns=5,
    overwrite=True,
    frameon=True,
):
    plt.figure(figsize=figsize)
    bar_width = 0.15

    load_positions = list(range(len(loads)))
    bottom = [0] * len(loads)

    for i in range(len(dataframes)):
        y = dataframes[i]["mean"]
        e = dataframes[i]["error"]
        plt.bar(
            load_positions,
            y,
            width=bar_width,
            label=labels[i],
            yerr=e,
            capsize=5,
            hatch=hatches[i % len(hatches)],
            edgecolor="black",
            bottom=bottom,
        )
        bottom = [b + y_val for b, y_val in zip(bottom, y)]
        plt.xticks(load_positions, loads)

    plt.xlabel(x_label, fontsize=fontsize)
    plt.ylabel(y_label, fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.grid(axis="y")

    if len(labels) < max_columns:
        max_columns = len(labels)

    # Place the legend below the y-axis label
    plt.legend(
        loc=legend_position,
        bbox_to_anchor=bbox_to_anchor,
        ncol=max_columns,
        fontsize=fontsize,
        frameon=frameon,
    )

    if output_file != "":
        if not overwrite and op.exists(f"{output_file}.png"):
            i = 0
            while True:
                if op.exists(f"{output_file}_{i}.png"):
                    i += 1
                else:
                    plt.savefig(f"{output_file}_{i}.png", dpi=150, bbox_inches="tight")
                    break
        else:
            plt.savefig(f"{output_file}.png", dpi=150, bbox_inches="tight")

    plt.close()


def main():
    base_directory = "TesteGraficoPython/simulations"
    directories = [
        "GreedReoptimization_CircuitBlocked_XT_XTO_001",
        "GreedReoptimization_CircuitFinalized_001",
        "NoReallocation",
    ]
    grouped_metrics = {
        "BitRateBlockingProbability": [
            "BitRate blocking probability",
        ],
        "BlockingProbability": [
            "Blocking probability",
        ],
    }

    # ? Temporary solution for getting labels

    labels = ex.get_labels(directories)

    # plot_line_graph(
    #     base_directory, directories, grouped_metrics, labels=labels, overwrite=True
    # )
    export_results(
        compile_individual_data(
            base_directory,
            directories,
            "BitRateBlockingProbability",
            "BitRate blocking probability",
        ),
        labels,
        base_directory,
        "BitRate blocking probability",
    )


if __name__ == "__main__":
    main()
