import os
import threading
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
)
import extraction as ex
import graphs as gr
from routes.utils import Logger

blueprint = Blueprint("graphs", __name__)
debug_output = True
logger = Logger(log=False)


@blueprint.record
def record_params(setup_state):
    global debug_output
    debug_output = setup_state.options.get("debug_output", True)


@blueprint.route("/generate-graphs", methods=["POST"])
def generate_graphs():
    base_directory = session.get("base_directory", "")
    grouped_metrics = session.get("grouped_metrics", None)

    graph_type = request.form.get("graph-type", "line")
    graph_composition = request.form.get("graph-composition", "individual")
    overwrite = request.form.get("overwrite", "false") == "true"

    directories = request.form.getlist("directory-list")
    chosen_metrics = request.form.getlist("metric-list")
    chosen_grouped_metrics = {}
    logger.log(f"Graph type: {graph_type}")
    logger.log(f"Graph composition: {graph_composition}")
    logger.log(f"Overwrite images: {overwrite}")

    if grouped_metrics:
        chosen_grouped_metrics = group_selected_metrics(grouped_metrics, chosen_metrics)
        try:
            # TODO implement graph composition logic
            if graph_type == "line":
                gr.plot_line_graph(
                    base_directory,
                    directories,
                    chosen_grouped_metrics,
                    labels=ex.get_labels(directories),
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
    try:
        for metric_group, metrics in chosen_grouped_metrics.items():
            for metric in metrics:
                gr.export_results(
                    gr.compile_simulation_results(
                        base_directory,
                        directories,
                        metric_group,
                        metric,
                    ),
                    ex.get_labels(directories),
                    base_directory,
                    f"{os.path.join(base_directory, filename_prefix)}_{metric}",
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
