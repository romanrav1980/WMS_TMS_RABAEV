"""172 synthetic own source metadata; all physical/task/shipping/cancellation effects use native owners."""
import sys,json,re
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();ware=20052672;article="QC16700CDC0EF51";tag="00cdc0ef51";src="Q167S"+tag;pick="Q167D"+tag;gate="Q172G"+tag
folder=Path("tmp/ni033_mixed172_fixture.json")
if folder.exists():print(folder.read_text(encoding="utf-8-sig"));raise SystemExit(0)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=20000
 def meta(sql,**binds):
  for key in sorted(binds,key=len,reverse=True):sql=re.sub(":"+re.escape(key)+r"\b",":p_"+key,sql)
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,{"p_"+k:v for k,v in binds.items()});c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 q.execute("select PICK_WAVE_ID from RRL_PICK_WAVE where WAVE_CODE='MIXED172.QA:00cdc0ef51'")
 wave=int(q.fetchone()[0])
 q.execute("select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1034");box_type=q.fetchone()[0]
 q.execute("select min(CUSTOMER_ID)from RRL_CUSTOMER");customer=q.fetchone()[0]
 result={"ware":ware,"article":article,"wave":wave,"source_cell":src,"case_cell":pick,"target_cell":gate,"revision":233,"full_uid":"MIXED172.FULL:"+tag,"case_uid":"MIXED172.CASE:"+tag,"shipment":"MIXED172.ST:"+tag,"controller":"QA172_KRO"}
 for key,kind in[("full","FULL_PALLET"),("empty","CASE_PICK")]:
  q.execute("""select wo.CUSTOMER_ORDER_ID,pl.CUSTOMER_ORDER_ROW_ID,wo.PICK_PLAN_ID,pl.PICK_PLAN_LINE_ID,pt.PICK_TASK_ID,wt.PICK_WAVE_TASK_ID
   from RRL_PICK_WAVE_ORDER wo join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_ID=wo.PICK_PLAN_ID
   join RRL_PICK_TASK pt on pt.PICK_PLAN_LINE_ID=pl.PICK_PLAN_LINE_ID
   join RRL_PICK_WAVE_TASK wt on wt.PICK_TASK_ID=pt.PICK_TASK_ID and wt.PICK_WAVE_ID=wo.PICK_WAVE_ID
   where wo.PICK_WAVE_ID=:p_wave and pt.TASK_TYPE=:p_kind""",p_wave=wave,p_kind=kind)
  data=q.fetchall();assert len(data)==1
  result[key]=dict(zip(("order","row","plan","line","pt","wt"),map(int,data[0])))
 task=seq("RRL_WAREHOUSE_TASK_SQ");st=seq("RRL_SBORKA_PALLETS_SQ");ff=seq("RRL_CUSTOMER_ORDER_FULF_SQ");case=seq("RRL_CASE_PICK_TASK_SQ");cl=seq("RRL_CASE_PICK_LINE_SQ")
 result.update({"task":task,"st":st,"ff":ff,"case":case,"case_line":cl,"carrier":"CP_MIXED172_"+tag})
 meta("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,ASSIGNED_TO,CREATED_BY)values(:id,'PICKING_MOVE','WAVE',:wt,'PICK_WAVE',:wave,:uid,:source,:target,:ware,:ware,3,'EA','PALLET','ASSIGNED','admin','admin')",id=task,wt=result["full"]["wt"],wave=wave,uid=result["full_uid"],source=src,target=gate,ware=ware)
 meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR)values(:id,:uid,:uid,:ware,0,'Owned172 synthetic standalone shipment')",id=st,uid=result["shipment"],ware=ware)
 meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY)values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:uid,:article,'EA',3)",uid=result["shipment"],article=article)
 meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY)values(:id,:order,:st,:uid,'PLANNED',0)",id=ff,order=result["full"]["order"],st=st,uid=result["shipment"])
 meta("insert into RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID,PICK_WAVE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,SSCC,PALLET_TYPE_ID,STATUS,WARE_ID,TOTAL_LINES,PLANNED_QTY,CREATED_BY)values(:id,:wave,:plan,:order,:customer,:carrier,:type,'NEW',:ware,1,1,'admin')",id=case,wave=wave,plan=result["empty"]["plan"],order=result["empty"]["order"],customer=customer,carrier=result["carrier"],type=box_type,ware=ware)
 meta("insert into RRL_CASE_PICK_LINE(CASE_PICK_LINE_ID,CASE_PICK_TASK_ID,PICK_WAVE_ID,PICK_WAVE_TASK_ID,PICK_TASK_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,ARTICUL,CELL_CODE,PLANNED_QTY,STATUS,CREATED_BY)values(:id,:case,:wave,:wt,:pt,:line,:order,:customer,:article,:cell,1,'NEW','admin')",id=cl,case=case,wave=wave,wt=result["empty"]["wt"],pt=result["empty"]["pt"],line=result["empty"]["line"],order=result["empty"]["order"],customer=customer,article=article,cell=pick)
 meta("insert into USER_GROUP(ID,NAME)values('QA172_QC','Owned172 independent warehouse control')")
 meta("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED)values('QA172_KRO','Owned172 independent controller','qa-test-only','QA172_QC',:ware,0)",ware=ware)
 for right in("outgoing_pallet_check","stock_ship_pallet"):meta("insert into RIGHTS(ID,RIGHT1,USER_GROUP)select nvl(max(ID),0)+1,:right,'QA172_QC'from RIGHTS",right=right)
 folder.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(result))
