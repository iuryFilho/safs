import pandas as pd
import os.path as op

from data.metric_data import METRIC_GROUP_ALIASES
from services import simulation_service as ss, path_service as ps


def export_results(
    base_directory: str,
    metric_type: str,
    directories: list[str],
    labels: list[str],
    chosen_grouped_metrics: dict[str, list[str]],
    loads: list[str],
    load_points: list[str],
    overwrite: bool,
):
    if metric_type == "individual":
        export_func = export_individual_results
    elif metric_type == "grouped":
        export_func = export_grouped_results
    filename = op.join(
        base_directory, f"{ps.get_basename(base_directory)}_{metric_type}"
    )
    filename = ps.ensure_unique_filename(filename, overwrite)
    full_directories = [op.join(base_directory, d) for d in directories]
    int_loads = [int(l) for l in loads]
    with pd.ExcelWriter(f"{filename}.xlsx") as writer:
        for metric_group, metrics in chosen_grouped_metrics.items():
            simulation_results = ss.load_simulation_results(
                full_directories, metric_group
            )
            metric_group_alias = METRIC_GROUP_ALIASES[metric_group]
            export_func(
                metric_group_alias,
                metrics,
                simulation_results,
                labels,
                int_loads,
                load_points,
                writer,
            )


def export_individual_results(
    metric_group: str,
    metrics: list[str],
    simulation_results: list[pd.DataFrame],
    labels: list[str],
    int_loads: list[int],
    load_points: list[str],
    writer: pd.ExcelWriter,
):
    int_load_points = [int(lp) for lp in load_points]
    all_tables = []
    for metric in metrics:
        results = ss.compile_individual_data(simulation_results, metric, load_points)

        table = assemble_results_table(labels, int_loads, int_load_points, results)
        out_df = pd.DataFrame(table)
        out_df.columns = pd.MultiIndex.from_tuples(out_df.columns)

        out_df = add_label_column("metric", metric, out_df)
        all_tables.append(out_df)

        empty_row = create_empty_row(out_df)
        all_tables.append(empty_row)
    final_df = pd.concat(all_tables, ignore_index=True)
    final_df.to_excel(writer, sheet_name=metric_group)


def export_grouped_results(
    metric_group: str,
    metrics: list[str],
    simulation_results: list[pd.DataFrame],
    labels: list[str],
    int_loads: list[int],
    load_points: list[str],
    writer: pd.ExcelWriter,
):
    int_load_points = [int(lp) for lp in load_points]
    all_tables = []
    for label, simulation_result in zip(labels, simulation_results):
        results = ss.compile_grouped_data(simulation_result, metrics, load_points)

        table = assemble_results_table(metrics, int_loads, int_load_points, results)
        out_df = pd.DataFrame(table)
        out_df.columns = pd.MultiIndex.from_tuples(out_df.columns)

        out_df = add_label_column("solution", label, out_df)
        all_tables.append(out_df)

        empty_row = create_empty_row(out_df)
        all_tables.append(empty_row)
    final_df = pd.concat(all_tables, ignore_index=True)
    final_df.to_excel(writer, sheet_name=metric_group)


def assemble_results_table(headers, int_loads, load_points, results):
    columns = [("", "point"), ("", "load")]
    data = [load_points, int_loads]
    for header, df in zip(headers, results):
        columns.append((header, "mean"))
        columns.append((header, "error"))
        data.append(df["mean"])
        data.append(df["error"])
    return dict(zip(columns, data))


def add_label_column(column_name: str, label: str, df: pd.DataFrame) -> pd.DataFrame:
    df[("", column_name)] = ""
    df.at[0, ("", column_name)] = label
    cols = [("", column_name)] + [col for col in df.columns if col != ("", column_name)]
    return df[cols]


def create_empty_row(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([[""] * len(df.columns)], columns=df.columns)


def main():
    return


if __name__ == "__main__":
    main()
