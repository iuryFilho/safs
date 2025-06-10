import os.path as op
from flask import (
    Blueprint,
    request,
    jsonify,
    session,
)

from services import (
    generation_service as gs,
    metrics_service as ms,
    path_service as ps,
    simulation_service as ss,
    utils_service as us,
)

blueprint = Blueprint("generation", __name__)
LOG_ENABLE = True
logger = us.Logger(LOG_ENABLE, __name__)


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

    if grouped_metrics:
        chosen_grouped_metrics = ms.filter_chosen_metrics(
            grouped_metrics, chosen_metrics
        )
        try:
            gs.generate_graphs(
                base_directory,
                directories,
                chosen_grouped_metrics,
                labels=labels,
                loads=loads.values(),
                chosen_loads=loads.keys(),
                fontsize=font_size,
                figsize=us.to_float(*figsize),
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
    chosen_grouped_metrics = ms.filter_chosen_metrics(grouped_metrics, chosen_metrics)

    overwrite = request.form.get("overwrite", "") == "true"
    filename_prefix = op.join(base_directory, ps.get_basename(base_directory))
    logger.debug(f"Filename prefix: {filename_prefix}")
    try:
        full_directories = [op.join(base_directory, d) for d in directories]
        for metric_group, metrics in chosen_grouped_metrics.items():
            simulation_results = ss.load_simulation_results(
                full_directories, metric_group
            )
            for metric in metrics:
                results = gs.compile_individual_data(
                    simulation_results,
                    metric,
                )
                filename = f"{filename_prefix}_{metric.replace(' ', '_')}"
                logger.debug(f"Exporting results for {metric} to {filename}")

                gs.export_results(results, labels, filename, overwrite)
        return jsonify({"message": "Results exported successfully."})
    except Exception as e:
        return jsonify({"error": str(e)})
