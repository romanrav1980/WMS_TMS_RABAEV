import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/master_data/contracts.py");s=p.read_text(encoding="utf-8")
s=s.replace("    marking_required: bool\n","    marking_required: bool\n    serialized_weight_boxes: bool | None = None\n");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py");s=p.read_text(encoding="utf-8")
s=s.replace("p.POLICY_VERSION, p.MARKING_REQUIRED,","p.POLICY_VERSION, p.MARKING_REQUIRED, p.SERIALIZED_WEIGHT_BOXES,")
s=s.replace('"profiles": profiles,','"profiles": profiles,\n                "serialized_weight_boxes": bool(row["serialized_weight_boxes"] or 0),',1)
s=s.replace("select POLICY_VERSION from RRL_SKU_RECEIPT_POLICY","select POLICY_VERSION,SERIALIZED_WEIGHT_BOXES from RRL_SKU_RECEIPT_POLICY")
s=s.replace('            params = {"a": articul,', '''            weighted = bool(old[1]) if request.serialized_weight_boxes is None and old else bool(request.serialized_weight_boxes)
            if weighted:
                cursor.callproc("RRL_WEIGHT_BOX_READ.assert_sku", [articul, None])
            params = {"w": int(weighted), "a": articul,''')
s=s.replace("MARKING_REQUIRED=:m,","MARKING_REQUIRED=:m,SERIALIZED_WEIGHT_BOXES=:w,")
s=s.replace("(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_AT,UPDATED_BY)","(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES,UPDATED_AT,UPDATED_BY)")
s=s.replace("values (:a,:v,:m,systimestamp,:actor)","values (:a,:v,:m,:w,systimestamp,:actor)")
s=s.replace('payload = {"marking_required": request.marking_required,','payload = {"marking_required": request.marking_required,"serialized_weight_boxes": weighted,')
s=s.replace('"marking_required": request.marking_required,\n                "profiles":','"marking_required": request.marking_required,"serialized_weight_boxes": weighted,\n                "profiles":')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receiving_marks.py");s=p.read_text(encoding="utf-8")
s=s.replace("select POLICY_VERSION,MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY","select POLICY_VERSION,MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES from RRL_SKU_RECEIPT_POLICY")
s=s.replace("        if not policy[1]:","""        if payload.get("weighted_boxes") or policy[2]:
            from .weighted_box_capture import resolve_weighted_boxes
            return resolve_weighted_boxes(cur, articul, quantity, payload, base_uom, policy)
        if not policy[1]:""",1)
s=s.replace("        if marks.get('units'):assert_current_mark_policy(cur,pallet,marks)","""        if marks.get("weighted_boxes"):
            from .weighted_box_capture import assert_current_weighted_policy
            assert_current_weighted_policy(cur, pallet, marks)
        elif marks.get('units'):assert_current_mark_policy(cur,pallet,marks)""")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/birth_capture.py");s=p.read_text(encoding="utf-8")
s=s.replace('        if not marked:\n','''        cursor.execute("select nvl(max(SERIALIZED_WEIGHT_BOXES),0) from RRL_SKU_RECEIPT_POLICY where ARTICUL=:p_article",p_article=article)
        weighted=cursor.fetchone()[0]
        if not marked and not weighted:
''',1)
s=s.replace('bindings.append({"unit_id":unit_id,"key":sha256(min(identities).encode()).hexdigest(),',
'''physical_identity=("GS1_WEIGHT_BOX:"+unit_id) if marks.get("weighted_boxes") else min(identities)
            bindings.append({"unit_id":unit_id,"key":sha256(physical_identity.encode()).hexdigest(),''')
out[str(p)]=s
print(json.dumps(out))
