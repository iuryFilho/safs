from flask import Blueprint, render_template, jsonify
from services import (
    exportation as es,
    generation as gs,
    loads_utils as lus,
    data_utils as dus,
    utils as us,
)
from services.data_utils import session
from data.metric_data import FILTERED_METRICS as FM

blueprint = Blueprint("generation", __name__)
debug_output = False


@blueprint.route("/", methods=["GET"])
def index():
    """
    Renders the configuration page with the current session data.
    Returns:
        Rendered HTML template for the configuration page.
    """
    base_directory = session["base_directory"]
    base_dir_error = session["base_dir_error"]
    if base_dir_error:
        return render_template(
            "generation.jinja",
            debug_output=debug_output,
            base_directory=base_directory,
            base_dir_error=base_dir_error,
        )
    metric_type = session["metric_type"]
    return render_template(
        "generation.jinja",
        debug_output=debug_output,
        base_directory=base_directory,
        metric_type=metric_type,
        grouped_metrics=FM[metric_type],
        input_config=session["input_config"],
        output_config=session["output_config"],
        directories=session["directories"],
        load_count=session["load_count"],
        has_config_data=session["has_config_data"],
        graph_type=session["graph_type"],
        language=session["language"],
        overwrite="true" if session["overwrite"] else "false",
        use_grid="true" if session["use_grid"] else "false",
        ylim_low=session["ylim_low"],
        ylim_up=session["ylim_up"],
        x_axis_direction=session["x_axis_direction"],
        title=session["title"],
        xlabel=session["xlabel"],
        ylabel=session["ylabel"],
        figure_width=session["figure_width"],
        figure_height=session["figure_height"],
        graph_fontsize=session["graph_fontsize"],
        legend_fontsize=session["legend_fontsize"],
        max_columns=session["max_columns"],
        anchor_x=session["anchor_x"],
        anchor_y=session["anchor_y"],
        frameon="true" if session["frameon"] else "false",
        legend_position=session["legend_position"],
        use_custom_loads=session["use_custom_loads"],
        load_points_filter=session["load_points_filter"],
        loads=session["loads"],
    )


@blueprint.route("/generate-graphs", methods=["POST"])
def generate_graphs():
    """
    Generates graphs based on the provided data and session information.
    Returns:
        A JSON response indicating the success or failure of the graph generation.
    """
    base_directory = session["base_directory"]
    metric_type = session["metric_type"]
    use_custom_loads = session["use_custom_loads"]

    data = dus.Data()
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
    session.update(
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
            return jsonify({"error": "Erro ao gerar gráficos:\n" + str(e)})
    else:
        return jsonify({"error": "Nenhuma métrica selecionada."})


@blueprint.route("/export-results", methods=["POST"])
def export_results():
    """
    Exports the results of the simulations based on the provided data and session information.
    Returns:
        A JSON response indicating the success or failure of the export operation.
    """
    base_directory = session["base_directory"]
    use_custom_loads = session["use_custom_loads"]
    metric_type = session["metric_type"]

    data = dus.Data()
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
            return jsonify({"error": "Erro ao calcular cargas:\n" + str(e)})
    loads = list(raw_loads.values())
    load_points = list(raw_loads.keys())

    session.update(
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
        return jsonify({"error": "Erro ao exportar resultados:\n" + str(e)})
