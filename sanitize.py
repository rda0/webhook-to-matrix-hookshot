from datetime import datetime
from typing import Dict, List, Tuple

from config import alert_default, incoming_default, reserved_labels, special_annotations


def get_unique_dict(source: Dict, common: Tuple[str]) -> Dict:
    """Filters out entries present in common keys"""
    return {k: v for k, v in source.items() if k not in common}


def get_common_time(alerts: List[Dict], key: str) -> str | None:
    """Return formatted timestamp if is common across alert instances"""
    unique_starts_at = {a[key] for a in alerts}
    if len(unique_starts_at) == 1:
        return unique_starts_at.pop()


def merge_with_default_dict(source_raw: Dict, default: Dict) -> Dict:
    """Merges source dict with default dict. Handles source_raw being None"""
    source = source_raw if isinstance(source_raw, dict) else dict()
    return default | source


def grafana_sanitize_incoming(incoming: Dict) -> Dict:
    sanitized = merge_with_default_dict(incoming, incoming_default)

    sanitized["commonLabels"] = merge_with_default_dict(
        sanitized["commonLabels"], reserved_labels
    )

    sanitized["commonAnnotations"] = merge_with_default_dict(
        sanitized["commonAnnotations"], special_annotations
    )

    sanitized["alerts"] = [
        grafana_sanitize_alert(
            alert,
            sanitized["commonLabels"].keys(),
            sanitized["commonAnnotations"].keys(),
        )
        for alert in incoming.get("alerts", [])
    ]

    firing_alerts = [a for a in sanitized["alerts"] if a["status"] == "firing"]
    sanitized["numberOfFiring"] = len(firing_alerts)

    for special_key in special_annotations.keys():
        sanitized[special_key] = sanitized["commonAnnotations"].get(special_key, "")

    sanitized["normalAnnotations"] = {
        k: v
        for k, v in sanitized["commonAnnotations"].items()
        if k not in special_annotations
    }
    sanitized["normalLabels"] = {
        k: v for k, v in sanitized["commonLabels"].items() if k not in reserved_labels
    }

    sanitized["commonStartsAtParsed"] = get_common_time(
        sanitized["alerts"], "startsAtParsed"
    )
    sanitized["commonEndsAtParsed"] = get_common_time(
        sanitized["alerts"], "endsAtParsed"
    )

    return sanitized


def grafana_sanitize_alert(
    alert: Dict, common_label_keys: Tuple[str], common_annotation_keys: Tuple[str]
) -> Dict:
    sanitized = alert_default | alert

    sanitized["values"] = merge_with_default_dict(sanitized["values"], dict())

    sanitized["uniqueLabels"] = get_unique_dict(sanitized["labels"], common_label_keys)
    sanitized["uniqueAnnotations"] = get_unique_dict(
        sanitized["annotations"], common_annotation_keys
    )

    sanitized["startsAtParsed"] = format_dt(sanitized.get("startsAt", ""))
    sanitized["endsAtParsed"] = format_dt(sanitized.get("endsAt", ""))

    return sanitized


def format_dt(dt_str: str) -> str:
    """
    Returns empty string if error or is year 1 e.g. zero value of golang time.Time
    see https://pkg.go.dev/time#Time
    """
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.year < 2:
            return ""
        return dt.strftime("%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        return ""
