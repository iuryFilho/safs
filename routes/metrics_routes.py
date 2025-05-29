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

blueprint = Blueprint("metrics", __name__)
debug_output = True


@blueprint.record
def record_params(setup_state):
    global debug_output
    debug_output = setup_state.options.get("debug_output", True)


@blueprint.route("", methods=["GET"])
def metrics_index():
    base_directory = session.get("base_directory", "")
    base_dir_error = session.get("base_dir_error", None)
    if base_dir_error:
        return render_template(
            "metrics.jinja",
            base_directory=base_directory,
            base_dir_error=base_dir_error,
            debug_output=debug_output,
        )
    input_config = session.get("input_config", "")
    output_config = session.get("output_config", "")

    directories = session.get("directories", None)
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
        "metrics.jinja",
        base_directory=base_directory,
        input_config=input_config,
        output_config=output_config,
        directories=directories,
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
        simulation_directories_paths = ex.get_simulations_directories(base_directory)
        simulation_directories = [
            s.split("/")[-2] for s in simulation_directories_paths
        ]
        csv_paths = ex.get_csv_paths(simulation_directories_paths[0])
        grouped_metrics = ex.group_metrics(csv_paths)
        load_count = ex.get_load_count(
            list(grouped_metrics.values())[0][0], csv_paths[0]
        )

        session["directories"] = simulation_directories
        session["grouped_metrics"] = grouped_metrics
        session["load_count"] = load_count
        session["base_dir_error"] = None
        return redirect(url_for("metrics.metrics_index"))
    except Exception as e:
        session["base_dir_error"] = str(e)
        return redirect(url_for("metrics.metrics_index"))


@blueprint.route("/load-config", methods=["POST"])
def load_config():
    input_config = request.form.get("input-config", "")
    session["input_config"] = input_config
    try:
        config_data = ex.load_config(input_config)
        session["has_config_data"] = True
        return jsonify({"config_data": config_data})
    except Exception as e:
        session["has_config_data"] = False
        return jsonify({"error": str(e)})


@blueprint.route("/save-config", methods=["POST"])
def save_config():
    output_config = request.form.get("output-config", "")
    if not output_config:
        return jsonify({"error": "Output config file is required."})
    session["output_config"] = output_config

    new_config_data = {"directories": {}, "metrics": {}}
    directories = request.form.getlist("directory-list")
    labels = request.form.getlist("labels")
    for dir, label in zip(directories, labels):
        new_config_data["directories"][dir] = label

    grouped_metrics = session.get("grouped_metrics", None)
    metric_list_form = request.form.getlist("metric-list")
    for metric_group, metric_list in grouped_metrics.items():
        for metric in metric_list_form:
            if metric in metric_list:
                new_config_data["metrics"][metric_group] = new_config_data[
                    "metrics"
                ].get(metric_group, []) + [metric]

    result = ex.save_config(new_config_data, output_config)
    return jsonify({"message": result})
