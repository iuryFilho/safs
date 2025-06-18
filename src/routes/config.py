from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
)
import os.path as op


from data.metric_data import FILTERED_METRICS
from services import (
    config_service as cs,
    path_service as ps,
    simulation_service as ss,
    utils_service as us,
)


blueprint = Blueprint("config", __name__)
debug_output = True
logger = us.Logger(True, __name__)


@blueprint.record
def record_params(setup_state: dict):
    global debug_output
    debug_output = setup_state.options.get("debug_output", True)


@blueprint.route("", methods=["GET"])
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
            "config.jinja",
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
    figure_width = session.get("figure_width", "10")
    figure_height = session.get("figure_height", "5")
    font_size = session.get("font_size", "medium")
    loads = session.get("loads", [])

    return render_template(
        "config.jinja",
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
        font_size=font_size,
        loads=loads,
        debug_output=debug_output,
    )


@blueprint.route("/get-metrics", methods=["POST"])
def get_metrics():
    """
    Retrieves the metrics based on the base directory and metric type from the session.
    Returns:
        A JSON response containing the grouped metrics for the selected metric type.
    Examples:
        >>> # This endpoint expects a JSON payload with the following structure:
        >>> {
        ... "base-directory": "path/to/base/directory",
        ... "metric-type": "individual"  # or "grouped"
        ... }
    """
    data: dict = request.get_json()
    base_directory = data.get("base-directory", "")
    session["base_directory"] = base_directory
    try:
        simulation_dirs_paths = ps.get_simulations_dirs_paths(base_directory)
        simulation_dirs = [op.basename(s) for s in simulation_dirs_paths]

        metric_type = data.get("metric-type", "individual")
        grouped_metrics = FILTERED_METRICS[metric_type]
        first_metric_group = list(grouped_metrics.keys())[0]
        first_metric = grouped_metrics[first_metric_group][0]
        load_count = ss.get_load_count(
            simulation_dirs_paths[0], first_metric_group, first_metric
        )

        session["directories"] = simulation_dirs
        session["metric_type"] = metric_type
        session["grouped_metrics"] = grouped_metrics
        session["load_count"] = load_count
        session["base_dir_error"] = None
        return redirect(url_for("config.index"))
    except Exception as e:
        session["base_dir_error"] = str(e)
        return redirect(url_for("config.index"))


@blueprint.route("/load-config", methods=["POST"])
def load_config():
    """
    Loads the configuration from the input config file specified in the request.
    Returns:
        A JSON response containing the loaded configuration data or an error message.
    Examples:
        >>> # This endpoint expects a JSON payload with the following structure:
        >>> {
        ... "input-config": "path/to/input/config/file"
        ... }
    """
    data: dict = request.get_json()
    input_config = data.get("input-config", "")
    session["input_config"] = input_config
    try:
        config_data = cs.load_config(input_config)
        session["has_config_data"] = True
        return jsonify({"config_data": config_data})
    except Exception as e:
        session["has_config_data"] = False
        return jsonify({"error": str(e)})


@blueprint.route("/save-config", methods=["POST"])
def save_config():
    """
    Saves the configuration data to the output config file specified in the request.
    Returns:
        A JSON response indicating the success or failure of the save operation.
    Examples:
        >>> # This endpoint expects a JSON payload with the following structure:
        >>> {
        ... "output-config": "path/to/output/config/file",
        ... "config-data": {
        ...     "base-directory": "path/to/base/directory",
        ...     "directories": ["dir1", "dir2"],
        ...     "metric-type": "individual",
        ...     "graph-config": {
        ...         "loads": ["100", "200"],
        ...         "load-filter": "1-2"
        ...     }
        ... }
    """
    data: dict = request.get_json()
    output_config = data.get("output-config", "")
    if not output_config:
        return jsonify({"error": "Output config file is required."})
    session["output_config"] = output_config

    new_config_data = cs.create_config_structure(data)

    result = cs.save_config(new_config_data, output_config)
    return jsonify({"message": result})


@blueprint.route("/update-metric-type", methods=["POST"])
def update_metric_type():
    """
    Updates the metric type in the session based on the request data.
    Returns:
        A JSON response indicating the success of the update operation.
    Examples:
        >>> # This endpoint expects a JSON payload with the following structure:
        >>> {
        ... "metric-type": "individual" or "grouped"
        ... }
    """
    data: dict = request.get_json()
    metric_type = data.get("metric-type", "individual")
    session["metric_type"] = metric_type
    session["grouped_metrics"] = FILTERED_METRICS[metric_type]
    return jsonify({"message": "Metric updated successfully."})
