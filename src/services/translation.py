from data.translations_data import METRICS_PT as MPT


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
        raise ValueError(f"Unsupported language: {language}")
