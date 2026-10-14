import json
from pathlib import Path
out={}
p=Path("db/migrations/2026-10-11_ni042_weight_box_capture/002_decoder.sql");s=p.read_text(encoding="utf-8")
s=s.replace("and(p_gtin is null or p_gtin in(lpad(a.BARCODE_SHT,14,'0'),lpad(a.BARCODE_KOR,14,'0'),lpad(a.BARCODE_BL,14,'0')));","""and(p_gtin is null
    or (regexp_like(a.BARCODE_SHT,'^([0-9]{8}|[0-9]{12}|[0-9]{13}|[0-9]{14})$','c')and p_gtin=lpad(a.BARCODE_SHT,14,'0'))
    or (regexp_like(a.BARCODE_KOR,'^([0-9]{8}|[0-9]{12}|[0-9]{13}|[0-9]{14})$','c')and p_gtin=lpad(a.BARCODE_KOR,14,'0'))
    or (regexp_like(a.BARCODE_BL,'^([0-9]{8}|[0-9]{12}|[0-9]{13}|[0-9]{14})$','c')and p_gtin=lpad(a.BARCODE_BL,14,'0')));""");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py");s=p.read_text(encoding="utf-8")
s=s.replace('            if weighted:\n                cursor.callproc("RRL_WEIGHT_BOX_READ.assert_sku", [articul, None])','            if weighted:\n                assert_weighted_sku(cursor, articul)')
s+='''

def assert_weighted_sku(cursor, article: str) -> None:
    try:
        cursor.callproc("RRL_WEIGHT_BOX_READ.assert_sku", [article, None])
    except oracledb.DatabaseError as exc:
        if exc.args[0].code == 20886:
            raise ValueError("Serialized weight boxes require a weighted SKU and a KG base policy.") from exc
        raise
''';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/master_data/api/routes.py");s=p.read_text(encoding="utf-8");s+='''    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
''';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/birth_capture.py");s=p.read_text(encoding="utf-8").replace("Unique unit capture is required for marked lot ","Physical unit capture is required for this lot ");out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/finished-goods.html");s=p.read_text(encoding="utf-8").replace('<label><input id="fgReceiptMarked" type="checkbox" /> Товар подлежит маркировке</label>','<label><input id="fgReceiptMarked" type="checkbox" /> Товар подлежит маркировке</label>\n            <label><input id="fgReceiptWeightedBoxes" type="checkbox" /> Серийные весовые коробки (KG, GS1)</label>\n            <p class="muted">Масса нетто и серийный номер считываются с этикетки коробки. Требование государственной маркировки настраивается отдельно.</p>').replace('sku-receiving-policy.js?v=20261007-ni01','sku-receiving-policy.js?v=20261011-weighted-boxes');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/sku-receiving-policy.js");s=p.read_text(encoding="utf-8").replace('      el("fgReceiptMarked").checked = data.marking_required;','      el("fgReceiptMarked").checked = data.marking_required;\n      el("fgReceiptWeightedBoxes").checked = Boolean(data.serialized_weight_boxes);').replace('marking_required: marked, profiles','marking_required: marked, serialized_weight_boxes: el("fgReceiptWeightedBoxes").checked, profiles');out[str(p)]=s
print(json.dumps(out,ensure_ascii=False))
