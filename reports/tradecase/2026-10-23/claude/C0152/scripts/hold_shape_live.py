"""C-0152: READ ONLY constraints/usage of RRL_QUALITY_HOLD and quarantine blocking in allocation (no writes)."""
import re, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
with OracleGateway().transaction("C-0152 hold shape READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select constraint_name,constraint_type,search_condition_vc from user_constraints where table_name='RRL_QUALITY_HOLD'")
    for r in cur.fetchall(): print("C", r)
    cur.execute("select index_name,uniqueness,column_expression from user_indexes i left join user_ind_expressions e using(index_name) where i.table_name='RRL_QUALITY_HOLD'")
    print("I", cur.fetchall())
    cur.execute("select trigger_name from user_triggers where table_name='RRL_QUALITY_HOLD'"); print("T", cur.fetchall())
    cur.execute("select line,text from user_source where name='RRL_TRACEABILITY_API' and type='PACKAGE BODY' and upper(text) like '%QUALITY_HOLD%' order by line")
    print("trace", cur.fetchall())
    cur.execute("select name,line,text from user_source where type='PACKAGE BODY' and upper(text) like '%BLOCKED_FOR_REMAINS%' order by name,line")
    for n, l, t in cur.fetchall(): print("BFR", n, l, t.strip()[:180])
