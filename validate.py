from datetime import datetime
from typing import Dict

# https://grafana.com/docs/grafana-cloud/alerting-and-irm/alerting/configure-notifications/manage-contact-points/integrations/webhook-notifier/


def validate_str_entry(d: Dict, k: str):
    """Empty string if not exists"""
    d[k] = d.get(k, "")


def validate_number_entry(d: Dict, k: str):
    """0 if not exists"""
    d[k] = d.get(k, 0)


def validate_dict_entry(d: Dict, k: str):
    """Empty dict if not exists"""
    entry = d.get(k, None)
    if not isinstance(entry, dict):
        entry = dict()
    d[k] = entry


def grafana_validate_incoming(incoming: Dict):
    """
    Makes sure the necessary keys are present in the incoming dict so it can be parsed by jinja
    """
    string_keys = ("receiver", "status", "externalUrl", "version", "groupKey")
    for key in string_keys:
        validate_str_entry(incoming, key)

    validate_number_entry(incoming, "orgId")
    validate_number_entry(incoming, "truncatedAlerts")

    validate_dict_entry(incoming, "groupLabels")
    validate_dict_entry(incoming, "commonLabels")
    validate_dict_entry(incoming, "commonAnnotations")

    incoming["alerts"] = alerts = incoming.get("alerts", [])

    for alert in alerts:  # Handle non dict values?
        grafana_validate_alert(alert)

    l = lambda a: a.get("status", "") == "firing"
    incoming["no_firing"] = len(tuple(filter(l, alerts)))


def grafana_validate_alert(alert: Dict):

    string_keys = (
        "status",
        "startsAt",
        "endsAt",
        "generatorURL",
        "fingerprint",
        "silenceURL",
        "imageURL",
    )
    for key in string_keys:
        validate_str_entry(alert, key)

    validate_dict_entry(alert, "labels")
    validate_dict_entry(alert, "annotations")
    validate_dict_entry(alert, "values")

    # fixes "values" being shadowed in jinja
    alert["valuesForJinja"] = alert.get("values", None)

    alert["startsAtParsed"] = format_dt(alert.get("startsAt", ""))
    alert["endsAtParsed"] = format_dt(alert.get("endsAt", ""))


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
