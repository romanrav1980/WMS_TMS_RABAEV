"""178 read-only same-snapshot equivalence and sparse container-cell access timings."""
import sys
from pathlib import Path
from time import perf_counter
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 q.execute("select INDEX_NAME,STATUS,NUM_ROWS from USER_INDEXES where INDEX_NAME='RRL_PALLETS_HUCELL_I1'")
 index=q.fetchone();assert index and index[1]=="VALID";print("Sparse index",index)
 q.execute("select NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_HU_CMD','RRL_STOCK_HU_SLOT')");assert not q.fetchall()
 q.execute("select distinct case when HU_KIND='CONTAINER'then HU_CURRENT_CELL end CELL from RRL_PALLETS where case when HU_KIND='CONTAINER'then HU_CURRENT_CELL end is not null order by CELL fetch first 6 rows only")
 cells=[x[0]for x in q.fetchall()]+["NO_CELL_178"]
 old_times=[];new_times=[]
 for cell in cells:
  start=perf_counter();q.execute("select UID_PALLET,HU_CONTENT_VERSION from RRL_PALLETS where HU_KIND='CONTAINER'and HU_CURRENT_CELL=:p_cell order by UID_PALLET",p_cell=cell);old=q.fetchall();old_times.append((perf_counter()-start)*1000)
  start=perf_counter();q.execute("select UID_PALLET,HU_CONTENT_VERSION from RRL_PALLETS where case when HU_KIND='CONTAINER'then HU_CURRENT_CELL end=:p_cell order by UID_PALLET",p_cell=cell);new=q.fetchall();new_times.append((perf_counter()-start)*1000)
  assert old==new,cell
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 c.rollback()
 print("PASS178 same current READ ONLY snapshot old/new equal cells",len(cells),"old average ms",round(sum(old_times)/len(cells),3),"new average ms",round(sum(new_times)/len(cells),3),"originalP20H20 unchanged; author latency sample, not load capacity")
