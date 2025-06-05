import os.path as op
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
LOG_ENABLE = True
logger = Logger(LOG_ENABLE, __name__)


@blueprint.route("/generate-graphs", methods=["POST"])
def generate_graphs():
    base_directory = session.get("base_directory", "")
    metric_type = session.get("metric_type", "individual")
    grouped_metrics = session.get("grouped_metrics", None)

    data: dict = request.get_json()
    directories = data.get("directory-list", [])
    raw_labels = data.get("directory-labels", [])
    labels = []
    session_labels = {}
    for dir, label in zip(directories, raw_labels):
        if label:
            labels.append(label)
            session_labels[dir] = label
        else:
            labels.append(dir)
    chosen_metrics = data.get("metric-list", [])

    graph_type = data.get("graph-type", "line")
    graph_composition = data.get("graph-composition", "individual")
    overwrite = data.get("overwrite", "") == "true"
    figsize = (
        data.get("figure-width", "10"),
        data.get("figure-height", "5"),
    )
    font_size = data.get("font-size", "medium")
    loads: dict = data.get("loads", {})

    session["labels"] = session_labels
    session["graph_type"] = graph_type
    session["graph_composition"] = graph_composition
    session["overwrite"] = overwrite
    session["figure_width"] = figsize[0]
    session["figure_height"] = figsize[1]
    session["font_size"] = font_size
    session["loads"] = loads

    # return jsonify({"message": "Graph generation started."})
    if grouped_metrics:
        chosen_grouped_metrics = group_selected_metrics(grouped_metrics, chosen_metrics)
        try:
            gr.generate_graph(
                base_directory,
                directories,
                chosen_grouped_metrics,
                labels=labels,
                loads=loads.values(),
                chosen_loads=loads.keys(),
                fontsize=font_size,
                figsize=to_float(*figsize),
                overwrite=overwrite,
                metric_type=metric_type,
                graph_type=graph_type,
            )
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
    raw_labels = request.form.getlist("directory-labels")
    labels = []
    session_labels = {}
    for dir, label in zip(directories, raw_labels):
        if label:
            labels.append(label)
            session_labels[dir] = label
        else:
            labels.append(dir)

    chosen_metrics = request.form.getlist("metric-list")
    chosen_grouped_metrics = group_selected_metrics(grouped_metrics, chosen_metrics)

    overwrite = request.form.get("overwrite", "") == "true"
    filename_prefix = op.join(base_directory, ex.get_basename(base_directory))
    logger.log(f"Filename prefix: {filename_prefix}")
    try:
        full_directories = [op.join(base_directory, d) for d in directories]
        for metric_group, metrics in chosen_grouped_metrics.items():
            csv_paths = ex.get_csv_paths_by_metric_group(full_directories, metric_group)
            simulation_results = ex.load_simulation_results(csv_paths)
            for metric in metrics:
                results = gr.compile_data_from_result_list(
                    simulation_results,
                    metric,
                )
                filename = f"{filename_prefix}_{metric.replace(' ', '_')}"
                logger.log(f"Exporting results for {metric} to {filename}")

                gr.export_results(results, labels, filename, overwrite)
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
