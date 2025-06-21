from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    session,
)
import os.path as op


from data.metric_data import FILTERED_METRICS
from services import (
    config as cs,
    path as ps,
    simulation as ss,
    utils as us,
)


blueprint = Blueprint("config", __name__)
logger = us.Logger(True, __name__)


@blueprint.route("/clear-session", methods=["POST"])
def clear_session():
    """Clear the session data."""
    try:
        session.clear()
        return jsonify({"message": "Sessão limpa com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@blueprint.route("/load-directory", methods=["POST"])
def load_directory():
    """
    Loads the directory specified in the request and retrieves simulation directories and metrics.
    Returns:
        A JSON response containing the simulation directories and metrics or an error message.
        - If the base directory is not found or an error occurs, it sets an error message in the session.
    Examples:
        >>> # This endpoint expects a JSON payload with the following structure:
        >>> {
        ... "base-directory": "path/to/base/directory",
        ... "metric-type": "individual"  # or "grouped"
        ... }
    """
    data: dict = request.get_json()
    base_directory = data.get("base-directory", "")
    print(f"Base directory: {base_directory}")
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
        return "Ok"
    except Exception as e:
        session["base_dir_error"] = str(e)
        return "Ok"


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
