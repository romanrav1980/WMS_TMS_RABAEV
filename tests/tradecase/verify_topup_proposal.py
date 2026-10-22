"""Compare current shared and new top-up package sources; no writes."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
M=ROOT/'db/migrations/2026-10-22_trade_topup_proposal'
report=dict(status='FAIL',sources={},checks=[])
with oracle_connection() as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
 expected={(k,'PACKAGE'if k in('RRL_STOCK_UNIT_CORE','RRL_STOCK_RESERVE_CORE')else'PACKAGE BODY'):v for k,v in json.loads((M/'manifest.json').read_text())['objects_after'].items()}
 for file in ('002_read.sql','003_api.sql','004_cmd.sql'):
  for chunk in re.split(r'(?m)^/\s*$',(M/file).read_text(encoding='utf-8').replace('\r','')):
   if not chunk.strip():continue
   stored=chunk.strip()[len('create or replace '):]
   match=re.match(r'package\s+(body\s+)?(\w+)',stored,re.I);assert match
   expected[(match[2].upper(),'PACKAGE BODY'if match[1]else'PACKAGE')]=hashlib.sha256(stored.encode()).hexdigest().upper()
 for (name,kind),digest in expected.items():
  q.execute('select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE',n=name,t=kind)
  actual=hashlib.sha256(''.join(r[0]for r in q).replace('\r','').rstrip('\n').encode()).hexdigest().upper()
  assert actual==digest,(name,kind,actual,digest);report['sources'][name+'.'+kind]=actual
 q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()==(0,)
 q.execute("select INDEX_TYPE,UNIQUENESS,STATUS from USER_INDEXES where INDEX_NAME='RRL_TRADE_TOPUP_SAP_ORDER_UK'");assert q.fetchone()==('FUNCTION-BASED NORMAL','UNIQUE','VALID')
 report['checks'].append('Eleven source SHA match, INVALID zero, conditional unique order index valid')
 q.execute('select STATUS,sum(BASE_QTY),count(*)from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID in(4,5)group by STATUS');report['holds']=[list(r)for r in q];assert report['holds']==[['RELEASED',80,2]]
 q.execute('select c.WARE_ID,sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID in(214410245,223887522,210564699,220793322)group by c.WARE_ID order by c.WARE_ID');report['stock']=[list(r)for r in q];assert report['stock']==[[210564699,250,0],[214410245,250,0],[220793322,7,5],[223887522,250,0]]
 q.execute("select count(*)from RRL_TRADE_TOPUP_PROPOSAL where WARE_ID=210564699 and STATUS in('CONFIRMED','SAP_ACCEPTED')");assert q.fetchone()==(0,)
 q.execute('select count(*)from RRL_TRADE_TOPUP_PROPOSAL p join RRL_EVENT_OUTBOX o on o.EVENT_OUTBOX_ID=p.REQUEST_OUTBOX_ID where p.PROPOSAL_ID in(4,5)');assert q.fetchone()==(2,)
 report['checks'].append('Own holds released, one request per confirmed proposal and prior stock preserved')
 try:
  q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000,2),round(ELAPSED_TIME/greatest(EXECUTIONS,1)/1000,2),BUFFER_GETS from v$sql where upper(SQL_TEXT)like '%RRL_TRADE_TOPUP_%'and lower(SQL_TEXT)not like '%v$sql%'and EXECUTIONS>0 order by ELAPSED_TIME/greatest(EXECUTIONS,1)desc fetch first 10 rows only")
  report['top_sql']=[list(r)for r in q]
 except Exception as exc: report['top_sql_unavailable']=type(exc).__name__
report['status']='PASS'
output=ROOT/'runtime/test-evidence/tradecase/2026-10-22/T08/topup-native-verification.json';output.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');print(json.dumps(dict(status='PASS',sources=len(expected),checks=len(report['checks']),stock=report['stock'],top_sql=report.get('top_sql'))))