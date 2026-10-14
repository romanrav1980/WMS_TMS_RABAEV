from pathlib import Path
import json
j=json.loads(Path("tmp/wire292draft.json").read_text(encoding="utf-16"))
path="wiki-raw/wms_admin_ui_reference/interwarehouse.js";s=j[path]
needle='   el("iwUnitProfile").replaceChildren('
assert needle in s
s=s.replace(needle,'''   selectedUnitPanel.replaceChildren(...(source.display_units||source.units||[]).map(unit=>{
    const label=document.createElement("label"),box=document.createElement("input");box.type="checkbox";box.dataset.interwareUnitKey=unit.key;
    label.append(box,document.createTextNode(" Единица "+(unit.unit_id||unit.key.slice(0,12))+" · "+unit.quantity+" "+unit.base_uom));return label;
   }));
'''+needle,1)
needle='if(path==="/receive"&&unitScans.length)'
assert needle in s
s=s.replace(needle,'if(path==="/receive"&&el("iwPartialReceipt").checked){const selected=[...selectedUnitPanel.querySelectorAll("input:checked")].map(n=>n.dataset.interwareUnitKey);if(selected.length)body.unit_keys=selected;}'+needle,1)
s=s.replace('pending=null;unitScans=[];unitPlan="";','pending=null;busy=false;selectedUnitPanel.replaceChildren();unitScans=[];unitPlan="";')
j[path]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8")
needle='                result["profiles"] = '
position=s.index(needle);end=s.index('\n',position)
s=s[:end]+'''
                wire=q.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,json.dumps(result.get("units",[])))
                q.execute("""select u.PHYSICAL_UNIT_KEY,u.UNIT_ID,j.Q,j.B from
                    json_table(:unit_keys,'$[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j
                    join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=j.K order by u.PHYSICAL_UNIT_KEY""",unit_keys=wire)
                result["display_units"]=[{"key":r[0],"unit_id":r[1],"quantity":r[2],"base_uom":r[3]}for r in q.fetchall()]
'''+s[end:]
# The module already imports json; enforce the dependency explicitly if needed.
if "import json"not in s[:400]:s="import json\n"+s
j[p.as_posix()]=s
print(json.dumps(j,ensure_ascii=True))
