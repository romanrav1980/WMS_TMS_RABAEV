"""One root-approved CASE1EA hypothetical TX; pure close/bind/return preflight; full rollback."""
import hashlib
import json
from pathlib import Path
import sys
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from case_scoped_confirmation_native_smoke import OracleGateway,oracle_connection,StockCommand,post,scalar,snapshot,ACTOR,LOT
from app.modules.inventory.infrastructure.case_carrier_close import validate_close_content
from app.modules.inventory.domain.carrier_shipment import assert_matching_composition
from app.modules.inventory.domain.case_close_state import close_transition
from app.modules.platform.public import read_oracle_json
OP='WHREQ15.COMPENSATION.ROLLBACK'
OUT=ROOT/'reports/retailcase/2026-10-15/warehouse-weigh-request/compensation-caller-rollback.json'


def main():
 g=OracleGateway();before=snapshot(g,1136,1139)
 assert before['task'][0]['status']=='IN_PROGRESS'and before['task'][0]['picked_qty']==0 and before['task'][0]['legacy_sborka_pallet_id']is None
 assert not g.fetch_all('select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:op',{'op':OP})
 marker=g.fetch_all('select nvl(max(LOG_ID),0)N from RRL_SQL_SLOW_LOG')[0]['n']
 command=StockCommand(OP,'CASE_PICK_CONFIRM',ACTOR,(),{'case_task_id':1136,'case_line_id':1139},metadata=dict(fact_qty='1',scan_cell='QIPcdbf4c0962',scan_product='REUSE.QA:cdbf4c0962',scan_container='090000000000008014',offline_event_id=None))
 checks=[];return_compiler={};hypothetical={}
 with oracle_connection()as conn:
  c=conn.cursor()
  try:
   result=post(c,command);checks.append('ONE_clean_prepare_execute_canonical_1EA_inside_caller_TX')
   assert scalar(c,'select sum(REMAIN)from RRL_REMAINS where UID_POLETA=:lot',lot=LOT)==23
   c.execute('select h.LOT_UID,s.CELL,s.REMAIN,s.HARD_RESERVED_BASE,p.STOCK_ORIGIN_UID,p.CREATED_BY_STOCK_OP from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID where h.CASE_PICK_TASK_ID=1136 and s.REMAIN>0')
   lots=c.fetchall();assert len(lots)==1 and lots[0][1]=='CPT_13583852'and lots[0][2:4]==(1,1)and lots[0][5]==OP,lots
   child=lots[0][0];assert lots[0][4]=='300000034518661218'
   c.execute('select STATUS,CONTENT_VERSION,SSCC,ASSIGNED_TO,SHIPPED_OPERATION,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136')
   state,version,sscc,assignee,shipped,legacy=c.fetchone();assert legacy is None and close_transition(state,shipped)=='CLOSE'
   validate_close_content(c,1136,ACTOR,assignee);checks.append('pure_current_close_validation_accepts_complete_physical_1EA_no_status_write')
   c.execute("select p.ARTICUL,s.BASE_UOM,to_char(s.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID where h.CASE_PICK_TASK_ID=1136 and s.REMAIN>0 order by h.LOT_UID,s.CELL")
   physical=c.fetchall()
   c.execute("select r.ARTICUL,to_char(r.QUANTITY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),u.BASE_UOM,u.NUMERATOR,u.DENOMINATOR,u.BASE_SCALE from RRL_SBORKA_PALLET_ROWS r join RRL_STOCK_UOM_CONVERSION u on u.ARTICUL=r.ARTICUL and u.INPUT_UOM=r.EI where r.PALLET_UID='TEST.WHREQ15.PREPARED'and u.POLICY_VERSION=(select max(v.POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION v where v.ARTICUL=r.ARTICUL and v.INPUT_UOM=r.EI)order by r.ID")
   planned=c.fetchall();assert_matching_composition(physical,planned);checks.append('pure_existing_bind_exact_BASE_composition_matches_prepared_ST_1EA')
   c.execute("select ID,WARE_ID,CONDITION from RRL_SBORKA_PALLETS where PALLET_UID='TEST.WHREQ15.PREPARED'");st=c.fetchone();assert st[1]==13583852 and(st[2]or 0)<2
   assert scalar(c,"select count(*)from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:st and CUSTOMER_ORDER_ID=2146 and STATUS='PLANNED'and FACT_QTY=0",st=st[0])==1
   c.execute('select LINE,TEXT from USER_SOURCE where NAME=\'RRL_STOCK_CASE_RETURN_CMD\'and TYPE=\'PACKAGE\'order by LINE');spec=''.join(r[1]for r in c.fetchall())
   return_command=StockCommand(OP+'.RETURN.PLAN','CASE_CARRIER_RETURN','admin',(),{'case_task_id':1136},metadata=dict(destinations={child:'QIPcdbf4c0962'},expected_content_version=version,scan_container=sscc))
   if 'accessible by'in spec.lower():
    # This direct compiler is owner-private; no wrapper, DDL, or dirty second Stockprepare.
    return_compiler=dict(status='NOT_RUN_OWNER_BOUNDARY',accessible_by='RRL_STOCK_POSTING_API',spec=spec)
   else:
    outputs=[c.var(oracledb.DB_TYPE_CLOB)for _ in range(3)]
    c.callproc('RRL_STOCK_CASE_RETURN_CMD.compile_command',[return_command.canonical_json(),return_command.operation_id,*outputs])
    return_compiler=dict(status='PURE_COMPILED',domain=read_oracle_json(outputs[2].getvalue()))
   # Source-reviewed compiler predicates on this same hypothetical physical composition.
   assert 1<=len(lots)<=200
   c.execute('select CELL_CODE from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=1139');assert c.fetchone()[0]=='QIPcdbf4c0962'
   c.execute('select RESERVATION_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_LINE_ID,STATUS,BASE_QTY,CELL from RRL_STOCK_RESERVATION where UID_PALLET=:lot and RESERVATION_KIND=\'HARD\'and STATUS in(\'ACTIVE\',\'ALLOCATED\',\'PICKING\')and BASE_QTY>0',lot=child)
   reserves=c.fetchall();assert len(reserves)==1 and reserves[0][1:4]==('PICK_WAVE',567,2137)and reserves[0][5]==1 and reserves[0][6]=='CPT_13583852',reserves
   assert state not in('SHIPPED','CANCELLED','FAILED')and not shipped
   checks.append('source_reviewed_RETURN_all_lots_original_cell_ownHARD_state_currentversion_predicates_pass_without_closed_requirement')
   assert scalar(c,'select count(*)from RRL_STOCK_OP_CLOCK where OPERATION_ID=:op',op=OP)==1
   assert scalar(c,'select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op',op=OP+'.RETURN.PLAN')==0
   hypothetical=dict(case_state=state,case_content_version=version,case_legacy_id=legacy,parent_total=23,child=dict(uid=child,cell=lots[0][1],P=1,H=1,origin=lots[0][4],created_operation=OP),physical=physical,prepared_composition=planned,return_command=json.loads(return_command.canonical_json()),return_compiler=return_compiler)
  finally:
   conn.rollback();c.callproc('RRL_STOCK_POSTING_API.reset_connection')
 assert snapshot(g,1136,1139)==before
 for table,column,value in [('RRL_STOCK_OPERATION','OPERATION_ID',OP),('RRL_PALLETS','CREATED_BY_STOCK_OP',OP),('RRL_STOCK_OP_CLOCK','OPERATION_ID',OP),('RRL_EVENT_OUTBOX','IDEMPOTENCY_KEY','STOCK:'+hashlib.sha256(OP.encode()).hexdigest().upper())]:
  assert g.fetch_all('select count(*)N from '+table+' where '+column+'=:value',{'value':value})[0]['n']==0
 assert not g.fetch_all('select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=1136')
 checks.append('source_case_line_events_operation_child_outbox_clock_all_rolled_back')
 slow=g.fetch_all('select LOG_ID,ELAPSED_MS,dbms_lob.substr(SQL_TEXT,300,1) SQL_SAMPLE from RRL_SQL_SLOW_LOG where LOG_ID>:marker order by ELAPSED_MS desc fetch first 10 rows only',{'marker':marker})
 report=dict(status='PASS_WITH_PRIVATE_COMPILER_LIMIT',checks=checks,operation_id=OP,stock_committed=False,metadata_close_or_bind_written=False,second_Stockprepare_called=False,
  native_RETURN_execute_proven=False,physical_hardware=False,before_after=before,hypothetical=hypothetical,slow_sql=slow,
  sql_decision='Retain bounded CASE1136/line1139 and specificUID/operation closures; no load/capacity claim. Native RETURN prepare/execute is a separate clean-TX gate after root quantity approval.')
 OUT.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
 print(json.dumps(dict(status=report['status'],checks=checks,stock_committed=False,return_compiler=return_compiler['status'])))


if __name__=='__main__':main()
