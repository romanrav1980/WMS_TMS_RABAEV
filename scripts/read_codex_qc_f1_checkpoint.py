exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import hashlib
folder=Path('reports/nicora/2026-10-13/codex/QC_F1');folder.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select dbms_metadata.get_ddl('PACKAGE_BODY','RRL_QC_SCOPE_READ',user)from dual");raw=q.fetchone()[0].read().strip()+'\n/\n';(folder/'before_reader.sql').write_text(raw,encoding='utf-8')
 q.execute("""select ff.LEGACY_SBORKA_PALLET_ID,ff.PALLET_UID,ff.CUSTOMER_ORDER_ID,ff.PICKED_PALLET_UID,ff.PICKED_STOCK_VERSION,m.TO_CELL,m.BASE_QTY,m.BASE_UOM,rr.STOCK_VERSION,st.WARE_ID
 from RRL_CUSTOMER_ORDER_FULFILLMENT ff join RRL_WAREHOUSE_TASK_STOCK_MOVE m on m.OPERATION_ID=ff.PICKED_OPERATION_ID and m.TASK_ID=ff.PICKED_WAREHOUSE_TASK_ID
 join RRL_PALLETS p on p.UID_PALLET=ff.PICKED_PALLET_UID join RRL_SAP_PALLET_RECEIPT receipt on receipt.UID_PALLET=p.UID_PALLET
 join RRL_REMAINS rr on rr.UID_POLETA=p.UID_PALLET and rr.CELL=m.TO_CELL
 join RRL_SBORKA_PALLETS st on st.ID=ff.LEGACY_SBORKA_PALLET_ID
 where ff.STATUS='PICKED' and p.STOCK_COMPOSITION_VERSION=1 and m.UID_PALLET=m.TARGET_UID_PALLET and rr.REMAIN=receipt.POSTED_BASE_QTY and rr.REMAIN>0
 order by ff.FULFILLMENT_ID fetch first 3 rows only""");rows=q.fetchall();(folder/'candidates.json').write_text(json.dumps(rows),encoding='utf-8');print('Candidates',rows)
(folder/'checkpoint.json').write_text(json.dumps({'before_sha256':hashlib.sha256(raw.encode()).hexdigest(),'file':'before_reader.sql'}),encoding='utf-8')
