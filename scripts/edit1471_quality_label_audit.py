from pathlib import Path
p=Path('api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py');s=p.read_text(encoding='utf-8');needle='    return Response(quality_label_html(snapshot,user.username),media_type="text/html",';assert needle in s;s=s.replace(needle,'''    if (snapshot.get("weight_exemption",{}).get("eligible") is True
            and snapshot.get("weight_exemption_recorded") is not True):
        raise HTTPException(409,"Предъявите грузовое место к контролю, чтобы сохранить основание освобождения от веса.")
'''+needle);p.write_text(s,encoding='utf-8')
p=Path('api/wms_api_server/app/modules/inventory/domain/quality_label.py');s=p.read_text(encoding='utf-8');needle='    rows = "".join';assert needle in s;s=s.replace(needle,'''    exemption = snapshot.get("weight_exemption")
    if isinstance(exemption,Mapping) and exemption.get("eligible") is True:
        fields.extend([
            ("Освобождение от веса",exemption.get("exemption_basis","")),
            ("Исходная приёмка",exemption.get("receipt_operation_id","")),
            ("Основание сохранено", "Да" if snapshot.get("weight_exemption_recorded") is True else "Нет"),
        ])
'''+needle);p.write_text(s,encoding='utf-8')
p=Path('wiki-raw/wms_admin_ui_reference/outgoing-quality.js');s=p.read_text(encoding='utf-8');s=s.replace('data.required===false?"":" "+explain(data.weight_policy_reason)', 'data.required===false||data.weight_exemption?.eligible?"":" "+explain(data.weight_policy_reason)');p.write_text(s,encoding='utf-8')
