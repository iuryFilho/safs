import extraction as ex
import matplotlib.pyplot as plt
import scipy.stats as st
import pandas as pd
import os
import logging
import json

markers = ["o", "v", "^", "s", "P", "x", "D", "_", "*", "2"]
linestyles = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-", "--"]


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
    logging.info(f"CSV paths: {to_json(csv_paths)}")
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


def plot_line_graph(
    base_directory, directories, grouped_metrics, labels=[], loads=[], show=True
):
    filename_prefix = base_directory.split("/")[-1] + "_Line_"
    x_label = "Carga na rede (Erlangs)"
    if not labels:
        labels = directories
    for metric_group, metrics in grouped_metrics.items():
        for metric in metrics:
            logging.info(f"Plotting {metric_group} - {metric}")
            dataframes = compile_simulation_results(
                base_directory,
                directories,
                metric_group,
                metric,
            )
            if loads == []:
                loads = dataframes[0]["loads"].tolist()
            output_file = (
                f"{base_directory}/{filename_prefix}{metric.replace(' ', '_')}"
            )
            aux_plot_line(
                dataframes,
                loads,
                labels,
                x_label,
                y_label=metric,
                output_file=output_file,
                show=show,
            )


def aux_plot_line(
    dataframes,
    loads,
    labels,
    x_label,
    y_label,
    output_file,
    show=True,
    legend_position="lower center",
    num_columns=5,
):
    font_size = 27
    plt.figure(figsize=(10, 7))
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
        )
        plt.xticks(x, loads)

    plt.xlabel(x_label, fontsize=font_size)
    plt.ylabel(y_label, fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    plt.grid(axis="y")
    if len(labels) < num_columns:
        num_columns = len(labels)

    plt.legend(
        loc=legend_position,
        ncol=num_columns,
        fontsize=font_size,
        bbox_to_anchor=(0.5, -0.43),
    )
    if output_file != "":
        if os.path.exists(f"{output_file}.png"):
            i = 0
            while True:
                if os.path.exists(f"{output_file}_{i}.png"):
                    i += 1
                else:
                    plt.savefig(f"{output_file}_{i}.png", dpi=150, bbox_inches="tight")
                    break
        else:
            plt.savefig(f"{output_file}.png", dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close()


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
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
    def get_labels():
        labels = []
        for dir in directories:
            dir = "".join([c for c in dir if c.isupper() or c.isnumeric()])
            logging.info(f"Directory: {dir}")
            labels.append(dir)
        return labels

    labels = get_labels()

    plot_line_graph(
        base_directory, directories, grouped_metrics, labels=labels, show=False
    )


if __name__ == "__main__":
    main()
