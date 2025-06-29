from flask import Blueprint, request, jsonify
import os.path as op

from services import (
    session_data_utils as sdus,
    config_utils as cs,
    loads_utils as lus,
    path_utils as pus,
    utils as us,
)


blueprint = Blueprint("config", __name__)


@blueprint.route("/clear-session", methods=["POST"])
def clear_session():
    """Clear the session data."""
    message, status_code = sdus.clear_session()
    return jsonify(message), status_code


@blueprint.route("/load-directory", methods=["POST"])
def load_directory():
    """
    Loads the directory specified in the request and retrieves simulation directories and metrics.
    Returns:
        A JSON response containing the simulation directories and metrics or an error message.
        - If the base directory is not found or an error occurs, it sets an error message in the session.
    """
    data = sdus.Data(request.get_json())
    base_directory = data["base-directory"]
    sess_data = {"base_directory": base_directory}
    try:
        if base_directory != "":
            simulation_dirs_paths = pus.get_simulations_dirs_paths(base_directory)
            simulation_dirs = [op.basename(s) for s in simulation_dirs_paths]

            metric_type: str = data["metric-type"]
            base_path = op.join(base_directory, simulation_dirs[0])
            use_custom_loads: bool = data["use-custom-loads"]
            if not use_custom_loads:
                loads = lus.calculate_loads(base_directory, simulation_dirs[0])
                sess_data["loads"] = loads
            load_count = lus.get_number_of_load_points(base_path)

            sess_data.update(
                {
                    "load_count": load_count,
                    "directories": simulation_dirs,
                    "metric_type": metric_type,
                    "base_dir_error": None,
                }
            )
    except Exception as e:
        sess_data["base_dir_error"] = str(e)
    finally:
        sdus.set_session_data(sess_data)
        return ""


@blueprint.route("/load-config", methods=["POST"])
def load_config():
    """
    Loads the configuration from the input config file specified in the request.
    Returns:
        A JSON response containing the loaded configuration data or an error message.
    """
    data = sdus.Data(request.get_json())
    input_config = data["input-config"]
    sess_data = {"input_config": input_config}
    response = {}
    try:
        config_data = cs.load_config(input_config)
        sess_data["has_config_data"] = True
        response = {"config_data": config_data}
    except Exception as e:
        sess_data["has_config_data"] = False
        response = {"error": str(e)}
    finally:
        sdus.set_session_data(sess_data)
        return jsonify(response)


@blueprint.route("/save-config", methods=["POST"])
def save_config():
    """
    Saves the configuration data to the output config file specified in the request.
    Returns:
        A JSON response indicating the success or failure of the save operation.
    """
    data = sdus.Data(request.get_json())
    output_config = data["output-config"]
    sdus.set_session_data({"output_config": output_config})
    if not output_config:
        return ""

    new_config_data = cs.create_config_structure(data)

    result = cs.save_config(new_config_data, output_config)
    return jsonify({"message": result})


@blueprint.route("/update-metric-type", methods=["POST"])
def update_metric_type():
    """
    Updates the metric type in the session based on the request data.
    Returns:
        A JSON response indicating the success of the update operation.
    """
    data = sdus.Data(request.get_json())
    metric_type = data["metric-type"]
    sdus.set_session_data({"metric_type": metric_type})
    return jsonify({"message": "Metric updated successfully."})


@blueprint.route("/update-use-custom-loads", methods=["POST"])
def update_use_custom_loads():
    """
    Updates the use of custom loads in the session based on the request data.
    Returns:
        A JSON response indicating the success of the update operation.
    """
    data = sdus.Data(request.get_json())
    use_custom_loads = data["use-custom-loads"]
    sdus.set_session_data({"use_custom_loads": use_custom_loads})
    return jsonify({"message": "Custom loads updated successfully."})
