from flask import (
    Blueprint,
    request,
    jsonify,
    session,
)

from services import (
    generation_service as gs,
    metrics_service as ms,
    utils_service as us,
    export_service as es,
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
    labels, session_labels = us.extract_labels(directories, raw_labels)
    chosen_metrics = data.get("metric-list", [])

    graph_type = data.get("graph-type", "line")
    overwrite = data.get("overwrite", "") == "true"
    figsize = (
        data.get("figure-width", "10"),
        data.get("figure-height", "5"),
    )
    font_size = data.get("font-size", "medium")
    loads: dict = data.get("loads", {})

    session["labels"] = session_labels
    session["graph_type"] = graph_type
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
                base_directory=base_directory,
                directories=directories,
                grouped_metrics=chosen_grouped_metrics,
                labels=labels,
                loads=loads.values(),
                load_points=loads.keys(),
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
    metric_type = session.get("metric_type", "individual")
    grouped_metrics = session.get("grouped_metrics", None)

    if not grouped_metrics:
        return jsonify({"error": "No metrics selected."})

    data: dict = request.get_json()
    directories = data.get("directory-list", [])
    raw_labels = data.get("directory-labels", [])
    labels, session_labels = us.extract_labels(directories, raw_labels)

    chosen_metrics = data.get("metric-list", [])
    chosen_grouped_metrics = ms.filter_chosen_metrics(grouped_metrics, chosen_metrics)
    loads: dict = data.get("loads", {})
    overwrite = data.get("overwrite", "") == "true"

    session["labels"] = session_labels
    session["loads"] = loads
    session["overwrite"] = overwrite
    try:
        es.export_results(
            base_directory,
            metric_type,
            directories,
            labels,
            chosen_grouped_metrics,
            loads=loads.values(),
            load_points=loads.keys(),
            overwrite=overwrite,
        )
        return jsonify({"message": "Results exported successfully."})
    except Exception as e:
        return jsonify({"error": str(e)})
