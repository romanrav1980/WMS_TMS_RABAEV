from pathlib import Path
import json
d=Path("db/migrations/2026-10-11_ni061_recovery_cancel");out={}
def put(n,s):out[(d/n).as_posix()]=s
put("001_schema.sql","""declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_IW_RECOVERY_CANCEL';
 if n=0 then execute immediate 'create table RRL_IW_RECOVERY_CANCEL(
 OPERATION_ID varchar2(100)primary key,REQUEST_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECOVERY_REQUEST(OPERATION_ID),
 LOSS_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_SHORTAGE_FACT(OPERATION_ID),WARE_ID number not null,
 BASE_QTY number not null check(BASE_QTY>0),BASE_UOM varchar2(20)not null,ACTOR varchar2(100)not null,
 REASON_TEXT varchar2(500 CHAR)not null,EVIDENCE_REFERENCE varchar2(255 CHAR)not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null)';end if;
end;
/
""")
put("002_cancel.sql","""create or replace package RRL_STOCK_IW_RECOVERY_CANCEL authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure assert_scope(p_request varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_IW_RECOVERY_CANCEL as
 procedure assert_scope(p_request varchar2,p_actor varchar2)is req RRL_INTERWARE_RECOVERY_REQUEST%rowtype;n number;approved number;
 begin
 select *into req from RRL_INTERWARE_RECOVERY_REQUEST where OPERATION_ID=p_request;
 select count(*)into approved from RRL_INTERWARE_RECOVERY_APPROVAL where REQUEST_OPERATION_ID=p_request;
 select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=req.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
 and RRL_HAS_WRIGHT(u.ID,'store_return_approve')=1;
 if n!=1 or(approved>0 and req.ACTOR=p_actor)then raise_application_error(-20882,'RECOVERY_CANCEL_CURRENT_INDEPENDENT_CONTROLLER_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20886,'RECOVERY_CANCEL_REQUEST_REQUIRED');end;
 procedure describe(p_request clob,p_actor varchar2,p_domain out json_object_t)is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');req_id varchar2(100):=d.get_object('source').get_string('request_operation_id');
 req RRL_INTERWARE_RECOVERY_REQUEST%rowtype;n number;reason varchar2(2000):=m.get_string('reason');ref varchar2(2000):=m.get_string('evidence_reference');source json_object_t;
 begin
 assert_scope(req_id,p_actor);select *into req from RRL_INTERWARE_RECOVERY_REQUEST where OPERATION_ID=req_id;
 if m.get_size!=3 or trim(reason)is null or length(trim(reason))<8 or length(reason)>500 or trim(ref)is null or length(ref)>255
 or RRL_STOCK_MATH.quantity(m.get_string('quantity'))!=req.BASE_QTY then raise_application_error(-20886,'RECOVERY_CANCEL_EXACT_REQUEST_REASON_EVIDENCE_REQUIRED');end if;
 select count(*)into n from RRL_IW_RECOVERY_CANCEL where REQUEST_OPERATION_ID=req_id;if n!=0 then raise_application_error(-20886,'RECOVERY_REQUEST_ALREADY_CANCELLED');end if;
 select count(*)into n from RRL_INTERWARE_RECOVERY_APPROVAL approved join RRL_INTERWARE_RECOVERY_RECEIPT received on received.APPROVAL_OPERATION_ID=approved.OPERATION_ID
 where approved.REQUEST_OPERATION_ID=req_id;if n!=0 then raise_application_error(-20886,'RECOVERY_PHYSICALLY_RECEIVED_CANNOT_CANCEL');end if;
 source:=json_object_t.parse(req.SOURCE_JSON);
 p_domain:=json_object_t();p_domain.put('request_operation_id',req_id);p_domain.put('loss_operation_id',req.LOSS_OPERATION_ID);
 p_domain.put('warehouse_id',req.WARE_ID);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(req.BASE_QTY));p_domain.put('base_uom',req.BASE_UOM);
 p_domain.put('source_units',source.get_array('source_units'));p_domain.put('reason',reason);p_domain.put('evidence_reference',ref);
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;u json_object_t;begin
 describe(p_request,d.get_string('actor'),v);RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_SHORTAGE_FACT',v.get_string('loss_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECOVERY_REQUEST',v.get_string('request_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_IW_RECOVERY_CANCEL',v.get_string('request_operation_id'));
 a:=v.get_array('source_units');for i in 0..a.get_size-1 loop u:=treat(a.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',u.get_string('key'));end loop;
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');wire clob;v json_object_t;fresh json_object_t;
 req_id varchar2(100);loss_id varchar2(100);ware number;qty number;uom varchar2(20);reason varchar2(2000);ref varchar2(2000);begin
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(wire).get_object('domain');
 describe(p_request,p_actor,fresh);if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'RECOVERY_CANCEL_SOURCE_CHANGED');end if;
 req_id:=v.get_string('request_operation_id');loss_id:=v.get_string('loss_operation_id');ware:=v.get_number('warehouse_id');qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
 uom:=v.get_string('base_uom');reason:=v.get_string('reason');ref:=v.get_string('evidence_reference');wire:=v.to_clob;
 insert into RRL_IW_RECOVERY_CANCEL(OPERATION_ID,REQUEST_OPERATION_ID,LOSS_OPERATION_ID,WARE_ID,BASE_QTY,BASE_UOM,ACTOR,REASON_TEXT,EVIDENCE_REFERENCE,SOURCE_JSON)
 values(op,req_id,loss_id,ware,qty,uom,p_actor,reason,ref,wire);
 v.put('operation_id',op);v.put('status','RECOVERY_CANCELLED');v.put('stock_changed',false);v.put('historical_loss_preserved',true);v.put('quantity_restored_to_unreported',v.get_string('quantity'));p_result:=v.to_clob;end;
end;
/
""")
put("003_guard.sql","""create or replace trigger RRL_IW_REC_CANCEL_G before insert or update or delete on RRL_IW_RECOVERY_CANCEL for each row
begin
 if updating or deleting then raise_application_error(-20863,'RECOVERY_CANCELLATION_IMMUTABLE');end if;
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'INTERWARE_RECOVERY_CANCEL');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_RECOVERY_CANCEL',:new.REQUEST_OPERATION_ID));
end;
/
""")
p=Path("db/migrations/2026-10-11_ni061_partial_recovery/002_decisions_current.sql");s=p.read_text(encoding="utf-8")
s=s.replace("from RRL_INTERWARE_RECOVERY_REQUEST where LOSS_OPERATION_ID=loss_id;","""from RRL_INTERWARE_RECOVERY_REQUEST candidate where LOSS_OPERATION_ID=loss_id and not exists(
 select 1 from RRL_IW_RECOVERY_CANCEL cancelled join RRL_STOCK_OPERATION cancel_op on cancel_op.OPERATION_ID=cancelled.OPERATION_ID
 where cancelled.REQUEST_OPERATION_ID=candidate.OPERATION_ID and cancel_op.STATE='APPLIED'and cancel_op.COMMAND_TYPE='INTERWARE_RECOVERY_CANCEL');""",1)
# Bound includes historical cancelled reports, not only active allocation.
needle="  if request_count>=1000"
s=s.replace(needle,"  select count(*)into request_count from RRL_INTERWARE_RECOVERY_REQUEST where LOSS_OPERATION_ID=loss_id;\n"+needle,1)
needle="  if quantity!=req.BASE_QTY"
s=s.replace(needle,"  select count(*)into n from RRL_IW_RECOVERY_CANCEL where REQUEST_OPERATION_ID=req_id;if n!=0 then raise_application_error(-20886,'RECOVERY_REQUEST_CANCELLED');end if;\n"+needle,1)
s=s.replace("and allocated.K=frozen.K);","""and allocated.K=frozen.K and not exists(select 1 from RRL_IW_RECOVERY_CANCEL cancelled
 join RRL_STOCK_OPERATION cancel_op on cancel_op.OPERATION_ID=cancelled.OPERATION_ID
 where cancelled.REQUEST_OPERATION_ID=claimed.OPERATION_ID and cancel_op.STATE='APPLIED'and cancel_op.COMMAND_TYPE='INTERWARE_RECOVERY_CANCEL'));""",1)
s=s.replace("and allocated.K=j.K);","""and allocated.K=j.K and not exists(select 1 from RRL_IW_RECOVERY_CANCEL cancelled
 join RRL_STOCK_OPERATION cancel_op on cancel_op.OPERATION_ID=cancelled.OPERATION_ID
 where cancelled.REQUEST_OPERATION_ID=claimed.OPERATION_ID and cancel_op.STATE='APPLIED'and cancel_op.COMMAND_TYPE='INTERWARE_RECOVERY_CANCEL'));""",1)
put("004_decisions_current.sql",s)
s=Path("db/migrations/2026-10-11_ni061_partial_recovery/003_receiving_current.sql").read_text(encoding="utf-8")
needle=" select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=req.RECEIPT_OPERATION_ID;"
s=s.replace(needle," select count(*)into n from RRL_IW_RECOVERY_CANCEL where REQUEST_OPERATION_ID=req.OPERATION_ID;if n!=0 then raise_application_error(-20886,'RECOVERY_REQUEST_CANCELLED');end if;\n"+needle,1);put("005_receiving_current.sql",s)
s=Path("db/migrations/2026-10-11_ni061_recovery_placement/008_root_body.sql").read_text(encoding="utf-8")
needle="  if g_kind='INTERWARE_RECOVERY_PUTAWAY_PLAN'then declare req "
assert s.count(needle)==2
s=s.replace(needle,"  if g_kind='INTERWARE_RECOVERY_CANCEL'then declare req json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_IW_RECOVERY_CANCEL.assert_scope(req.get_object('source').get_string('request_operation_id'),p_actor);end;end if;\n"+needle)
s=s.replace("   if g_kind='INTERWARE_RECOVERY_PUTAWAY_PLAN'then","   if g_kind='INTERWARE_RECOVERY_CANCEL'then RRL_STOCK_IW_RECOVERY_CANCEL.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='INTERWARE_RECOVERY_PUTAWAY_PLAN'then",1)
s=s.replace("  elsif g_kind='INTERWARE_RECOVERY_PUTAWAY_PLAN'then RRL_STOCK_IW_RECOVERY_PUT.execute_command","  elsif g_kind='INTERWARE_RECOVERY_CANCEL'then RRL_STOCK_IW_RECOVERY_CANCEL.execute_command(g_request,g_actor,p_result);\n  elsif g_kind='INTERWARE_RECOVERY_PUTAWAY_PLAN'then RRL_STOCK_IW_RECOVERY_PUT.execute_command",1);put("006_root_body.sql",s)
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8").replace('{"INTERWARE_RECOVERY_PUTAWAY_PLAN",','{"INTERWARE_RECOVERY_CANCEL","INTERWARE_RECOVERY_PUTAWAY_PLAN",',1);out[p.as_posix()]=s
put("apply.sql","".join("@@"+n+"\n"for n in ["001_schema.sql","002_cancel.sql","003_guard.sql","004_decisions_current.sql","005_receiving_current.sql","006_root_body.sql"])+"@@../2026-10-08_stock_posting_core/014b_recompile.sql\n")
put("rollback.sql","""declare n number;begin select count(*)into n from RRL_IW_RECOVERY_CANCEL;if n>0 then raise_application_error(-20878,'RETAINED_RECOVERY_CANCELLATIONS_REQUIRE_FORWARD_FIX');end if;end;
/
@@../2026-10-11_ni061_recovery_placement/008_root_body.sql
@@../2026-10-11_ni061_partial_recovery/002_decisions_current.sql
@@../2026-10-11_ni061_partial_recovery/003_receiving_current.sql
drop trigger RRL_IW_REC_CANCEL_G;
drop package RRL_STOCK_IW_RECOVERY_CANCEL;
drop table RRL_IW_RECOVERY_CANCEL;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
""")
put("verify.sql","select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_IW_RECOVERY_CANCEL','RRL_STOCK_IW_RECOVERY_PLAN','RRL_STOCK_IW_RECOVERY_REC','RRL_STOCK_POSTING_API');\n")
out["wiki/database/nicora_ni061_recovery_cancel_20261011.md"]="""# NI06.1: отмена сообщения о находке до физической приёмки (307)
Вход: requestID/его exactqty/причина/основание. Controller store_return_approve/currenttargetWARE; отмена уже согласованного report — другой actor относительно reporter. Новая immutable RRL_IW_RECOVERY_CANCEL, одинcancel наrequest. Report/approval/source snapshots сохраняются. NativeRoot replay/currentauth beforecache/afterwait, LOSSROW+REQUESTROW+UNITmutex в общем порядке; Source recapture подlock. Quantitywriter не меняется, quantity effect0.

Пока physicalreceipt не создан, report можноотменить и освободить его declaredquota/selectedkeys для нового report. После physicalreceipt отмена запрещена: требуется настоящий возврат/коррекция, не удаление истории. Конкурирующие receive/cancel делятLOSSROW: первыйзафиксированный физический receipt закрываетcancel, первыйcancel закрываетreceive/новуюapproval. Старые stored successfulcommand results остаются историческими; currentread отдельно показываетcancel.

Report quota/claimedkey исключают только matching APPLIEDcancel/nativekind, bound1000 включает историю отмен. Ни lossfact, ни stock/UNIT state/QR, ни customeracceptance не меняются. Журнал ROOT/commonoutbox/отмена atomic. Selectedcase reader/UI должны отображатьcancel и избегатьphysical approval на отменённойзаявке. Реальный partialclaim recurrence case и negativepostreceipt следующаяпроверка, no fabricated stock.
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Отмена сообщения о находке](database/nicora_ni061_recovery_cancel_20261011.md):307 immutablecancel/currentcontroller/zeroqty/receive competition; apply-case next.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 11.10.2026 307 design/checkpoint: immutable prephysical recoverycancellation, sameLOSSROW/UNITmutex/Root/scope; release logicalquota without inventoryeffect, full history retained. Physicalreceive and cancelledrequest deny rules prepared; current sources305/Root301 checkpoint.\n"
print(json.dumps(out))
