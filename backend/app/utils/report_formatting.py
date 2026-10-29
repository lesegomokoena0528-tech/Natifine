import json
from datetime import date, datetime
from decimal import Decimal


def flatten_report_data(data):
    """Convert nested report data to section, metric, value rows."""
    rows = []

    def visit(value, section, metric):
        if isinstance(value, dict):
            if not value:
                rows.append((section or "Overview", metric, ""))
                return
            for key, child in value.items():
                child_metric = f"{metric} / {key}" if metric else str(key)
                visit(child, section or str(key), child_metric if section else "")
            return

        if isinstance(value, (list, tuple)):
            value = json.dumps(value, default=_json_default, ensure_ascii=False)
        elif isinstance(value, (datetime, date)):
            value = value.isoformat()

        rows.append((section or "Overview", metric or "Value", value))

    for key, value in data.items():
        if isinstance(value, dict):
            visit(value, str(key), "")
        else:
            visit(value, "Overview", str(key))

    return rows


def _json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def display_label(value):
    return str(value).replace("_", " ").strip().title()


def display_value(metric, value):
    if value is None:
        return "—"
    if isinstance(value, Decimal):
        value = float(value)
    if isinstance(value, (int, float)) and any(
        word in str(metric).lower()
        for word in ("revenue", "amount", "total paid")
    ):
        return f"R {value:,.2f}"
    return str(value)
