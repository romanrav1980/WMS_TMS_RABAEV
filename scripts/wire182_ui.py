from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/case_pick_policy.py");s=p.read_text(encoding="utf-8").replace('select l.ARTICUL,','select l.ARTICUL,nvl((select SERIALIZED_WEIGHT_BOXES from RRL_SKU_RECEIPT_POLICY p where p.ARTICUL=l.ARTICUL),0) SERIALIZED_WEIGHT_BOXES,')
s=s.replace('"profiles": profiles}','"profiles": profiles, "serialized_weight_boxes": bool(rows[0]["serialized_weight_boxes"])}');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/weighted_case_routes.py");s=p.read_text(encoding="utf-8").replace('"message": str(exc)}','"message": str(exc), "outcome_confirmed": True, "retry_same_operation_id": False}');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/case-pick-posting.js");s=p.read_text(encoding="utf-8")
s=s.replace('let busy = false, policyGeneration = 0;','let busy = false, policyGeneration = 0, currentPolicy = null;')
s=s.replace('    profile.replaceChildren();cpTsdEl("cpTsdMarking").hidden = true;','    currentPolicy = null;\n    profile.replaceChildren();cpTsdEl("cpTsdMarking").hidden = true;\n    window.cpWeightedBox.show({serialized_weight_boxes:false,profiles:[]});')
s=s.replace('        if(generation !== policyGeneration)return;','        if(generation !== policyGeneration)return;\n        currentPolicy = policy; window.cpWeightedBox.show(policy);')
s=s.replace('        const quantity=cpTsdEl("cpTsdFactQty").value.trim();','        if(!currentPolicy)throw new Error("Дождитесь загрузки настроек товара.");\n        const weighted = Boolean(currentPolicy.serialized_weight_boxes);\n        const quantity=cpTsdEl("cpTsdFactQty").value.trim();')
s=s.replace('if(!/^[0-9]{1,18}([.][0-9]{1,9})?$/.test(quantity))','if(!weighted && !/^[0-9]{1,18}([.][0-9]{1,9})?$/.test(quantity))')
s=s.replace('        const payload={operation_id:','        let payload={operation_id:')
s=s.replace('        intent={task:task.case_pick_task_id,line:line.case_pick_line_id,payload};','        if(weighted)payload=window.cpWeightedBox.payload(payload.operation_id,payload.scan_cell,payload.scan_container);\n        intent={task:task.case_pick_task_id,line:line.case_pick_line_id,route:weighted?"weighted-box":"confirm",payload};')
s=s.replace('+intent.line+"/confirm"', '+intent.line+"/"+(intent.route||"confirm")')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/case-pick-tsd.html");s=p.read_text(encoding="utf-8").replace('          <label>Факт<input','          <div id="cpTsdWeightedBox" hidden></div>\n          <label>Факт<input').replace('<script src="case-pick-posting.js"></script>','<script src="case-weighted-box.js?v=20261011"></script>\n    <script src="case-pick-posting.js?v=20261011-weighted"></script>');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
