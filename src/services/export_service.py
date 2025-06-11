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
    filename_prefix = op.join(
        base_directory, f"{ps.get_basename(base_directory)}_{metric_type}"
    )
    full_directories = [op.join(base_directory, d) for d in directories]
    int_loads = [int(l) for l in loads]
    for metric_group, metrics in chosen_grouped_metrics.items():
        simulation_results = ss.load_simulation_results(full_directories, metric_group)
        metric_group_alias = METRIC_GROUP_ALIASES[metric_group]
        filename = f"{filename_prefix}_{metric_group_alias}"
        if not overwrite and op.exists(f"{filename}.xlsx"):
            i = 0
            while True:
                new_filename = f"{filename}_{i}"
                if op.exists(f"{new_filename}.xlsx"):
                    i += 1
                else:
                    filename = new_filename
                    break
        export_func(
            f"{filename}.xlsx",
            metrics,
            simulation_results,
            labels,
            int_loads,
            load_points,
        )


def export_individual_results(
    filename: str,
    metrics: list[str],
    simulation_results: list[pd.DataFrame],
    labels: list[str],
    int_loads: list[int],
    load_points: list[str],
):
    with pd.ExcelWriter(filename) as writer:
        for metric in metrics:
            results = ss.compile_individual_data(
                simulation_results, metric, load_points
            )
            columns = [("Load Points", "points"), ("Load Points", "loads")]
            data = [load_points, int_loads]
            for label, df in zip(labels, results):
                columns.append((label, "mean"))
                columns.append((label, "error"))
                data.append(df["mean"])
                data.append(df["error"])
            out_df = pd.DataFrame(dict(zip(columns, data)))
            out_df.columns = pd.MultiIndex.from_tuples(out_df.columns)
            out_df.to_excel(writer, sheet_name=metric[:31])


def export_grouped_results(
    filename: str,
    metrics: list[str],
    simulation_results: list[pd.DataFrame],
    labels: list[str],
    int_loads: list[int],
    load_points: list[str],
):
    all_tables = []
    for label, simulation_result in zip(labels, simulation_results):
        results = ss.compile_grouped_data(simulation_result, metrics, load_points)

        table = assemble_results_table(metrics, int_loads, load_points, results)
        out_df = pd.DataFrame(table)
        out_df.columns = pd.MultiIndex.from_tuples(out_df.columns)

        out_df = add_label(label, out_df)
        all_tables.append(out_df)

        empty_row = create_empty_row(out_df)
        all_tables.append(empty_row)
    final_df = pd.concat(all_tables, ignore_index=True)
    with pd.ExcelWriter(filename) as writer:
        final_df.to_excel(writer, sheet_name="Resultados")


def assemble_results_table(metrics, int_loads, load_points, results):
    columns = [("Load Points", "points"), ("Load Points", "loads")]
    data = [load_points, int_loads]
    for metric, df in zip(metrics, results):
        columns.append((metric, "mean"))
        columns.append((metric, "error"))
        data.append(df["mean"])
        data.append(df["error"])
    return dict(zip(columns, data))


def add_label(label: str, df: pd.DataFrame) -> pd.DataFrame:
    df[("", "Solution")] = ""
    df.at[0, ("", "Solution")] = label
    cols = [("", "Solution")] + [col for col in df.columns if col != ("", "Solution")]
    return df[cols]


def create_empty_row(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([[""] * len(df.columns)], columns=df.columns)


def main():
    return


if __name__ == "__main__":
    main()
