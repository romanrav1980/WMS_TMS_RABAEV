"""173 own one original row4 -> FULL3 + CASE1; synthetic source metadata, no stock writes."""
import sys,json,re
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();f=json.loads(Path("tmp/ni033_mixed172_fixture.json").read_text(encoding="utf-8-sig"));cache=Path("tmp/ni033_mixed173_fixture.json")
if cache.exists():print(cache.read_text(encoding="utf-8-sig"));raise SystemExit(0)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def meta(sql,**binds):
  for key in sorted(binds,key=len,reverse=True):sql=re.sub(":"+re.escape(key)+r"\b",":p_"+key,sql)
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,{"p_"+k:v for k,v in binds.items()});c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 q.execute("select count(*)from RRL_PICK_WAVE where WAVE_CODE='MIXED173.QA:00cdc0ef51'");assert q.fetchone()[0]==0,"Resume existing source, no duplicate metadata"
 q.execute("select CUSTOMER_ID from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:p_id",p_id=f["full"]["order"]);customer=q.fetchone()[0]
 q.execute("select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=f["case"]);box_type=q.fetchone()[0]
 wave,order,row,plan,line,wo=[seq(n)for n in("RRL_PICK_WAVE_SQ","RRL_CUSTOMER_ORDER_SQ","RRL_CUSTOMER_ORDER_ROW_SQ","RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_WAVE_ORDER_SQ")]
 f.update({"wave":wave,"full_uid":"MIXED173.FULL:00cdc0ef51","case_uid":"MIXED173.CASE:00cdc0ef51","shipment":"MIXED173.ST:00cdc0ef51","carrier":"CP_MIXED173_00cdc0ef51"})
 meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:id,'MIXED173:ONE:00cdc0ef51',:customer,:ware)",id=order,customer=customer,ware=f["ware"])
 meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(:id,:order,1,:article,4,'EA')",id=row,order=order,article=f["article"])
 meta("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS)values(:id,:order,:customer,:ware,'RELEASED')",id=plan,order=order,customer=customer,ware=f["ware"])
 meta("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,STATUS)values(:id,:plan,:row,:article,4,4,'PLANNED_FULL')",id=line,plan=plan,row=row,article=f["article"])
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY)values(:id,'MIXED173.QA:00cdc0ef51',:ware,'LAUNCHED','admin')",id=wave,ware=f["ware"])
 meta("insert into RRL_PICK_WAVE_ORDER(PICK_WAVE_ORDER_ID,PICK_WAVE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID)values(:id,:wave,:plan,:order,:customer)",id=wo,wave=wave,plan=plan,order=order,customer=customer)
 for key,qty,kind,uid,source,target in[("full",3,"FULL_PALLET",f["full_uid"],f["source_cell"],f["target_cell"]),("empty",1,"CASE_PICK",f["case_uid"],f["case_cell"],f["case_cell"])]:
  pt,wt=[seq(n)for n in("RRL_PICK_TASK_SQ","RRL_PICK_WAVE_TASK_SQ")];f[key]={"order":order,"row":row,"plan":plan,"line":line,"pt":pt,"wt":wt}
  meta("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,QTY)values(:id,:plan,:line,:order,:customer,:kind,'NEW',:article,:uid,:source,:target,:qty)",id=pt,plan=plan,line=line,order=order,customer=customer,kind=kind,article=f["article"],uid=uid,source=source,target=target,qty=qty)
  meta("insert into RRL_PICK_WAVE_TASK(PICK_WAVE_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,QTY,SOURCE_CELL_CODE,TARGET_CELL_CODE)values(:id,:wave,:pt,:kind,'NEW',:article,:uid,:qty,:source,:target)",id=wt,wave=wave,pt=pt,kind=kind,article=f["article"],uid=uid,qty=qty,source=source,target=target)
 task,st,ff,case,cl=[seq(n)for n in("RRL_WAREHOUSE_TASK_SQ","RRL_SBORKA_PALLETS_SQ","RRL_CUSTOMER_ORDER_FULF_SQ","RRL_CASE_PICK_TASK_SQ","RRL_CASE_PICK_LINE_SQ")]
 f.update({"task":task,"st":st,"ff":ff,"case":case,"case_line":cl})
 meta("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,ASSIGNED_TO,CREATED_BY)values(:id,'PICKING_MOVE','WAVE',:wt,'PICK_WAVE',:wave,:uid,:source,:target,:ware,:ware,3,'EA','PALLET','ASSIGNED','admin','admin')",id=task,wt=f["full"]["wt"],wave=wave,uid=f["full_uid"],source=f["source_cell"],target=f["target_cell"],ware=f["ware"])
 meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR)values(:id,:uid,:uid,:ware,0,'Owned173 one original order partial shipment')",id=st,uid=f["shipment"],ware=f["ware"])
 meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY)values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:uid,:article,'EA',3)",uid=f["shipment"],article=f["article"])
 meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY)values(:id,:order,:st,:uid,'PLANNED',0)",id=ff,order=order,st=st,uid=f["shipment"])
 meta("insert into RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID,PICK_WAVE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,SSCC,PALLET_TYPE_ID,STATUS,WARE_ID,TOTAL_LINES,PLANNED_QTY,CREATED_BY)values(:id,:wave,:plan,:order,:customer,:carrier,:type,'NEW',:ware,1,1,'admin')",id=case,wave=wave,plan=plan,order=order,customer=customer,carrier=f["carrier"],type=box_type,ware=f["ware"])
 meta("insert into RRL_CASE_PICK_LINE(CASE_PICK_LINE_ID,CASE_PICK_TASK_ID,PICK_WAVE_ID,PICK_WAVE_TASK_ID,PICK_TASK_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,ARTICUL,CELL_CODE,PLANNED_QTY,STATUS,CREATED_BY)values(:id,:case,:wave,:wt,:pt,:line,:order,:customer,:article,:cell,1,'NEW','admin')",id=cl,case=case,wave=wave,wt=f["empty"]["wt"],pt=f["empty"]["pt"],line=line,order=order,customer=customer,article=f["article"],cell=f["case_cell"])
 cache.write_text(json.dumps(f,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps(f))
