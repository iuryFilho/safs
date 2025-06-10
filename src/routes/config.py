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


from data.metric_groups import filtered_metrics
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
def record_params(setup_state):
    global debug_output
    debug_output = setup_state.options.get("debug_output", True)


@blueprint.route("", methods=["GET"])
def index():
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
    graph_composition = session.get("graph_composition", "individual")
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
        graph_composition=graph_composition,
        overwrite=overwrite,
        figure_width=figure_width,
        figure_height=figure_height,
        font_size=font_size,
        loads=loads,
        debug_output=debug_output,
    )


@blueprint.route("/get-metrics", methods=["POST"])
def get_metrics():
    base_directory = request.form["base-directory"]
    session["base_directory"] = base_directory
    try:
        simulation_dirs_paths = ps.get_simulations_dirs_paths(base_directory)
        simulation_dirs = [op.basename(s) for s in simulation_dirs_paths]

        metric_type = request.form.get("metric_type", "individual")
        grouped_metrics = filtered_metrics[metric_type]
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
    input_config = request.form.get("input-config", "")
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
    data: dict = request.get_json()
    output_config = data.get("output-config", "")
    if not output_config:
        return jsonify({"error": "Output config file is required."})
    session["output_config"] = output_config

    new_config_data = cs.create_config_structure(data)

    graph_config = data.get("graph-config", {})
    new_config_data["graph-config"] = graph_config

    result = cs.save_config(new_config_data, output_config)
    return jsonify({"message": result})


@blueprint.route("/update-metric-type", methods=["POST"])
def update_metric_type():
    data: dict = request.get_json()
    metric_type = data.get("metric-type", "individual")
    session["metric_type"] = metric_type
    session["grouped_metrics"] = filtered_metrics[metric_type]
    return jsonify({"message": "Metric updated succesfully."})
