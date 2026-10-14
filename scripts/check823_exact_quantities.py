from pathlib import Path
import json,httpx
with httpx.Client(auth=('admin','admin123'),timeout=30)as c:
 r=c.get('http://127.0.0.1:8088/api/warehouse-tasks/1080');assert r.status_code==200,r.text
 t=r.json();assert t['qty_exact']=='3'and t['fact_qty_exact']=='3'and t['qty']==3,t
 r=c.get('http://127.0.0.1:8088/api/warehouse-tasks',params={'source_doc_type':'ST_DEFER','limit':10});assert r.status_code==200,r.text
 assert all(isinstance(x['qty_exact'],str)for x in r.json());print('823 PASS real task GET/LIST exact strings; legacy numeric qty preserved')
exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select to_char(cast(1000000000000.123456789 as number(28,9)),'TM9','NLS_NUMERIC_CHARACTERS=''.,''')from dual");assert q.fetchone()[0]=='1000000000000.123456789';print('823 PASS Oracle projection preserves 9 fractional digits; expression only, no stock mutation')
