"""174 rollback-only prove old planner still asks4 after real original4/shipped3."""
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 try:
  plan=q.callfunc("RRL_PICKING_API.create_plan",oracledb.DB_TYPE_NUMBER,[1931,"FEFO","admin"])
  q.execute("select TOTAL_ORDER_QTY,TOTAL_PLANNED_QTY from RRL_PICK_PLAN where PICK_PLAN_ID=:p_plan",p_plan=plan);print("Old requested/planned after original4/shipped3:",q.fetchone())
 finally:c.rollback()
