exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
ctx=json.loads(Path('tmp/qc1461_config.json').read_text());uid=json.loads(Path('tmp/qc1457_candidates.json').read_text())[0][0]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute('set transaction read only');q.execute('select p.ARTICUL,r.CELL,r.BASE_UOM,r.REMAIN,p.STOCK_COMPOSITION_VERSION from RRL_PALLETS p join RRL_REMAINS r on r.UID_POLETA=p.UID_PALLET where p.UID_PALLET=:p_uid and r.REMAIN>0',p_uid=uid);article,cell,uom,qty,epoch=q.fetchone()
 domain={'warehouse':ctx['warehouse'],'document_id':ctx['document_id'],'pallet_identifier':ctx['shipment'],'legs':[{'uid':uid,'cell':cell,'article':article,'quantity':str(qty),'base_uom':uom}]}
 def proof(d):
  q.execute('select RRL_QC_SCOPE_READ.exemption_json(:body) from dual',body=json.dumps(d));value=q.fetchone()[0];return json.loads(value.read() if hasattr(value,'read') else value)
 whole=proof(domain);assert whole['eligible'],whole
 partial=json.loads(json.dumps(domain));partial['legs'][0]['quantity']='2';partial_proof=proof(partial);assert not partial_proof['eligible'],partial_proof
 q.execute('select RRL_STOCK_QC_MARK.required_for_plan(:body) from dual',body=json.dumps(domain));marked=q.fetchone()[0];assert marked==1
 try:q.execute('begin RRL_STOCK_QC_GATE.assert_approved(:body);end;',body=json.dumps(domain));raise AssertionError('Marked goods admitted without scan')
 except oracledb.DatabaseError as e:
  reason=str(e.args[0]);assert 'SHIPMENT_CURRENT_UNIQUE_MARK_CONTROL_REQUIRED' in reason,reason
 q.execute('select count(*) from RRL_QC_EXEMPT_FACT');audit_count=q.fetchone()[0];assert audit_count==0
 result={'whole':whole,'partial':partial_proof,'marked_required':marked,'marked_without_scans':reason.splitlines()[0],'audit_rows_after_read':audit_count,'native_domain':'synthetic domain with real immutable receipt/current stock, not a shipment execution','writes':0}
 Path('tmp/result1462.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result))

