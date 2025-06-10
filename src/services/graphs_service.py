import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import os.path as op
from typing import TypeAlias

from services import (
    utils_service as us,
    metrics_service as ms,
    path_service as ps,
    simulation_service as ss,
)


GroupedMetricT: TypeAlias = dict[str, list[str]]

matplotlib.use("agg")

LOG_ENABLE = True
log = us.Logger(LOG_ENABLE, __name__).debug

markers = ["o", "v", "^", "s", "P", "x", "D", "_", "*", "2"]
linestyles = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-", "--"]
hatches = ["", "/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]


def generate_graphs(
    base_directory: str,
    directories: list[str],
    grouped_metrics: GroupedMetricT,
    labels: list[str] = [],
    loads: list[str] = [],
    chosen_loads: list[str] = [],
    fontsize: str = "large",
    figsize: tuple[int, int] = (10, 5),
    overwrite: bool = True,
    metric_type: str = "individual",
    graph_type: str = "line",
):
    if metric_type == "individual":
        generate_graphs_func = generate_individual_graphs
    elif metric_type == "grouped":
        generate_graphs_func = generate_grouped_graphs
    filename_prefix = op.join(
        base_directory, f"{ps.get_basename(base_directory)}_{graph_type}"
    )
    x_label = "Carga na rede (Erlangs)"
    if not labels:
        labels = directories
    full_directories = [op.join(base_directory, d) for d in directories]
    for metric_group, metrics in grouped_metrics.items():
        simulation_results = ss.load_simulation_results(full_directories, metric_group)
        generate_graphs_func(
            metrics,
            simulation_results,
            labels,
            chosen_loads,
            loads,
            fontsize,
            figsize,
            overwrite,
            graph_type,
            filename_prefix,
            x_label,
        )


def generate_individual_graphs(
    metrics: list[str],
    simulation_results: list[pd.DataFrame],
    labels: list[str],
    chosen_loads: list[str],
    loads: list[str],
    fontsize: str = "large",
    figsize: tuple[int, int] = (10, 5),
    overwrite: bool = True,
    graph_type: str = "line",
    filename_prefix: str = "",
    x_label: str = "",
):
    for metric in metrics:
        dataframes = ss.compile_individual_data(
            simulation_results,
            metric,
            loads_filter=chosen_loads,
        )
        if not loads:
            loads = dataframes[0]["loads"].tolist()
        output_file = f"{filename_prefix}_{metric.replace(' ', '_')}"
        plot_graph(
            graph_type=graph_type,
            dataframes=dataframes,
            loads=loads,
            labels=labels,
            x_label=x_label,
            y_label=metric,
            fontsize=fontsize,
            figsize=figsize,
            output_file=output_file,
            overwrite=overwrite,
        )


def generate_grouped_graphs(
    labels: list[str] = [],
    loads: list[str] = [],
    chosen_loads: list[str] = [],
    fontsize: str = "large",
    figsize: tuple[int, int] = (10, 5),
    overwrite: bool = True,
    graph_type: str = "line",
    filename_prefix: str = "",
    x_label: str = "",
    metric_group: str = "",
    metrics: list[str] = [],
    simulation_results: list[pd.DataFrame] = [],
):
    for label, simulation_result in zip(labels, simulation_results):
        dataframes = ss.compile_grouped_data(
            simulation_result,
            metrics,
            loads_filter=chosen_loads,
        )
        if not loads:
            loads = dataframes[0]["loads"].tolist()
        output_file = f"{filename_prefix}_{metric_group}_{label}"
        plot_graph(
            graph_type=graph_type,
            dataframes=dataframes,
            loads=loads,
            labels=ms.get_metrics_components(metrics),
            x_label=x_label,
            y_label=metric_group,
            fontsize=fontsize,
            figsize=figsize,
            output_file=output_file,
            overwrite=overwrite,
        )


def plot_graph(
    graph_type: str,
    dataframes: list[pd.DataFrame],
    loads: list[str],
    labels: list[str],
    x_label: str,
    y_label: str,
    fontsize: str,
    figsize: tuple[int, int],
    output_file: str,
    overwrite: bool,
    legend_position: str = "upper center",
    bbox_to_anchor: tuple[float, float] = (0.5, -0.15),
    max_columns: int = 5,
    frameon: bool = True,
):
    plt.figure(figsize=figsize)

    if graph_type == "line":
        plot_line_graph(dataframes, loads, labels)
    elif graph_type == "bar":
        plot_bar_graph(dataframes, loads, labels)
    elif graph_type == "stacked-bar":
        plot_stacked_bar_graph(dataframes, loads, labels)

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


def plot_line_graph(
    dataframes,
    loads,
    labels,
):
    load_positions = list(range(len(loads)))
    for i in range(len(dataframes)):
        y = dataframes[i]["mean"]
        e = dataframes[i]["error"]
        color = plt.cm.tab10(i % 10)
        plt.plot(
            load_positions,
            y,
            linestyle=linestyles[i % len(linestyles)],
            marker=markers[i % len(markers)],
            label=labels[i],
            fillstyle="none",
            color=color,
            zorder=1,
        )
        plt.errorbar(
            load_positions,
            y,
            xerr=0,
            yerr=e,
            linestyle="none",
            marker=None,
            label=None,
            ecolor="black",
            color=color,
            zorder=2,
        )
        plt.xticks(load_positions, loads)


def plot_bar_graph(
    dataframes,
    loads,
    labels,
):
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


def plot_stacked_bar_graph(
    dataframes,
    loads,
    labels,
):
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


def main():
    return


if __name__ == "__main__":
    main()
