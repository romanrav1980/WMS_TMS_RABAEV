"""Expose actual carrier contents and remove the old active CASE clamp entrypoint."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=1:raise RuntimeError("Missing unique anchor "+path+" "+old[:35])
 files[path]=text.replace(old,new,1)
path="api/wms_api_server/app/services/case_pick_service.py"
# Scope exact quantity substitutions to get_task only, preserving unrelated queries.
text=(ROOT/path).read_text(encoding="utf-8")
start=text.index("    def get_task(");end=text.index("\n    def ",start+10)
chunk=text[start:end]
chunk=chunk.replace("t.PLANNED_QTY,","to_char(t.PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_QTY,")
chunk=chunk.replace("t.PICKED_QTY,","to_char(t.PICKED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PICKED_QTY,\n                   t.CURRENT_CELL,t.CONTENT_VERSION,")
chunk=chunk.replace("                   PLANNED_QTY,","                   to_char(PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PLANNED_QTY,")
chunk=chunk.replace("                   PICKED_QTY,","                   to_char(PICKED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PICKED_QTY,")
chunk=chunk.replace("        return task","""        task["physical_lots"] = self.gateway.fetch_all(
            "select h.LOT_UID UID,h.CASE_PICK_LINE_ID,p.ARTICUL,s.CELL,s.BASE_UOM,"
            "to_char(s.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PHYSICAL_QTY,"
            "to_char(s.HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') HARD_QTY "
            "from RRL_CASE_CARRIER_LOT h join RRL_REMAINS s on s.UID_POLETA=h.LOT_UID "
            "join RRL_PALLETS p on p.UID_PALLET=h.LOT_UID "
            "where h.CASE_PICK_TASK_ID=:id and s.REMAIN>0 order by h.LOT_UID,s.CELL fetch first 201 rows only",
            {"id": case_pick_task_id})
        return task""")
files[path]=text[:start]+chunk+text[end:]
# Locked shortage row quantities stay precise too.
edit(path,'        planned_qty = Decimal(str(line.get("planned_qty") or 0))',
 """        exact = self.gateway.fetch_all("select to_char(PLANNED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') Q from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:id", {"id": line_id})
        planned_qty = Decimal(str(exact[0]["q"] or "0"))""")
path="api/wms_api_server/app/services/picking_service.py"
edit(path,"""        actor = request.completed_by or "API"
        rows = self.gateway.fetch_all(""","""        actor = request.completed_by or "API"
        release = self.gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if not release or release[0]["state"] != "PREPARED":
            types = self.gateway.fetch_all(
                "select t.TASK_TYPE,l.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID "
                "from RRL_PICK_TASK t left join RRL_CASE_PICK_LINE l on l.PICK_TASK_ID=t.PICK_TASK_ID "
                "where t.PICK_TASK_ID=:id", {"id": pick_task_id})
            if types and types[0]["task_type"] == "CASE_PICK":
                raise HTTPException(409, detail={"code": "CASE_PICK_CONFIRM_REQUIRED",
                    "case_pick_task_id": types[0].get("case_pick_task_id"),
                    "case_pick_line_id": types[0].get("case_pick_line_id"),
                    "message": "Confirm the existing CASE line in case-pick-tsd.html; physical stock stays reserved until shipment"})
        rows = self.gateway.fetch_all(""")
print(json.dumps(files,ensure_ascii=True))
