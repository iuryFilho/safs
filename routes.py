from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
)
import TesteGraficoPython.extraction as ex

metrics = Blueprint("metrics", __name__)


@metrics.route("", methods=["GET"])
def get_metrics_form():
    base_directory = session.get("base_directory", "")
    directories = session.pop("directories", None)
    grouped_metrics = session.pop("grouped_metrics", None)
    return render_template(
        "metrics.jinja",
        base_directory=base_directory,
        directories=directories,
        grouped_metrics=grouped_metrics,
    )


@metrics.route("/extract", methods=["POST"])
def extract_metrics():
    base_directory = request.form["base-directory"]
    session["base_directory"] = base_directory
    try:
        print("Base Directory:", base_directory)
        simulation_directories_paths = ex.get_simulations_directories(base_directory)
        directories = [s.split("/")[-2] for s in simulation_directories_paths]
        csv_paths = ex.get_csv_by_directory(simulation_directories_paths[0])
        metric_groups = ex.extract_metric_group_names(csv_paths)
        grouped_metrics = ex.group_metrics(metric_groups, csv_paths)
        # Salva na sessão
        session["directories"] = directories
        session["grouped_metrics"] = grouped_metrics
        # Redireciona para o GET, que renderiza o template com os dados
        print(1)
        return redirect(url_for("metrics.get_metrics_form"))
    except Exception as e:
        session["error"] = str(e)
        return redirect(url_for("metrics.get_metrics_form"))


@metrics.route("/load-config", methods=["POST"])
def load_config():
    input_config = request.form.get("input-config", "")
    try:
        config_data = ex.load_config(input_config)
        return jsonify({"config_data": config_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@metrics.route("/save-config", methods=["POST"])
def save_config():
    output_config = request.form.get("output-config", "")
    grouped_metrics = request.form.get("grouped-metrics", {})
    new_config_data = {"directories": [], "metrics": {}}
    for dir in request.form.getlist("directory-list"):
        new_config_data["directories"].append(dir)
    metric_list_form = request.form.getlist("metric-list")
    # Aqui você pode precisar ajustar a lógica para reconstruir grouped_metrics
    for metric_group, metric_list in grouped_metrics.items():
        for metric in metric_list_form:
            if metric in metric_list:
                new_config_data["metrics"][metric_group] = new_config_data[
                    "metrics"
                ].get(metric_group, []) + [metric]
    ex.save_config(new_config_data, output_config)
    return jsonify({"message": "Configuração salva com sucesso!"})
