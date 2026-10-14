from pathlib import Path
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.html");s=p.read_text(encoding="utf-8").replace('<button id="iwDecisionSave">Сохранить решение</button>','''<label>Сообщение об ошибке<select id="iwIncidentKind"><option value="">Без нового сообщения</option><option value="TRANSPORT_DELAY">Задержка транспорта</option><option value="MISSING_PALLET">Отсутствует ожидаемая паллета</option><option value="IDENTIFIER_MISMATCH">Не совпадает идентификатор паллеты</option></select></label><label>Описание сообщения<input id="iwIncidentDetail" maxlength="1000"></label><label>Источник или номер акта<input id="iwIncidentEvidence" maxlength="200"></label><button id="iwDecisionSave">Сохранить решение и сообщение</button><button id="iwDecisionHistory">Показать историю выбранного плана</button><button id="iwDecisionHistoryMore" hidden>Следующие решения</button><div id="iwDecisionHistoryRows"></div>''',1);p.write_text(s,encoding="utf-8")
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('decisionPlans=[];','decisionPlans=[],historyPlan="",historyNext=null;',1)
s=s.replace('if(!body.expected_arrival||!body.reason||!body.decision_reference)throw Error','''if(el("iwIncidentKind").value){body.incident_kind=el("iwIncidentKind").value;body.incident_detail=el("iwIncidentDetail").value.trim();body.evidence_reference=el("iwIncidentEvidence").value.trim();if(!body.incident_detail||!body.evidence_reference)throw Error("Укажите описание ошибки и источник сообщения.");}
  if(!body.expected_arrival||!body.reason||!body.decision_reference)throw Error''',1)
# Reset history on authorization or warehouse change.
s=s.replace('el("iwRows").replaceChildren();','historyPlan="";historyNext=null;el("iwDecisionHistoryRows").replaceChildren();el("iwDecisionHistoryMore").hidden=true;el("iwRows").replaceChildren();')
s=s.replace('p.textContent=(r.temperature_decision?', 'p.textContent=(r.incident_kind?"Сообщение об ошибке: "+r.incident_detail+" · источник "+r.evidence_reference+". ":"")+(r.temperature_decision?',1)
anchor='el("iwIncomingLoad").addEventListener'
helper='''async function history(more=false){if(busy||pending)return;const plan=el("iwDecisionPlan").value,scope=key();if(!plan){say("Выберите план.");return;}if(more&&(historyPlan!==plan||historyNext===null))return;const after=more?historyNext:0;busy=true;controls();try{
 const result=await request("/plans/"+encodeURIComponent(plan)+"/decisions?after_revision="+after);if(scope!==key()||plan!==el("iwDecisionPlan").value)return;
 if(!more)el("iwDecisionHistoryRows").replaceChildren();
 for(const row of result.decisions){const p=document.createElement("p");p.textContent="Редакция "+row.revision_no+" · "+row.created_at+" · "+row.actor+" · "+(row.decision_kind==="WAIT"?"ожидать":"перенести")+" · рейс "+row.previous_tt_id+" → "+row.target_tt_id+" · "+row.reason_text+(row.incident_kind?" · сообщение: "+row.incident_detail+" / "+row.evidence_reference:"");el("iwDecisionHistoryRows").append(p);}
 historyPlan=plan;historyNext=result.next_after_revision;el("iwDecisionHistoryMore").hidden=!result.has_more;
 if(!result.decisions.length&&!more)say("Решений по плану пока нет.");
 }catch(e){if(scope===key())say(e.message);}finally{busy=false;controls();}}
 el("iwDecisionHistory").addEventListener("click",()=>history(false));el("iwDecisionHistoryMore").addEventListener("click",()=>history(true));
 el("iwDecisionPlan").addEventListener("change",()=>{historyPlan="";historyNext=null;el("iwDecisionHistoryRows").replaceChildren();el("iwDecisionHistoryMore").hidden=true;});
 '''
assert anchor in s;s=s.replace(anchor,helper+anchor,1)
p.write_text(s,encoding="utf-8")
