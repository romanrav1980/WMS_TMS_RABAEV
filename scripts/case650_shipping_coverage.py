exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from datetime import date
from app.modules.finance.infrastructure.shipping_register import read_snapshot
from app.modules.master_data.public import published_cell_coverage
ctx=json.loads(Path("tmp/context641.json").read_text());ware=ctx["warehouse"];src=ctx["receive"];dst=ctx["pick"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 before=published_cell_coverage(q,ware);assert not before["classification_complete"]
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("select RRL_WH_TOPOLOGY_SQ.nextval from dual");topology=int(q.fetchone()[0])
  q.execute("insert into RRL_WAREHOUSE_TOPOLOGY(TOPOLOGY_ID,WARE_ID,TOPOLOGY_CODE,TOPOLOGY_NAME,STATUS,CREATED_BY,UPDATED_BY)values(:topo,:ware,:code,'Own650 rollback classification','PUBLISHED','admin','admin')",topo=topology,ware=ware,code="OWN650:"+ctx["tag"])
  q.execute("select CELL from RRL_CELLS where WARE_ID=:ware order by CELL",ware=ware);cells=[x[0]for x in q]
  for cell in cells:
   q.execute("insert into RRL_TOPOLOGY_CELL(TOPOLOGY_CELL_ID,TOPOLOGY_ID,WARE_ID,CELL_CODE,LEGACY_CELL_CODE,CELL_KIND,CREATED_BY,UPDATED_BY)values(RRL_TOPOLOGY_CELL_SQ.nextval,:topo,:ware,:cell,:cell,:kind,'admin','admin')",topo=topology,ware=ware,cell=cell,kind="GATE"if cell==src else "STORAGE")
  empty=read_snapshot(q,ware,date(2026,10,12),0,20)
  assert empty["all_shipping_zone_coverage_verified"]and empty["shipping_zone_empty_confirmed"],empty["classification_coverage"]
  q.execute("update RRL_TOPOLOGY_CELL set CELL_KIND='TRANSPORT_STAGING'where TOPOLOGY_ID=:topo and LEGACY_CELL_CODE=:cell",topo=topology,cell=dst)
  occupied=read_snapshot(q,ware,date(2026,10,12),0,20)
  assert occupied["all_shipping_zone_coverage_verified"]and not occupied["shipping_zone_empty_confirmed"]and occupied["declared_cells_occupied"]
  q.execute("update RRL_TOPOLOGY_CELL set CELL_KIND='EMPTY'where TOPOLOGY_ID=:topo and LEGACY_CELL_CODE=:cell",topo=topology,cell=dst)
  unknown=published_cell_coverage(q,ware);assert not unknown["classification_complete"]and unknown["unclassified_cell_count"]==1
  q.execute("update RRL_TOPOLOGY_CELL set CELL_KIND='STORAGE'where TOPOLOGY_ID=:topo and LEGACY_CELL_CODE=:cell",topo=topology,cell=dst)
  q.execute("insert into RRL_TOPOLOGY_CELL(TOPOLOGY_CELL_ID,TOPOLOGY_ID,WARE_ID,CELL_CODE,LEGACY_CELL_CODE,CELL_KIND)values(RRL_TOPOLOGY_CELL_SQ.nextval,:topo,:ware,:code,:cell,'EMPTY')",topo=topology,ware=ware,code="AMB650:"+ctx["tag"],cell=dst)
  ambiguous=published_cell_coverage(q,ware);assert not ambiguous["classification_complete"]and ambiguous["ambiguous_cell_count"]==1
  c.rollback()
 finally:c.rollback();q.callproc("RRL_STOCK_CONFIG_API.end_change")
 after=published_cell_coverage(q,ware);assert before==after
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["lot"],cell=dst);assert q.fetchone()==(3,0)
 q.execute("select SQL_ID,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)like '%MAPPED_COUNT%'and upper(SQL_TEXT)not like '%V$SQL%'order by LAST_ACTIVE_TIME desc fetch first 3 rows only")
 print("SQL650",json.dumps(q.fetchall()))
print("PASS650 complete catalog empty/occupied/unknown/ambiguous mixed roles -> rollback restores source/P3H0; no actual physical-zone certification")
