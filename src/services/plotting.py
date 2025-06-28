import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from services import path_utils as pus


matplotlib.use("agg")


class GraphPlotter:
    """
    Class to plot graphs based on provided data.
    This class provides methods to plot line, bar, and stacked bar graphs
    with error bars representing the uncertainty in the data.
    """

    MARKERS = ["o", "v", "^", "s", "P", "x", "D", "_", "*", "2"]
    LINESTYLES = ["-", "--", "-.", ":", "-", "--", "-.", ":", "-", "--"]
    HATCHES = ["", "/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]

    def __init__(self, graph_config: dict):
        """
        Initialize the GraphPlotter with the provided graph configuration.
        Args:
            graph_config (dict): Configuration dictionary for the graph.
        """
        self.PLOTTING_STRATEGIES = {
            "linear": self.plot_line_graph,
            "log": self.plot_line_graph,
            "bar": self.plot_bar_graph,
            "stacked": self.plot_stacked_bar_graph,
        }
        self.ylim_low = graph_config.get("ylim_low", "")
        self.ylim_up = graph_config.get("ylim_up", "")
        self.x_axis_direction = graph_config.get("x_axis_direction", "horizontal")
        self.title = graph_config.get("title", "")
        self.x_label = graph_config.get("xlabel", "")
        self.y_label = graph_config.get("ylabel", "")
        self.graph_type: str = graph_config.get("graph_type", "linear")
        self.figsize = graph_config.get("figsize", (10, 5))
        self.graph_fontsize = graph_config.get("graph_fontsize", "medium")
        self.legend_fontsize = graph_config.get("legend_fontsize", "medium")
        self.legend_position = graph_config.get("legend_position", "upper center")
        self.bbox_to_anchor = graph_config.get("bbox_to_anchor", (0.5, -0.15))
        self.max_columns = graph_config.get("max_columns", 5)
        self.frameon = graph_config.get("frameon", False)
        self.overwrite = graph_config.get("overwrite", False)
        self.use_grid = graph_config.get("use_grid", False)

    def initialize_graphs_data(
        self,
        loads: list[str],
        labels: list[str],
        x_label: str = "",
        y_label: str = "",
    ):
        """
        Initialize the data required for plotting graphs.
        Args:
            loads (list[str]): List of loads for the x-axis.
            labels (list[str]): List of labels for the graph legend.
            x_label (str, optional): Label for the x-axis. Defaults to "".
            y_label (str, optional): Label for the y-axis. Defaults to "".
        """
        self.loads = loads
        self.load_positions = list(range(len(loads)))
        self.labels = labels
        self.labels_len = len(labels)
        self.set_colors()
        if self.x_label == "":
            self.x_label = x_label
        if self.y_label == "":
            self.y_label = y_label

    def set_colors(self):
        if self.labels_len <= 0:
            raise ValueError("Size must be a positive integer.")
        if self.labels_len <= 10:
            cmap = plt.get_cmap("tab10")
        else:
            cmap = plt.get_cmap("tab20")
        self.colors = [cmap(i) for i in range(cmap.N)]
        self.colors_len = len(self.colors)

    def plot_graph(
        self,
        dataframes: list[pd.DataFrame],
        output_file: str,
        x_label: str | None = None,
        y_label: str | None = None,
    ):
        """
        Plot a graph based on the provided parameters.
        Args:
            dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
            loads (list[str]): List of loads for the x-axis.
            labels (list[str]): List of labels for the graph legend.
            x_label (str, optional): Label for the x-axis. Defaults to value set in `initialize_graphs_data`.
            y_label (str, optional): Label for the y-axis. Defaults to value set in `initialize_graphs_data`.
            output_file (str): Path to save the output file (without extension).
        """
        plt.figure(figsize=self.figsize)

        if self.title:
            plt.title(self.title, fontsize=self.graph_fontsize, fontweight="bold")

        if self.graph_type in ("linear", "log"):
            plt.yscale(self.graph_type)
        plot_function = self.PLOTTING_STRATEGIES.get(self.graph_type)
        if plot_function is not None:
            plot_function(dataframes)
        else:
            raise ValueError(f"Graph type not supported: {self.graph_type}")
        if self.ylim_low != "":
            plt.ylim(bottom=float(self.ylim_low))
        if self.ylim_up != "":
            plt.ylim(top=float(self.ylim_up))
        if x_label is None or self.x_label != "":
            x_label = self.x_label
        if y_label is None or self.y_label != "":
            y_label = self.y_label
        plt.xlabel(x_label, fontsize=self.graph_fontsize, fontweight="bold")
        plt.ylabel(y_label, fontsize=self.graph_fontsize, fontweight="bold")
        if self.use_grid:
            plt.grid(axis="y")
        if self.labels_len < self.max_columns:
            self.max_columns = self.labels_len
        if self.x_axis_direction == "vertical":
            plt.xticks(rotation=90)

        if self.legend_position == "none":
            plt.legend().set_visible(False)
        else:
            plt.legend(
                loc=self.legend_position,
                bbox_to_anchor=self.bbox_to_anchor,
                ncol=self.max_columns,
                fontsize=self.legend_fontsize,
                frameon=self.frameon,
            )
        if output_file != "":
            output_file = pus.ensure_unique_filename(output_file, "png", self.overwrite)
            plt.savefig(f"{output_file}.png", dpi=150, bbox_inches="tight")
        plt.close()

    def plot_line_graph(self, dataframes: list[pd.DataFrame]):
        """
        Plot a line graph with error bars.\\
        This function generates a line graph for the provided dataframes,
        loads, and labels, with error bars representing the uncertainty in the data.
        Args:
            dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        """
        capsize = 3
        idx_shift = 0
        idx_count = 0
        for i in range(len(dataframes)):
            if idx_count == self.colors_len:
                idx_count = 0
                idx_shift += 1
            style_idx = (i + idx_shift) % len(self.LINESTYLES)
            idx_count += 1
            mean = dataframes[i]["mean"]
            error = dataframes[i]["error"]
            if self.graph_type == "linear" and sum(mean == 0) >= 2:
                mean_len = len(mean)
                for idx in range(mean_len):
                    if mean[idx] == 0 and idx < mean_len - 1 and mean[idx + 1] == 0:
                        continue
                    if error[idx] > 0:
                        plt.errorbar(
                            [self.load_positions[idx]],
                            [mean[idx]],
                            yerr=[error[idx]],
                            capsize=capsize,
                            linestyle="none",
                            color=self.get_color(i),
                            elinewidth=1,
                            ecolor="black",
                            zorder=2,
                        )
                    plt.scatter(
                        self.load_positions[idx],
                        mean[idx],
                        marker=self.MARKERS[style_idx],
                        color=self.get_color(i),
                        facecolors="none",
                        zorder=1,
                    )
            else:
                if any(error > 0):
                    plt.errorbar(
                        self.load_positions,
                        mean,
                        yerr=error,
                        capsize=capsize,
                        linestyle="none",
                        color=self.get_color(i),
                        elinewidth=1,
                        ecolor="black",
                        zorder=2,
                    )
                plt.scatter(
                    self.load_positions,
                    mean,
                    marker=self.MARKERS[style_idx],
                    color=self.get_color(i),
                    facecolors="none",
                    zorder=1,
                )
            plt.plot(
                self.load_positions,
                mean,
                linestyle=self.LINESTYLES[style_idx],
                color=self.get_color(i),
                zorder=1,
            )
            plt.plot(
                [],
                [],
                linestyle=self.LINESTYLES[style_idx],
                marker=self.MARKERS[style_idx],
                color=self.get_color(i),
                markerfacecolor="none",
                label=self.labels[i],
            )
        plt.xticks(self.load_positions, self.loads, fontsize=self.graph_fontsize)
        plt.yticks(fontsize=self.graph_fontsize)

    def plot_bar_graph(self, dataframes: list[pd.DataFrame]):
        """
        Plot a bar graph with error bars.\\
        This function generates a bar graph for the provided dataframes,
        loads, and labels, with error bars representing the uncertainty in the data.
        Args:
            dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        """
        bar_width = 0.15
        idx_shift = 0
        idx_count = 0
        for i in range(len(dataframes)):
            if idx_count == self.colors_len:
                idx_count = 0
                idx_shift += 1
            style_idx = (i + idx_shift) % len(self.HATCHES)
            idx_count += 1
            mean = dataframes[i]["mean"]
            error = dataframes[i]["error"]
            plt.bar(
                [p + i * bar_width for p in self.load_positions],
                mean,
                width=bar_width,
                label=self.labels[i],
                yerr=error,
                capsize=5,
                hatch=self.HATCHES[style_idx],
                color=self.get_color(i),
                edgecolor="black",
                ecolor="black",
            )
        plt.xticks(
            [p + (len(dataframes) - 1) * bar_width / 2 for p in self.load_positions],
            self.loads,
            fontsize=self.graph_fontsize,
        )
        plt.yticks(fontsize=self.graph_fontsize)
        plt.ylim(bottom=0)

    def plot_stacked_bar_graph(self, dataframes: list[pd.DataFrame]):
        """
        Plot a stacked bar graph with error bars.\\
        This function generates a stacked bar graph for the provided dataframes,
        loads, and labels, with error bars representing the uncertainty in the data.
        Args:
            dataframes (list[pd.DataFrame]): List of DataFrames containing the data to plot.
        """
        bar_width = 0.15
        bottom = [0] * len(self.loads)
        idx_shift = 0
        idx_count = 0
        for i in range(len(dataframes)):
            if idx_count == self.colors_len:
                idx_count = 0
                idx_shift += 1
            style_idx = (i + idx_shift) % len(self.HATCHES)
            idx_count += 1
            y = dataframes[i]["mean"]
            e = dataframes[i]["error"]
            plt.bar(
                self.load_positions,
                y,
                width=bar_width,
                label=self.labels[i],
                yerr=e,
                capsize=5,
                hatch=self.HATCHES[style_idx],
                color=self.get_color(i),
                edgecolor="black",
                bottom=bottom,
                ecolor="black",
            )
            bottom = [b + y_val for b, y_val in zip(bottom, y)]
        plt.xticks(self.load_positions, self.loads, fontsize=self.graph_fontsize)
        plt.yticks(fontsize=self.graph_fontsize)
        plt.ylim(bottom=0)

    def get_color(self, idx: int) -> tuple[float, float, float, float]:
        return self.colors[idx % self.colors_len]
