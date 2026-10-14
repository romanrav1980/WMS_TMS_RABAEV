from pathlib import Path
p=Path(__file__).resolve().parents[1]/"api/wms_api_server/app/modules/inventory/infrastructure/case_carrier_close.py"
s=p.read_text(encoding="utf-8")
a=s.index('    cur.execute("""select count(*)from RRL_CASE_PICK_LINE l')
s=s[:a]+'''    cur.execute("""select count(*)from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:id
        and (nvl(PICKED_QTY,0)<0 or nvl(PLANNED_QTY,0)<0 or nvl(PICKED_QTY,0)>nvl(PLANNED_QTY,0)
             or(STATUS='PICKED'and nvl(PICKED_QTY,0)!=nvl(PLANNED_QTY,0)))""", id=task)
    if cur.fetchone()[0]:
        raise HTTPException(409, detail="CASE_LINE_QUANTITY_STATE_CONFLICT")
'''+s[a:]
p.write_text(s,encoding="utf-8")
