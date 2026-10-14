"""Print the current native QC snapshot; printing creates no stock or QC fact."""
from datetime import datetime, timezone
from html import escape
from typing import Any, Mapping
import re


def quality_label_html(snapshot: Mapping[str, Any], actor: str) -> str:
    signature = snapshot.get("composition_signature")
    versioned = isinstance(signature, str) and re.fullmatch(r"[A-F0-9]{64}", signature) is not None
    allowed = snapshot.get("ready") is True and versioned
    failed = snapshot.get("rescan_required") is True
    title = "КОНТРОЛЬ ПРОЙДЕН" if allowed else "КРАСНЫЙ ТЕГ: ПОВТОРНЫЙ КОНТРОЛЬ" if failed else "ДОПУСК НЕ ПОДТВЕРЖДЁН"
    color = "#16703a" if allowed else "#b00020"
    fields = [
        ("Идентификатор СТ", snapshot.get("shipment_identifier", "")),
        ("Режим контроля", snapshot.get("control_mode", "")),
        ("Подпись состава", signature if versioned else "Версионный состав отсутствует"),
        ("Основание", snapshot.get("reason", "")),
        ("Сформировал", actor),
        ("Сформировано, UTC", datetime.now(timezone.utc).isoformat(timespec="seconds")),
    ]
    rows = "".join(f"<dt>{escape(name)}</dt><dd>{escape(str(value))}</dd>" for name, value in fields)
    note = "Этикетка действует только для указанного состава. Изменение состава отзывает допуск; перед погрузкой система проверяет актуальное разрешение."
    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>Контроль СТ</title>
<style>@page{{size:100mm 150mm;margin:5mm}}body{{font:14px Arial,sans-serif;margin:0;color:#111}}
h1{{font-size:22px;border:4px solid {color};padding:8px;color:{color}}}dt{{font-weight:bold;margin-top:8px}}
dd{{margin:2px 0;overflow-wrap:anywhere}}footer{{margin-top:14px;font-size:11px}}@media print{{button{{display:none}}}}</style>
</head><body><h1>{title}</h1><dl>{rows}</dl><footer>{escape(note)}</footer>
<button type="button" onclick="window.print()">Печать</button></body></html>"""
