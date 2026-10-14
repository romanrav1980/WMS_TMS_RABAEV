from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_group_read.py');t=p.read_text(encoding='utf-8')
needle='            state=q.fetchone()'
add='''            state=q.fetchone()
            q.execute("""select c.OPERATION_ID,o.RESULT_JSON from RRL_IW_GROUP_CUSTODY c
                left join RRL_IW_GROUP_ONWARD o on o.RECEIPT_OPERATION_ID=c.RECEIPT_OPERATION_ID
                join RRL_IW_GROUP_RECEIPT r on r.OPERATION_ID=c.RECEIPT_OPERATION_ID where r.PLAN_OPERATION_ID=:plan_id""",plan_id=plan)
            onward=q.fetchone()
            q.execute("""select count(distinct d.ST_ID),count(distinct d.OPERATION_ID),
                count(distinct case when shop.STATUS='ACCEPTED'then d.ST_ID end)
                from RRL_IW_GROUP_DISPATCH d join RRL_IW_GROUP_RECEIPT r on r.OPERATION_ID=d.RECEIPT_OPERATION_ID
                left join RRL_STORE_RECEIPT_FACT shop on shop.LOAD_OPERATION_ID=d.OPERATION_ID
                where r.PLAN_OPERATION_ID=:plan_id""",plan_id=plan)
            loaded_members,load_count,accepted_members=q.fetchone()
'''
assert needle in t;t=t.replace(needle,add,1)
t=t.replace('                        grouped_receipt_available=True,stock_changed=False)','''                        custody_operation_id=onward[0]if onward else None,
                        onward=read_oracle_json(onward[1])if onward and onward[1]else None,
                        loaded_members=loaded_members,load_count=load_count,accepted_members=accepted_members,
                        delivered=accepted_members==len(lots),grouped_receipt_available=True,stock_changed=False)''',1)
out[p.as_posix()]=t
p=Path('wiki-raw/wms_admin_ui_reference/interwarehouse-groups.html');t=p.read_text(encoding='utf-8')
section='''<section class="panel" data-permission="interwarehouse_receive"><h2>Передача ответственности</h2><p>После полной приёмки и размещения подтвердите передачу груза принимающему складу.</p><button id="ggCustody">Завершить ответственность первого плеча</button></section>
<section class="panel" data-permission="outgoing_pallet_edit"><h2>Подготовка второго плеча</h2><label>Основание<textarea id="ggOnwardReason" maxlength="500"></textarea></label><label>Документ<input id="ggOnwardReference" maxlength="60"></label><button id="ggOnward">Подготовить СТ всех товаров</button><div id="ggOnwardResult"></div><p>Назначьте подготовленные СТ на указанный рейс, пройдите выходной контроль и погрузите целое место через существующий процесс отгрузки.</p></section>
'''
t=t.replace('<section class="panel"><button id="ggRetry"',section+'<section class="panel"><button id="ggRetry"',1)
out[p.as_posix()]=t
p=Path('wiki-raw/wms_admin_ui_reference/interwarehouse-groups.js');t=p.read_text(encoding='utf-8')
t=t.replace('el("ggState").textContent=result.target_cell?','el("ggState").textContent=result.delivered?"Принято покупателем":result.loaded_members===result.lots.length?"Все товары погружены на второе плечо":result.target_cell?',1)
needle=' taskLink(result.placement_task_id);restoreScans();'
t=t.replace(needle,''' if(result.onward)el("ggOnwardResult").textContent=result.onward.members.map(m=>"СТ "+m.st_number+" · "+m.article+" "+m.quantity+" "+m.base_uom+" · рейс "+m.target_trip_id).join(" / ");
 else el("ggOnwardResult").textContent="";
 taskLink(result.placement_task_id);restoreScans();''',1)
needle='el("ggRetry").addEventListener'
addition='''el("ggCustody").addEventListener("click",async()=>{try{
 planId();if(!detail.receipt_operation_id)throw Error("Сначала подтвердите приёмку");
 await post("/release-custody",{operation_id:op("CUSTODY"),receipt_operation_id:detail.receipt_operation_id});
}catch(e){status(e.message);}});
el("ggOnward").addEventListener("click",async()=>{try{
 planId();if(!detail.custody_operation_id)throw Error("Подтвердите передачу ответственности");
 const reason=el("ggOnwardReason").value.trim(),reference=el("ggOnwardReference").value.trim();if(!reason||!reference)throw Error("Укажите основание и документ");
 await post("/group-onward",{operation_id:op("ONWARD"),receipt_operation_id:detail.receipt_operation_id,reason,decision_reference:reference});
}catch(e){status(e.message);}});
'''+needle
t=t.replace(needle,addition,1)
out[p.as_posix()]=t
print(json.dumps(out))
