from flask import Flask, render_template, request
from markupsafe import escape
import argparse
import TesteGraficoPython.extraction as ex

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.jinja")


@app.route("/choose-metrics", methods=["GET", "POST"])
def choose_metrics() -> str:
    """
    Handles the selection of metrics.
    - If the request method is GET, it renders the initial form for selecting
    metrics.
    - If the request method is POST, it processes the form submission.
        - If you select a valid base directory, it extracts the metrics from the CSV
        files in the specified directory.
        - If the configuration file is successfully loaded, it allows the user to
        load the configuration file with the selected metrics.
        - If the user specifies an output configuration file, it saves the selected
        metrics to that file.
        - If there are any errors during the process, it renders the error messages.
        - Finally, it renders the form with the selected metrics and configuration data.
    Returns:
        template:
            Rendered HTML template for the metrics selection form.
    """
    if request.method == "POST":
        base_directory = request.form["base-directory"]
        simulation_directories, err = ex.get_simulations_directories(base_directory)
        if err:
            return render_template(
                "choose_metrics.jinja",
                base_dir_error=err,
                base_directory=base_directory,
                config_file=config_file,
            )

        csv_paths = ex.get_csv_by_directory(simulation_directories[0])
        metric_groups = ex.extract_metric_group_names(csv_paths)
        grouped_metrics = ex.group_metrics(metric_groups, csv_paths)

        config_file = request.form["config-file"]
        config_data, err = ex.load_config(config_file)
        if err:
            return render_template(
                "choose_metrics.jinja",
                config_file_error=err,
                base_directory=base_directory,
                config_file=config_file,
                grouped_metrics=grouped_metrics,
            )

        output_config_file = request.form.get("output-config-file", "")
        if output_config_file:
            new_config_data = {}
            for metric_group, metric_list in config_data.items():
                for metric in metric_list:
                    if metric in request.form:
                        new_config_data[metric_group] = new_config_data.get(
                            metric_group, []
                        ) + [metric]
            ex.save_config(new_config_data, output_config_file)

        return render_template(
            "choose_metrics.jinja",
            base_directory=base_directory,
            config_file=config_file,
            simulation_directories=simulation_directories,
            grouped_metrics=grouped_metrics,
            config_data=config_data,
        )
    else:
        return render_template("choose_metrics.jinja")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Flask app.")
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the server on"
    )
    parser.add_argument(
        "--no-debug", action="store_false", help="Disable debug mode for the server"
    )
    args = parser.parse_args()

    app.run(host="127.0.0.1", port=args.port, debug=args.no_debug)
