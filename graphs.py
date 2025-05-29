import extraction as ex
import matplotlib
import matplotlib.pyplot as plt
import scipy.stats as st
import pandas as pd
import os
import json
from utils import to_json, Logger

matplotlib.use("agg")

LOG = True
logger = Logger(log=LOG)

markers = ["o", "v", "^", "s", "P", "x", "D", "_", "*", "2"]
linestyles = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-", "--"]
bbox_to_anchor = (0.5, 0)


# * Auxiliary functions
def to_json(obj):
    return json.dumps(obj, indent=4)


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


def compile_simulation_results(
    base_directory: str,
    directories: list[str],
    metric_group: str,
    metric: str,
) -> list[pd.DataFrame]:
    """
    Compiles the simulation results for the given metric.
    Args:
        base_directory (str): The base directory of the simulations.
        directories (list[str]): The list of simulation directories.
        metric_group (str): The metric group to filter by.
        metric (str): The specific metric to filter by.
    Returns:
        list: A list of DataFrames containing the compiled simulation results.
    """
    length = len(directories)
    full_directories = [os.path.join(base_directory, d) for d in directories]
    csv_paths = ex.get_csv_paths_by_metric(full_directories, metric_group)
    logger.log(f"CSV paths: {to_json(csv_paths)}")
    simulation_results = ex.load_simulation_results(csv_paths)
    del csv_paths

    metric_results = ex.filter_metric(metric, simulation_results)
    del simulation_results

    loads = ex.extract_load_points(metric_results)
    final_results = ex.extract_repetitions(metric_results)
    del metric_results

    number_of_reps = get_number_of_repetitions(final_results)
    average = calculate_average(final_results)
    error = calculate_standard_error(final_results, number_of_reps)
    del final_results

    dataframes = [pd.DataFrame() for i in range(length)]

    for i in range(length):
        dataframes[i]["loads"] = loads
        dataframes[i]["mean"] = average[i]
        dataframes[i]["error"] = error[i]
    return dataframes


def export_results(
    dataframes: list[pd.DataFrame],
    labels: list[str],
    base_directory: str,
    output_name: str,
) -> None:
    """
    Exports the compiled results to an Excel file with each DataFrame in a separate sheet.
    Args:
        dataframes (list[pd.DataFrame]): List of DataFrames containing the compiled results.
        labels (list[str]): List of labels for each DataFrame.
        base_directory (str): The base directory where the Excel file will be saved.
        output_name (str): The name of the output Excel file (without extension).
    """
    with pd.ExcelWriter(f"{os.path.join(base_directory, output_name)}.xlsx") as writer:
        for label, df in zip(labels, dataframes):
            df.to_excel(writer, sheet_name=label, index=False)


def plot_line_graph(
    base_directory,
    directories,
    grouped_metrics,
    labels=[],
    loads=[],
    fontsize="large",
    figsize=(10, 5),
    overwrite=True,
):
    filename_prefix = ex.normalize_path(base_directory).split("/")[-1] + "_Line_"
    x_label = "Carga na rede (Erlangs)"
    if not labels:
        labels = directories
    for metric_group, metrics in grouped_metrics.items():
        for metric in metrics:
            dataframes = compile_simulation_results(
                base_directory,
                directories,
                metric_group,
                metric,
            )
            if loads == []:
                loads = dataframes[0]["loads"].tolist()
            output_file = f"{os.path.join(base_directory, filename_prefix)}{metric.replace(' ', '_')}"
            aux_plot_line(
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


def aux_plot_line(
    dataframes,
    loads,
    labels,
    x_label,
    y_label,
    fontsize,
    figsize,
    output_file,
    legend_position="lower center",
    max_columns=5,
    overwrite=True,
):
    plt.figure(figsize=figsize)
    for i in range(len(dataframes)):
        x = dataframes[i]["loads"]
        y = dataframes[i]["mean"]
        e = dataframes[i]["error"]
        plt.errorbar(
            x,
            y,
            xerr=0,
            yerr=e,
            linestyle=linestyles[i],
            marker=markers[i],
            label=labels[i],
            fillstyle="none",
        )
        plt.xticks(x, loads)

    plt.xlabel(x_label, fontsize=fontsize)
    plt.ylabel(y_label, fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.grid(axis="y")
    if len(labels) < max_columns:
        max_columns = len(labels)

    plt.legend(
        loc=legend_position,
        ncol=max_columns,
        fontsize=fontsize,
        bbox_to_anchor=bbox_to_anchor,
    )
    if output_file != "":
        logger.log(f"Saving graph to {output_file}.png")
        if not overwrite and os.path.exists(f"{output_file}.png"):
            i = 0
            while True:
                if os.path.exists(f"{output_file}_{i}.png"):
                    i += 1
                else:
                    plt.savefig(f"{output_file}_{i}.png", dpi=150, bbox_inches="tight")
                    break
        else:
            plt.savefig(f"{output_file}.png", dpi=150, bbox_inches="tight")
    plt.close()


def plot_bar_graph(
    base_directory,
    directories,
    grouped_metrics,
    labels=[],
    loads=[],
    fontsize="large",
    figsize=(10, 5),
    overwrite=True,
):
    filename_prefix = ex.normalize_path(base_directory).split("/")[-1] + "_Bar_"
    x_label = "Carga na rede (Erlangs)"
    if not labels:
        labels = directories
    for metric_group, metrics in grouped_metrics.items():
        for metric in metrics:
            dataframes = compile_simulation_results(
                base_directory,
                directories,
                metric_group,
                metric,
            )
            if loads == []:
                loads = dataframes[0]["loads"].tolist()
            output_file = f"{os.path.join(base_directory, filename_prefix)}{metric.replace(' ', '_')}"
            aux_plot_bar(
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


def aux_plot_bar(
    dataframes,
    loads,
    labels,
    x_label,
    y_label,
    fontsize,
    figsize,
    output_file,
    legend_position="best",
    max_columns=5,
    overwrite=True,
):
    plt.figure(figsize=figsize)
    bar_width = 0.15

    for i in range(len(dataframes)):
        x = dataframes[i]["loads"]
        y = dataframes[i]["mean"]
        e = dataframes[i]["error"]
        plt.bar(
            [p + i * bar_width for p in x],
            y,
            width=bar_width,
            label=labels[i],
            yerr=e,
            capsize=5,
        )
        plt.xticks([p + (len(dataframes) - 1) * bar_width / 2 for p in x], loads)

    plt.xlabel(x_label, fontsize=fontsize)
    plt.ylabel(y_label, fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.grid(axis="y")

    if len(labels) < max_columns:
        max_columns = len(labels)

    plt.legend(
        loc=legend_position,
        ncol=max_columns,
        fontsize=fontsize,
        # bbox_to_anchor=bbox_to_anchor,
    )

    if output_file != "":
        logger.log(f"Saving graph to {output_file}.png")
        if not overwrite and os.path.exists(f"{output_file}.png"):
            i = 0
            while True:
                if os.path.exists(f"{output_file}_{i}.png"):
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
        compile_simulation_results(
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
