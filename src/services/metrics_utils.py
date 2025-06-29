from data.translations_data import METRICS_PT as MPT


def get_metric_root(metric: str) -> str:
    """
    Extracts the root of the metric from the given metric string.
    Args:
        metric (str): The metric string to extract the root from.
    Returns:
        str: The root of the metric.
    """
    return metric.split(" by ", 1)[0].strip()


def get_metrics_components(metrics: list[str], language: str) -> list[str]:
    """
    Extracts the components of the metrics from a list of metric strings.
    Args:
        metrics (list[str]): List of metric strings.
        language (str): The language code for translation.
    Returns:
        list[str]: List of components extracted from the metric strings.
    """
    components = []
    if language == "pt":
        separator = "por"
    elif language == "en":
        separator = "by"
    else:
        raise ValueError(f"Idioma não suportado: {language}")
    for metric in metrics:
        if separator in metric:
            components.append(get_metric_root(metric))
        else:
            components.append(metric)
    return components


def translate_metric(metric: str, language: str) -> str:
    """
    Translates a metric name to the specified language.

    Args:
        metric (str): The metric name to translate.
        language (str): The language code for translation ('pt' for Portuguese, 'en' for English).

    Returns:
        str: The translated metric name.
    """
    if language == "pt":
        return MPT.get(metric, metric)
    elif language == "en":
        return metric
    else:
        raise ValueError(f"Idioma não suportado: {language}")
