"""Use one native readonly assembly clock authority for CASE and ordinary BOX."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json


def box_assembly_clocks(cursor: Any,tree: dict[str,Any],ware: int,region: str)->list[dict[str,Any]]:
    cursor.setinputsizes(tree_body=oracledb.DB_TYPE_CLOB)
    cursor.execute("select RRL_BOX_ASSEMBLY_READ.clocks_json(:tree_body,:ware,:region)from dual",
                   tree_body=json.dumps(tree),ware=ware,region=region)
    return read_oracle_json(cursor.fetchone()[0])
