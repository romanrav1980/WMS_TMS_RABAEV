from pathlib import Path
import json,re
files={}
p="api/wms_api_server/app/modules/inventory/contracts_waiting_tasks.py";t=Path(p).read_text(encoding="utf-8")
needle='    decision_operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")'
assert needle in t;t=t.replace(needle,needle+'\n    root_identifier: str | None=Field(default=None,min_length=1,max_length=200,pattern=r"^[^\\x00]+$")')
files[p]=t
p="api/wms_api_server/app/modules/inventory/infrastructure/st_defer_waiting.py";t=Path(p).read_text(encoding="utf-8")
t=t.replace("import oracledb", "import logging\nimport oracledb",1)
t=t.replace("class StDeferWaiting:",'_logger=logging.getLogger(__name__)\n\nclass StDeferWaiting:',1)
t=t.replace("request.decision_operation_id,actor,out])","request.decision_operation_id,actor,out,request.root_identifier])",1)
needle='            raise WaitingTaskError("ST_WAITING_PLAN_REJECTED" if status!=503 else "ST_WAITING_PLAN_UNCONFIRMED",'
assert needle in t
t=t.replace(needle,'''            if status==503:
                _logger.warning("ST waiting plan unconfirmed operation=%s oracle_code=%s",request.operation_id,code or None)
            if code==20886 and "DEFER_WAIT_ROOT_SELECTION_REQUIRED" in str(exc):
                raise WaitingTaskError("ST_WAITING_ROOT_SELECTION_REQUIRED","Choose a top place before planning",409) from exc
'''+needle)
needle='            return {"decision_operation_id":decision,'
assert needle in t;t=t.replace(needle,'''            places_out=cur.var(oracledb.DB_TYPE_CLOB)
            cur.callproc("RRL_ST_DEFER_WAIT_API.read_places",[decision,actor,places_out])
            places=read_oracle_json(places_out.getvalue())
            return {"available_places":places.get("places",[]),"selection_required":places.get("selection_required",False),
                    "places_unavailable_reason":places.get("unavailable_reason"),
                    "decision_operation_id":decision,''',1)
files[p]=t
p="wiki-raw/wms_admin_ui_reference/st-waiting-tasks.js";t=Path(p).read_text(encoding="utf-8")
t=t.replace("shownDecision=null,rows=[];","shownDecision=null,rows=[],places=[],selectionRequired=false;",1)
old="if(keys.length!==2||!keys.includes('operation_id')||!keys.includes('decision_operation_id')||"
new="if(![2,3].includes(keys.length)||keys.some(k=>!['operation_id','decision_operation_id','root_identifier'].includes(k))||!keys.includes('operation_id')||!keys.includes('decision_operation_id')||\n   (keys.includes('root_identifier')&&(typeof body.root_identifier!=='string'||!body.root_identifier.length||body.root_identifier.length>200||body.root_identifier.includes('\\u0000')))||"
assert old in t;t=t.replace(old,new,1)
t=t.replace("el('swPlan').disabled=busy||!!p||!selected;", "el('swPlan').disabled=busy||loading||!!p||!selected||(selectionRequired&&!el('swRoot').value);el('swRoot').disabled=busy||loading||!!p;")
pos=t.index(" async function request(")
functions=""" function renderPlaces(){
  const chosen=el('swRoot').value;el('swRoot').replaceChildren();
  const empty=document.createElement('option');empty.value='';empty.textContent=selectionRequired?'Выберите одно верхнее место':'По действующему составу СТ';el('swRoot').appendChild(empty);
  for(const place of places){
   const option=document.createElement('option');option.value=place.root_identifier;option.disabled=!place.available;
   const label=place.place_kind==='CASE'?'CASE':'HU';
   option.textContent=label+' '+place.root_identifier+(place.cell?' · '+place.cell:'')+
    (place.planned_task_id?' · задание #'+place.planned_task_id:!place.available?' · требуется разбор':!place.move_required?' · уже в ожидании':'');
   el('swRoot').appendChild(option);
  }
  if(places.some(p=>p.root_identifier===chosen&&p.available))el('swRoot').value=chosen;
  else if(places.length===1&&places[0].available&&selectionRequired)el('swRoot').value=places[0].root_identifier;
  el('swRootHint').textContent=selectionRequired?'Каждое верхнее место получает своё задание. Выберите место; состав и принадлежность проверит WMS.':
   'Для нескольких контейнеров выбирается конкретное место. Самостоятельные CASE можно запланировать прежним общим действием.';
 }
"""
t=t[:pos]+functions+t[pos:]
t=t.replace("if(!response.ok)throw Error(result.detail?.message||'Операция не подтверждена.');", "if(!response.ok){const error=Error(result.detail?.code==='ST_WAITING_ROOT_SELECTION_REQUIRED'?'Выберите конкретное верхнее место.':result.detail?.message||'Операция не подтверждена.');error.code=result.detail?.code;throw error;}",1)
needle="next=result.next_after_task_id;shownDecision=decision;render();"
assert t.count(needle)>=1
t=t.replace(needle,"next=result.next_after_task_id;shownDecision=decision;places=result.available_places||[];selectionRequired=result.selection_required===true;renderPlaces();render();")
t=t.replace("if(busy)return;const identity=scope(),savedKey=key();let intent;", "if(busy)return;const identity=scope(),savedKey=key();let intent,firstAttempt=false;",1)
needle="const body={operation_id:'STWAIT:'+crypto.randomUUID(),decision_operation_id:decision};"
assert needle in t
t=t.replace(needle,"""if(selectionRequired&&!el('swRoot').value)throw Error('Выберите конкретное верхнее место.');
    const body={operation_id:'STWAIT:'+crypto.randomUUID(),decision_operation_id:decision};
    if(el('swRoot').value)body.root_identifier=el('swRoot').value;firstAttempt=true;""",1)
t=t.replace("result.stock_changed!==false||!Array.isArray(result.tasks)", "(intent.body.root_identifier&&result.root_identifier!==intent.body.root_identifier)||result.stock_changed!==false||!Array.isArray(result.tasks)",1)
needle="}catch(e){if(identity===scope())el('swMessage').textContent=e.message+' Исходную команду можно повторить.';}"
assert needle in t
t=t.replace(needle,"""}catch(e){
   if(identity===scope()&&firstAttempt&&e.code==='ST_WAITING_ROOT_SELECTION_REQUIRED'&&localStorage.getItem(savedKey)===intent.raw){
    localStorage.removeItem(savedKey);await read();if(identity===scope())el('swMessage').textContent='Выберите верхнее место. Новый план не был создан.';
   }else if(identity===scope())el('swMessage').textContent=e.message+' Исходную команду можно повторить.';
  }""",1)
t=t.replace("shownDecision=null;rows=[];el('swRows')", "shownDecision=null;rows=[];places=[];selectionRequired=false;renderPlaces();el('swRows')",1)
t=t.replace(" el('swDecision').addEventListener('input'", " el('swRoot').addEventListener('change',controls);\n el('swDecision').addEventListener('input'",1)
files[p]=t
p="wiki-raw/wms_admin_ui_reference/day-reconciliation.html";t=Path(p).read_text(encoding="utf-8")
needle='<button id="swRead">Обновить задания</button>';assert needle in t
t=t.replace(needle,'<label>Грузовое место<select id="swRoot"><option value="">По действующему составу СТ</option></select></label>'+needle,1)
t=t.replace('<p id="swPending"', '<p id="swRootHint" class="waiting-place-hint">Для нескольких контейнеров выберите верхнее место после обновления.</p><p id="swPending"',1)
t=t.replace('id="swPlan">Создать задания','id="swPlan">Создать план ожидания',1)
t=re.sub(r'st-waiting-tasks.js(?:\?v=[^"]+)?','st-waiting-tasks.js?v=20261013-1078',t)
files[p]=t
# Reuse the existing waiting workspace stylesheet.
paths=list(Path("wiki-raw/wms_admin_ui_reference").glob("*waiting*.css"))
if paths:
 p=str(paths[0]).replace("\\","/")
 files[p]=Path(p).read_text(encoding="utf-8")+"\n#swRoot{min-width:220px;max-width:360px;width:100%;padding:10px;border:1px solid #d9e4f2;border-radius:8px;background:#fff;color:#264467}.waiting-place-hint{font-size:13px;color:#63758e;line-height:1.6}\n"
print(json.dumps(files,ensure_ascii=True))
