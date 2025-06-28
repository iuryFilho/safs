from flask import Blueprint, render_template, request, jsonify
from services import (
    exportation as es,
    generation as gs,
    loads_utils as lus,
    metrics_utils as mus,
    session_data_utils as sdus,
    utils as us,
)
from data.metric_data import FILTERED_METRICS as FM

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
    base_directory = sdus.get_session("base_directory")
    base_dir_error = sdus.get_session("base_dir_error")
    if base_dir_error:
        return render_template(
            "generation.jinja",
            debug_output=debug_output,
            base_directory=base_directory,
            base_dir_error=base_dir_error,
        )
    metric_type = sdus.get_session("metric_type")
    return render_template(
        "generation.jinja",
        debug_output=debug_output,
        base_directory=base_directory,
        metric_type=metric_type,
        grouped_metrics=FM[metric_type],
        input_config=sdus.get_session("input_config"),
        output_config=sdus.get_session("output_config"),
        directories=sdus.get_session("directories"),
        load_count=sdus.get_session("load_count"),
        has_config_data=sdus.get_session("has_config_data"),
        graph_type=sdus.get_session("graph_type"),
        language=sdus.get_session("language"),
        overwrite="true" if sdus.get_session("overwrite") else "false",
        use_grid="true" if sdus.get_session("use_grid") else "false",
        ylim_low=sdus.get_session("ylim_low"),
        x_axis_direction=sdus.get_session("x_axis_direction"),
        title=sdus.get_session("title"),
        xlabel=sdus.get_session("xlabel"),
        ylabel=sdus.get_session("ylabel"),
        figure_width=sdus.get_session("figure_width"),
        figure_height=sdus.get_session("figure_height"),
        graph_fontsize=sdus.get_session("graph_fontsize"),
        legend_fontsize=sdus.get_session("legend_fontsize"),
        max_columns=sdus.get_session("max_columns"),
        anchor_x=sdus.get_session("anchor_x"),
        anchor_y=sdus.get_session("anchor_y"),
        frameon="true" if sdus.get_session("frameon") else "false",
        legend_position=sdus.get_session("legend_position"),
        use_custom_loads=sdus.get_session("use_custom_loads"),
        load_points_filter=sdus.get_session("load_points_filter"),
        loads=sdus.get_session("loads"),
    )


@blueprint.route("/generate-graphs", methods=["POST"])
def generate_graphs():
    """
    Generates graphs based on the provided data and session information.
    Returns:
        A JSON response indicating the success or failure of the graph generation.
    """
    base_directory = sdus.get_session("base_directory")
    metric_type = sdus.get_session("metric_type")
    use_custom_loads = sdus.get_session("use_custom_loads")

    data = sdus.Data(request.get_json())
    directories: list[str] = data["directory-list"]
    if not directories:
        return jsonify({"error": "Nenhum diretório selecionado."})
    raw_labels = data["labels"]
    labels, session_labels = us.extract_labels(directories, raw_labels)
    grouped_metrics = data["grouped-metrics"]
    if not grouped_metrics:
        return jsonify({"error": "Nenhuma métrica selecionada."})

    graph_type = data["graph-type"]
    language = data["language"]
    overwrite = data["overwrite"] == "true"
    use_grid = data["use-grid"] == "true"
    ylim_low = data["ylim-low"]
    ylim_up = data["ylim-up"]
    x_axis_direction = data["x-axis-direction"]
    title = data["title"]
    xlabel = data["xlabel"]
    ylabel = data["ylabel"]
    figsize = us.to_float(
        data["figure-width"],
        data["figure-height"],
    )
    graph_fontsize = data["graph-font-size"]
    legend_fontsize = data["legend-font-size"]
    anchor = us.to_float(
        data["anchor-x"],
        data["anchor-y"],
    )
    legend_position = data["legend-position"]
    max_columns = int(data["max-columns"])
    frameon = data["frameon"] == "true"

    load_error = ""
    load_points_filter = ""
    if use_custom_loads:
        raw_loads: dict = data["loads"]
    else:
        load_points_filter = data["load-points-filter"]
        try:
            raw_loads: dict = lus.calculate_loads(
                base_directory, directories[0], load_points_filter
            )
            for i in range(1, len(directories)):
                other_raw_loads = lus.calculate_loads(
                    base_directory, directories[i], load_points_filter
                )
                if len(other_raw_loads) != len(raw_loads):
                    load_error = "Gráficos gerados com sucesso, mas a quantidade de pontos de carga não é igual entre os diretórios selecionados."
                    break
        except Exception as e:
            return jsonify({"error": str(e)})
    loads = list(raw_loads.values())
    load_points = list(raw_loads.keys())
    sdus.set_session_data(
        {
            "labels": session_labels,
            "graph_type": graph_type,
            "language": language,
            "overwrite": overwrite,
            "use_grid": use_grid,
            "ylim_low": ylim_low,
            "ylim_up": ylim_up,
            "x_axis_direction": x_axis_direction,
            "title": title,
            "xlabel": xlabel,
            "ylabel": ylabel,
            "figure_width": figsize[0],
            "figure_height": figsize[1],
            "graph_fontsize": graph_fontsize,
            "legend_fontsize": legend_fontsize,
            "legend_position": legend_position,
            "anchor_x": anchor[0],
            "anchor_y": anchor[1],
            "frameon": frameon,
            "max_columns": max_columns,
            "load_points_filter": load_points_filter,
            "loads": raw_loads,
        }
    )

    if grouped_metrics:
        try:
            gs.GraphGenerator(
                base_directory,
                metric_type,
                language,
                graph_type,
                directories,
                dir_labels=labels,
                grouped_metrics=grouped_metrics,
                loads=loads,
                load_points=load_points,
            ).generate_graphs(
                ylim_low,
                ylim_up,
                x_axis_direction,
                title,
                xlabel,
                ylabel,
                graph_fontsize,
                legend_fontsize,
                figsize,
                overwrite,
                use_grid,
                anchor,
                legend_position,
                max_columns,
                frameon,
            )
            if load_error:
                return jsonify({"error": load_error})
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
    """
    base_directory = sdus.get_session("base_directory")
    use_custom_loads = sdus.get_session("use_custom_loads")
    metric_type = sdus.get_session("metric_type")

    data = sdus.Data(request.get_json())
    directories = data["directory-list"]
    if not directories:
        return jsonify({"error": "Nenhum diretório selecionado."})
    raw_labels = data["labels"]
    labels, session_labels = us.extract_labels(directories, raw_labels)

    grouped_metrics = data["grouped-metrics"]
    if not grouped_metrics:
        return jsonify({"error": "Nenhuma métrica selecionada."})
    overwrite = data["overwrite"] == "true"

    if use_custom_loads:
        raw_loads: dict = data["loads"]
    else:
        load_points_filter = data["load-points-filter"]
        try:
            raw_loads = lus.calculate_loads(
                base_directory, directories[0], load_points_filter
            )
        except Exception as e:
            return jsonify({"error": str(e)})
    loads = list(raw_loads.values())
    load_points = list(raw_loads.keys())

    sdus.set_session_data(
        {
            "labels": session_labels,
            "loads": loads,
            "overwrite": overwrite,
        }
    )
    try:
        es.ResultExporter().export_results(
            base_directory,
            metric_type,
            directories,
            labels,
            grouped_metrics,
            loads=loads,
            load_points=load_points,
            overwrite=overwrite,
        )
        return jsonify({"message": "Resultados exportados com sucesso."})
    except Exception as e:
        return jsonify({"error": str(e)})
