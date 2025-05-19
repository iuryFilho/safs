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
        input_config = request.form.get("input-config", "")
        output_config = request.form.get("output-config", "")
        action = request.form.get("action", "")
        print(f"Action: {action}")

        try:
            simulation_directories_paths = ex.get_simulations_directories(
                base_directory
            )
        except Exception as e:
            return render_template(
                "choose_metrics.jinja",
                base_dir_error=str(e),
                base_directory=base_directory,
                input_config=input_config,
                output_config=output_config,
            )

        simulation_directories = [
            s.split("/")[-2] for s in simulation_directories_paths
        ]

        csv_paths = ex.get_csv_by_directory(simulation_directories_paths[0])
        metric_groups = ex.extract_metric_group_names(csv_paths)
        grouped_metrics = ex.group_metrics(metric_groups, csv_paths)

        try:
            config_data = ex.load_config(input_config)
        except Exception as e:
            return render_template(
                "choose_metrics.jinja",
                input_config_error=str(e),
                base_directory=base_directory,
                input_config=input_config,
                simulation_directories=simulation_directories,
                grouped_metrics=grouped_metrics,
                output_config=output_config,
            )

        if action == "save-config" and output_config:
            new_config_data = {"directories": [], "metrics": {}}
            for dir in simulation_directories:
                if dir in request.form:
                    new_config_data["directories"].append(dir)
            for metric_group, metric_list in grouped_metrics.items():
                for metric in metric_list:
                    if metric in request.form:
                        new_config_data["metrics"][metric_group] = new_config_data[
                            "metrics"
                        ].get(metric_group, []) + [metric]
            ex.save_config(new_config_data, output_config)

        return render_template(
            "choose_metrics.jinja",
            base_directory=base_directory,
            input_config=input_config,
            config_data=config_data,
            simulation_directories=simulation_directories,
            grouped_metrics=grouped_metrics,
            output_config=output_config,
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
