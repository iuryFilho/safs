import pandas as pd
import os.path as op
from services import simulation_service as ss


def export_results(
    base_directory: str,
    metric_type: str,
    directories: list[str],
    chosen_grouped_metrics: dict[str, list[str]],
    filename_prefix: str,
    overwrite: bool,
    labels: list[str],
):
    full_directories = [op.join(base_directory, d) for d in directories]
    for metric_group, metrics in chosen_grouped_metrics.items():
        simulation_results = ss.load_simulation_results(full_directories, metric_group)
        for metric in metrics:
            results = ss.compile_individual_data(
                simulation_results,
                metric,
            )
            filename = f"{filename_prefix}_{metric.replace(' ', '_')}"
            if not overwrite and op.exists(f"{filename}.xlsx"):
                i = 0
                while True:
                    if op.exists(f"{filename}_{i}.xlsx"):
                        i += 1
                    else:
                        with pd.ExcelWriter(f"{filename}_{i}.xlsx") as writer:
                            for label, df in zip(labels, results):
                                df.to_excel(writer, sheet_name=label, index=False)
                        break
            else:
                with pd.ExcelWriter(f"{filename}.xlsx") as writer:
                    for label, df in zip(labels, results):
                        df.to_excel(writer, sheet_name=label, index=False)
