from pathlib import Path
import json
files={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py");s=p.read_text(encoding="utf-8")
s=s.replace('select CASE_PICK_TASK_ID,RESULT_JSON from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=:p_key','select CASE_PICK_TASK_ID,RESULT_JSON,CAPTURE_PURPOSE from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=:p_key')
old='                return read_oracle_json(row[1])'
new='''                result=read_oracle_json(row[1])
                q.execute("""select STOCK_OPERATION_ID from RRL_WH_SCALE_USE where CAPTURE_KEY=:p_key
                    union all select STOCK_OPERATION_ID from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key""",p_key=key)
                uses=q.fetchmany(2)
                if len(uses)>1:
                    raise WarehouseScaleError("SCALE_USAGE_AMBIGUOUS","Требуется сверка использования показания")
                return {**result,"capture_purpose":row[2],"used_operation_id":uses[0][0]if uses else None}'''
assert old in s;s=s.replace(old,new);files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/case-weighted-box.js");s=p.read_text(encoding="utf-8")
start=s.index('    if (task && line) cpTsdFetch("/api/inventory/warehouse-scales/captures?')
end=s.index('    for (const profile',start)
s=s[:start]+'    if(task&&line)window.cpScaleArchive.mount({panel,select,task,line,policy,isCurrent:()=>generation===currentGeneration});\n\n'+s[end:]
s=s.replace('panel.querySelectorAll("input")','panel.querySelectorAll("input[data-system][data-profile]")')
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/case-pick-tsd.html");s=p.read_text(encoding="utf-8").replace('<script src="case-weighted-box.js','<script src="case-scale-archive.js"></script><script src="case-weighted-box.js');files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/case-pick-guide.css");files[str(p)]=p.read_text(encoding="utf-8")+"""
#cpTsdWeightedBox{background:#fff;border:1px solid #dbe5ef;border-radius:12px;padding:16px;margin:12px 0}
#cpTsdWeightedBox[hidden]{display:none}
#cpTsdWeightedBox label{display:grid;gap:8px;margin:12px 0}
#cpTsdWeightedBox select,#cpTsdWeightedBox input{width:100%;box-sizing:border-box}
.cp-scale-tools{display:grid;gap:12px}.cp-scale-tools p{line-height:1.5;font-size:13px;overflow-wrap:anywhere}
.cp-scale-detail:not(:empty){border-left:4px solid #3985dc;padding:12px;background:#f0f7ff;border-radius:8px}
.cp-scale-tools details{border-top:1px solid #dbe5ef;padding-top:12px}.cp-scale-tools summary{min-height:32px;cursor:pointer}
"""
print(json.dumps(files,ensure_ascii=True))
