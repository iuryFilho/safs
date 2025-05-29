import os
from flask import (
    Blueprint,
    request,
    jsonify,
    session,
)
import extraction as ex
import graphs as gr
from utils import Logger

blueprint = Blueprint("graphs", __name__)
LOG = True


@blueprint.record
def record_params(setup_state):
    global logger
    logger = Logger(log=(LOG and setup_state.options.get("debug_output", True)))


@blueprint.route("/generate-graphs", methods=["POST"])
def generate_graphs():
    base_directory = session.get("base_directory", "")
    grouped_metrics = session.get("grouped_metrics", None)
    directories = request.form.getlist("directory-list")
    raw_labels = request.form.getlist("directory-labels")
    labels = []
    session_labels = {}
    for dir, label in zip(directories, raw_labels):
        if label:
            labels.append(label)
            session_labels[dir] = label
        else:
            labels.append(ex.get_default_label(dir))
    chosen_metrics = request.form.getlist("metric-list")

    graph_type = request.form.get("graph-type", "line")
    graph_composition = request.form.get("graph-composition", "individual")
    overwrite = request.form.get("overwrite", "") == "true"
    figsize = (
        request.form.get("figure-width", "10"),
        request.form.get("figure-height", "5"),
    )
    font_size = request.form.get("font-size", "medium")

    session["graph_type"] = graph_type
    session["graph_composition"] = graph_composition
    session["overwrite"] = overwrite
    session["figure_width"] = figsize[0]
    session["figure_height"] = figsize[1]
    session["font_size"] = font_size

    if grouped_metrics:
        chosen_grouped_metrics = group_selected_metrics(grouped_metrics, chosen_metrics)
        try:
            # TODO implement graph composition logic
            if graph_type == "line":
                gr.plot_line_graph(
                    base_directory,
                    directories,
                    chosen_grouped_metrics,
                    labels=labels,
                    fontsize=font_size,
                    figsize=to_float(*figsize),
                    overwrite=overwrite,
                )
            elif graph_type == "bar":
                # TODO implement bar graph plotting
                return jsonify({"error": "Bar graph plotting not implemented yet."})
            else:
                return jsonify({"error": "Unsupported graph type."})
            return jsonify({"message": "Graphs generated successfully."})
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        return jsonify({"error": "No metrics selected."})


@blueprint.route("/export-results", methods=["POST"])
def export_results():
    base_directory = session.get("base_directory", "")
    grouped_metrics = session.get("grouped_metrics", None)

    if not grouped_metrics:
        return jsonify({"error": "No metrics selected."})

    directories = request.form.getlist("directory-list")
    chosen_metrics = request.form.getlist("metric-list")
    chosen_grouped_metrics = group_selected_metrics(grouped_metrics, chosen_metrics)

    filename_prefix = ex.normalize_path(base_directory).split("/")[-1]
    logger.log(f"Filename prefix: {filename_prefix}")
    try:
        for metric_group, metrics in chosen_grouped_metrics.items():
            for metric in metrics:
                results = gr.compile_simulation_results(
                    base_directory,
                    directories,
                    metric_group,
                    metric,
                )
                filename = f"{filename_prefix}_{metric.replace(' ', '_')}"
                logger.log(f"Exporting results for {metric} to {filename}")

                gr.export_results(
                    results,
                    ex.get_labels(directories),
                    base_directory,
                    filename,
                )
        return jsonify({"message": "Results exported successfully."})
    except Exception as e:
        return jsonify({"error": str(e)})


def group_selected_metrics(grouped_metrics, chosen_metrics):
    chosen_grouped_metrics = {}
    for metric_group, metric_list in grouped_metrics.items():
        for metric in chosen_metrics:
            if metric in metric_list:
                chosen_grouped_metrics[metric_group] = chosen_grouped_metrics.get(
                    metric_group, []
                ) + [metric]

    return chosen_grouped_metrics


def to_float(*values: str) -> list[float]:
    """
    Converts a string or list of strings to a list of floats.
    Args:
        *values (str): A variable number of string values to be converted to floats.
    Returns:
        list[float]: The converted values.
    """
    float_values = []
    for value in values:
        if value.find(",") != -1:
            float_values.append(float(value.replace(",", ".")))
        else:
            float_values.append(float(value))
    return float_values
