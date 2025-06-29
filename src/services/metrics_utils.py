def get_metric_root(metric: str) -> str:
    """
    Extracts the root of the metric from the given metric string.
    Args:
        metric (str): The metric string to extract the root from.
    Returns:
        str: The root of the metric.
    """
    return metric.split(" by ", 1)[0].strip()


def get_metrics_components(metrics: list[str]) -> list[str]:
    """
    Extracts the components of the metrics from a list of metric strings.
    Args:
        metrics (list[str]): List of metric strings.
    Returns:
        list[str]: List of components extracted from the metric strings.
    """
    components = []
    for metric in metrics:
        components.append(metric.split("by", 1)[1].strip())
    return components
