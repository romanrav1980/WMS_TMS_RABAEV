from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_final_qc")
p=f/"005_gate.sql";s=p.read_text(encoding="utf-8")
needle="   RRL_STOCK_QC_POLICY.settings_for_plan(domain,v_mode,v_independent);"
assert s.count(needle)==1
s=s.replace(needle,needle+"""
   declare dom json_object_t:=json_object_t.parse(domain);task_no number;required_flag number:=0;begin
    task_no:=dom.get_number('case_task');j.put('case_task_id',task_no);j.put('case_content_version',dom.get_number('case_version'));
    if task_no is not null then select case when p.FINAL_WEIGHT_REQUIRED=1 and upper(p.LOAD_UNIT_CLASS)='CONTAINER'then 1 else 0 end into required_flag
     from RRL_CASE_PICK_TASK c join RRL_PALLET_TYPE p on p.PALLET_TYPE_ID=c.PALLET_TYPE_ID where c.CASE_PICK_TASK_ID=task_no;end if;
    j.put('final_scale_required',required_flag=1);
   end;""");out[str(p)]=s
p=f/"004_qc.sql";s=p.read_text(encoding="utf-8")
needle="  j.put('failure_reason',v_reason);j.put('operation_id',op);"
assert s.count(needle)==1
s=s.replace(needle,"""  if m.has('final_scale_capture')then
   declare capture_json json_object_t;key_value varchar2(64):=m.get_string('final_scale_capture');wire clob;begin
    select RESULT_JSON into wire from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=key_value;capture_json:=json_object_t.parse(wire);
    j.put('final_scale_capture',key_value);j.put('final_scale_device_mode',capture_json.get_string('device_mode'));
    j.put('gross_weight_kg',capture_json.get_string('weight_kg'));j.put('tare_weight_kg',capture_json.get_string('tare_weight_kg'));j.put('net_weight_kg',capture_json.get_string('net_weight_kg'));
   end;
  end if;
"""+needle);out[str(p)]=s
out[str(f/"011_ui.sql")]="@@004_qc.sql\n@@005_gate.sql\n"
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/outgoing_quality.py");s=p.read_text(encoding="utf-8")
old='''                with self.gateway.transaction("Current warehouse QC status access")as q:
                    q.callproc("RRL_OUTGOING_QC_ACCESS.assert_identifier",[identifier,actor])
            rows = self.gateway.fetch_all('''
new='''                with self.gateway.transaction("Current warehouse QC status access")as q:
                    q.execute("set transaction read only")
                    q.callproc("RRL_OUTGOING_QC_ACCESS.assert_identifier",[identifier,actor])
                    q.execute("select RRL_STOCK_QC_GATE.status_json(:p_identifier) from dual",p_identifier=identifier)
                    return read_oracle_json(q.fetchone()[0])
            rows = self.gateway.fetch_all('''
assert old in s;s=s.replace(old,new)
s+="""

    def final_readings(self,identifier:str,actor:str)->dict:
        try:
            with self.gateway.transaction("Current QC whole CASE final scale readings")as q:
                q.execute("set transaction read only")
                q.callproc("RRL_OUTGOING_QC_ACCESS.assert_identifier",[identifier,actor])
                q.execute("select c.CASE_PICK_TASK_ID,c.CONTENT_VERSION from RRL_CASE_PICK_TASK c join RRL_SBORKA_PALLETS s on s.ID=c.LEGACY_SBORKA_PALLET_ID where s.PALLET_UID=:p_id",p_id=identifier)
                case=q.fetchone()
                if case is None:return {"items":[],"has_older":False,"use_by_capture":{}}
                q.execute("select c.RESULT_JSON,c.CAPTURE_KEY,u.STOCK_OPERATION_ID from(select RESULT_JSON,CAPTURE_KEY,RECEIVED_AT from RRL_WH_SCALE_CAPTURE where CASE_PICK_TASK_ID=:p_task and CAPTURE_PURPOSE='FINAL_GROSS' order by RECEIVED_AT desc,CAPTURE_KEY desc fetch first 51 rows only)c left join RRL_WH_FINAL_SCALE_USE u on u.CAPTURE_KEY=c.CAPTURE_KEY order by c.RECEIVED_AT desc,c.CAPTURE_KEY desc",p_task=case[0])
                rows=q.fetchall()
                return {"case_task_id":int(case[0]),"case_content_version":int(case[1]),"items":[read_oracle_json(row[0])for row in rows[:50]],"has_older":len(rows)>50,"use_by_capture":{row[1]:{"operation_id":row[2]}for row in rows[:50]if row[2]is not None}}
        except oracledb.DatabaseError as exc:
            error=exc.args[0]
            raise StockPostingError("FINAL_SCALE_READ_REJECTED"if 20800<=error.code<=20899 else"RESULT_UNCERTAIN","",error.code,str(error).split("\\n")[0])from exc
""";out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/outgoing_quality_routes.py");s=p.read_text(encoding="utf-8")
needle="    def check_final(self, identifier: str, body: dict, actor: str) -> dict: ..."
s=s.replace(needle,needle+"\n    def final_readings(self, identifier: str, actor: str) -> dict: ...")
s+="""

@router.get("/{identifier}/final-captures")
def final_readings(identifier:str=Path(min_length=1,max_length=150),
                   user:AdminUser=Depends(require_permission("outgoing_pallet_check")),
                   service:QualityPort=Depends(outgoing_quality_service))->dict:
    return service.final_readings(identifier,user.username)
""";out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/outgoing-quality.js");s=p.read_text(encoding="utf-8")
needle=' const el=k=>panel.querySelector'
pos=s.index(needle)
s=s[:pos]+""" const finalPanel=document.createElement("div");
 finalPanel.innerHTML='<h3>Финальное показание коробки</h3><p>Брутто и измеренная тара берутся из архива весового поста. Ручной ввод для этой коробки не применяется.</p><select data-final-capture aria-label="Финальное показание весов"></select><button data-final-refresh>Обновить показания</button>';
 panel.insertBefore(finalPanel,panel.querySelector("[role=status]"));finalPanel.hidden=true;
"""+s[pos:]
s=s.replace('let snapshot=null,pending=null,draft=null,busy=false,generation=0,identity="";','let snapshot=null,pending=null,draft=null,busy=false,generation=0,identity="",finalGeneration=0;')
needle=" function show(data){"
pos=s.index(needle)
s=s[:pos]+""" async function finalReadings(){
  const id=snapshot?.shipment_identifier,signature=snapshot?.composition_signature,gen=++finalGeneration;
  finalPanel.hidden=!snapshot?.final_scale_required;
  el("gross").disabled=Boolean(snapshot?.final_scale_required);el("tare").disabled=Boolean(snapshot?.final_scale_required);el("kind").disabled=Boolean(snapshot?.final_scale_required);
  el("final-capture").replaceChildren(new Option("Выберите актуальное показание",""));
  if(finalPanel.hidden||!id)return;
  try{
   const data=await call(path(id)+"/final-captures");
   if(gen!==finalGeneration||snapshot?.shipment_identifier!==id||snapshot?.composition_signature!==signature)return;
   for(const item of data.items||[]){
    if(item.case_content_version!==snapshot.case_content_version||item.composition_signature!==signature||data.use_by_capture?.[item.capture_key])continue;
    el("final-capture").append(new Option(item.measured_at+" / брутто "+item.weight_kg+" / тара "+item.tare_weight_kg+" / нетто "+item.net_weight_kg+" кг / "+(item.device_mode==="TEST"?"TEST: техническое показание":"HARDWARE"),item.capture_key));
   }
  }catch(error){if(gen===finalGeneration)message.textContent=error.message;}
 }
"""+s[pos:]
s=s.replace("  snapshot=data;el(\"marks\")","  snapshot=data;finalReadings();el(\"marks\")",1)
s=s.replace('finally{busy=false;panel.querySelectorAll("input,select,button").forEach(x=>x.disabled=false);}', 'finally{busy=false;panel.querySelectorAll("input,select,button").forEach(x=>x.disabled=false);el("gross").disabled=Boolean(snapshot?.final_scale_required);el("tare").disabled=Boolean(snapshot?.final_scale_required);el("kind").disabled=Boolean(snapshot?.final_scale_required);}')
needle='  }else{\n   const gross=el("gross")'
s=s.replace(needle,'  }else if(snapshot.final_scale_required){\n   if(!el("final-capture").value){message.textContent="Выберите актуальное архивное показание весового поста.";return;}\n   kind="final-weight";body.capture_key=el("final-capture").value;\n  }else{\n   const gross=el("gross")')
s=s.replace(' el("id").addEventListener("input",()=>{generation++;snapshot=null;});',' el("final-refresh").onclick=finalReadings;\n el("id").addEventListener("input",()=>{generation++;finalGeneration++;snapshot=null;finalPanel.hidden=true;});')
out[str(p)]=s
# TSD displays actual tare archive instead of asking workers to manufacture a scale packet.
p=Path("wiki-raw/wms_admin_ui_reference/case-sscc-label.js");s=p.read_text(encoding="utf-8")
s=s.replace("current=null;", "current=null,tareNote;",1)
s=s.replace('panel.append(issue,retry,print,scan,confirm,message);','tareNote=node("p");const tareRefresh=node("button","Обновить показание пустой тары");tareRefresh.onclick=refresh;panel.append(issue,retry,print,scan,confirm,message,tareNote,tareRefresh);')
needle='   message.textContent=data.issued?'
pos=s.index(needle)
s=s[:pos]+"""   const readings=await cpTsdFetch("/api/inventory/warehouse-scales/final-captures?task="+id);
   if(gen!==generation||id!==cpTsd.task?.case_pick_task_id)return;
   const tare=(readings.items||[]).find(item=>item.purpose==="EMPTY_TARE"&&item.scan_container===cpTsd.task.sscc);
   tareNote.textContent=tare?"Пустая тара измерена: "+tare.weight_kg+" кг / "+tare.device_mode+" / "+tare.measured_at:"До наполнения малой коробки измерьте её пустую тару на весовом посту и обновите показание.";
"""+s[pos:]
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
