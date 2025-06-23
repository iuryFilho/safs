from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    session,
)

from services import (
    exportation as es,
    generation as gs,
    metrics as ms,
    utils as us,
)

blueprint = Blueprint("generation", __name__)
debug_output = False
logger = us.Logger(True, __name__)


@blueprint.route("/", methods=["GET"])
def index():
    """
    Renders the configuration page with the current session data.
    Returns:
        Rendered HTML template for the configuration page.
    """
    base_directory = session.get("base_directory", "")
    base_dir_error = session.get("base_dir_error", None)
    if base_dir_error:
        return render_template(
            "generation.jinja",
            base_directory=base_directory,
            base_dir_error=base_dir_error,
            debug_output=debug_output,
        )
    input_config = session.get("input_config", "")
    output_config = session.get("output_config", "")

    directories = session.get("directories", None)
    metric_type = session.get("metric_type", "individual")
    grouped_metrics = session.get("grouped_metrics", None)
    load_count = session.get("load_count", 0)
    has_config_data = session.get("has_config_data", False)

    graph_type = session.get("graph_type", "line")
    overwrite = session.get("overwrite", False)
    figure_width = session.get("figure_width", 10)
    figure_height = session.get("figure_height", 6)
    graph_fontsize = session.get("graph_fontsize", "medium")
    legend_fontsize = session.get("legend_fontsize", "medium")
    max_columns = session.get("max_columns", 5)
    anchor_x = session.get("anchor_x", 0.5)
    anchor_y = session.get("anchor_y", -0.15)
    frameon = session.get("frameon", False)
    legend_position = session.get("legend_position", "upper center")
    loads = session.get("loads", {})

    return render_template(
        "generation.jinja",
        base_directory=base_directory,
        input_config=input_config,
        output_config=output_config,
        directories=directories,
        metric_type=metric_type,
        grouped_metrics=grouped_metrics,
        load_count=load_count,
        has_config_data=has_config_data,
        graph_type=graph_type,
        overwrite=overwrite,
        figure_width=figure_width,
        figure_height=figure_height,
        graph_fontsize=graph_fontsize,
        legend_fontsize=legend_fontsize,
        anchor_x=anchor_x,
        anchor_y=anchor_y,
        legend_position=legend_position,
        max_columns=max_columns,
        frameon=frameon,
        loads=loads,
        debug_output=debug_output,
    )


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
        ...    "figure-height": 6,
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
    grouped_metrics: gs.GroupedMetricT = session.get("grouped_metrics", None)

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
    max_columns = int(data.get("max-columns", "6"))
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

    chosen_grouped_metrics = ms.filter_chosen_metrics(grouped_metrics, chosen_metrics)
    if chosen_grouped_metrics:
        try:
            generator = gs.GraphGenerator()
            generator.initialize_graphs_data(
                base_directory,
                metric_type,
                graph_type,
                directories,
                dir_labels=labels,
                grouped_metrics=chosen_grouped_metrics,
                loads=list(loads.values()),
                load_points=list(loads.keys()),
            ).generate_graphs(
                graph_fontsize,
                legend_fontsize,
                figsize,
                overwrite,
                anchor,
                legend_position,
                max_columns,
                frameon,
            )
            return jsonify({"message": "Gráficos gerados com sucesso."})
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        return jsonify({"error": "Nenhuma métrica selecionada."})


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
        exporter = es.ResultExporter()
        exporter.export_results(
            base_directory,
            metric_type,
            directories,
            labels,
            chosen_grouped_metrics,
            loads=list(loads.values()),
            load_points=list(loads.keys()),
            overwrite=overwrite,
        )
        return jsonify({"message": "Results exported successfully."})
    except Exception as e:
        return jsonify({"error": str(e)})
