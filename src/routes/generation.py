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
logger = us.Logger(True, __name__)


@blueprint.route("/generate-graphs", methods=["POST"])
def generate_graphs():
    """
    Generates graphs based on the provided data and session information.
    Returns:
        A JSON response indicating the success or failure of the graph generation.
    Examples:
        >>> # This endpoint expects a JSON payload with the following structure:
        >>> {
        ...    "directory-list": ["dir1", "dir2", ..., "dirN"],
        ...    "directory-labels": ["label1", "label2", ..., "labelN"],
        ...    "metric-list": ["metric1", "metric2", ...],
        ...    "graph-type": "line", "bar" or "scatter",
        ...    "overwrite": true or false,
        ...    "figure-width": 10,
        ...    "figure-height": 5,
        ...    "frameon": true or false,
        ...    "max-columns": 5,
        ...    "graph-font-size": "medium",
        ...    "legend-font-size": "medium",
        ...    "legend-position": "upper center",
        ...    "anchor-x": 0.5,
        ...    "anchor-y": -0.15,
        ...    "loads": {"1": "100", "2": "200", ...}
        ... }
    """
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
    figsize = us.to_float(
        data.get("figure-width", "10"),
        data.get("figure-height", "5"),
    )
    graph_fontsize = data.get("graph-font-size", "medium")
    legend_fontsize = data.get("legend-font-size", "medium")
    anchor = us.to_float(
        data.get("anchor-x", "0.5"),
        data.get("anchor-y", "-0.15"),
    )
    legend_position = data.get("legend-position", "upper center")
    max_columns = int(data.get("max-columns", "5"))
    frameon = data.get("frameon", "") == "true"
    loads: dict = data.get("loads", {})

    session["labels"] = session_labels
    session["graph_type"] = graph_type
    session["overwrite"] = overwrite
    session["figure_width"] = figsize[0]
    session["figure_height"] = figsize[1]
    session["graph_fontsize"] = graph_fontsize
    session["legend_fontsize"] = legend_fontsize
    session["legend_position"] = legend_position
    session["anchor_x"] = anchor[0]
    session["anchor_y"] = anchor[1]
    session["frameon"] = frameon
    session["max_columns"] = max_columns
    session["loads"] = loads

    if grouped_metrics:
        chosen_grouped_metrics = ms.filter_chosen_metrics(
            grouped_metrics, chosen_metrics
        )
        try:
            gs.generate_graphs(
                base_directory=base_directory,
                directories=directories,
                dir_labels=labels,
                grouped_metrics=chosen_grouped_metrics,
                loads=loads.values(),
                load_points=loads.keys(),
                metric_type=metric_type,
                graph_type=graph_type,
                overwrite=overwrite,
                figsize=figsize,
                graph_fontsize=graph_fontsize,
                legend_fontsize=legend_fontsize,
                bbox_to_anchor=anchor,
                legend_position=legend_position,
                max_columns=max_columns,
                frameon=frameon,
            )
            return jsonify({"message": "Graphs generated successfully."})
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        return jsonify({"error": "No metrics selected."})


@blueprint.route("/export-results", methods=["POST"])
def export_results():
    """
    Exports the results of the simulations based on the provided data and session information.
    Returns:
        A JSON response indicating the success or failure of the export operation.
    Examples:
        >>> # This endpoint expects a JSON payload with the following structure:
        >>> {
        ...    "directory-list": ["dir1", "dir2", ..., "dirN"],
        ...    "directory-labels": ["label1", "label2", ..., "labelN"],
        ...    "metric-list": ["metric1", "metric2", ...],
        ...    "loads": {"1": "100", "2": "200", ...},
        ...    "overwrite": true or false
        ... }
    """
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
