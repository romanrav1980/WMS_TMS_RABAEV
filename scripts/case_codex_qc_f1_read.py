exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from time import perf_counter
folder=Path('reports/retailcase/2026-10-13/codex/QC_F1');ctx=json.loads(Path('tmp/qc1461_config.json').read_text());uid=json.loads(Path('tmp/qc1457_candidates.json').read_text())[0][0];results={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_QC_SCOPE_READ'");assert not q.fetchall()
 q.execute('select p.ARTICUL,r.CELL,r.BASE_UOM,r.REMAIN,r.STOCK_VERSION from RRL_PALLETS p join RRL_REMAINS r on r.UID_POLETA=p.UID_PALLET where p.UID_PALLET=:p_uid and r.REMAIN>0',p_uid=uid);article,cell,uom,qty,version=q.fetchone()
 domain={'warehouse':ctx['warehouse'],'document_id':ctx['document_id'],'pallet_identifier':ctx['shipment'],'legs':[{'uid':uid,'cell':cell,'article':article,'quantity':str(qty),'base_uom':uom}]}
 q.execute('select count(*)from RRL_QC_EXEMPT_FACT');audit=q.fetchone()[0];c.rollback()
 def proof(d):
  start=perf_counter();q.execute('select RRL_QC_SCOPE_READ.exemption_json(:body)from dual',body=json.dumps(d));v=json.loads(q.fetchone()[0].read());v['read_ms']=round((perf_counter()-start)*1000,2);return v
 q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
 try:
  q.execute("update RRL_QC_SCOPE_RULE set ACTIVE_FLAG=1,CONTROL_MODE='WEIGHT',EXEMPT_WHOLE=1,EXEMPT_STORAGE=0 where WARE_ID=:w and STORE_ADDR='*'and PLACE_CATEGORY='STOCK'",w=ctx['warehouse'])
  results['whole']=proof(domain);assert results['whole']['eligible']
  q.execute("update RRL_QC_SCOPE_RULE set EXEMPT_WHOLE=0,EXEMPT_STORAGE=1 where WARE_ID=:w and STORE_ADDR='*'and PLACE_CATEGORY='STOCK'",w=ctx['warehouse'])
  results['storage_no_binding']=proof(domain);assert not results['storage_no_binding']['eligible']
  domain.update({'bound_physical_uid':uid,'customer_order_id':1,'bound_stock_version':version,'bound_current_stock_version':version})
  results['forged_domain_binding']=proof(domain);assert not results['forged_domain_binding']['eligible']
  q.execute('select count(*)from RRL_QC_EXEMPT_FACT');assert q.fetchone()[0]==audit
 finally:c.rollback();q.callproc('RRL_STOCK_CONFIG_API.end_change')
 q.execute("select RULE_VERSION,ACTIVE_FLAG from RRL_QC_SCOPE_RULE where WARE_ID=:w and STORE_ADDR='*'and PLACE_CATEGORY='STOCK'",w=ctx['warehouse']);results['rule_after_rollback']=q.fetchone();assert results['rule_after_rollback']==(3,0)
results['audit_unchanged']=True;results['scope']='Synthetic domain with actual receipt; temporary configuration rolled back; no stock writes';(folder/'readonly.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(results,ensure_ascii=True))
