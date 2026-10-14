from pathlib import Path
p=Path(__file__).resolve().parents[1]/"api/wms_api_server/app/modules/transport/infrastructure/plan_preflight.py"
s=p.read_text(encoding="utf-8")
a=s.index('    payload = cur.var',s.index('def current_sources'))
b=s.index('    for ware in sorted',a)
s=s[:a]+'''    rows: list[dict[str, Any]] = []
    for offset in range(0, len(numbers), 200):
        batch = numbers[offset:offset + 200]
        binds = {f"st{index}": number for index, number in enumerate(batch)}
        names = ",".join(f":st{index}" for index in range(len(batch)))
        binds["row_limit"] = 5001 - len(rows)
        cur.execute(
            "select ID,ST_NUMBER,WARE_ID,TRANSTASK_ID,CONDITION from RRL_SBORKA_PALLETS "
            f"where ST_NUMBER in ({names}) order by ID fetch first :row_limit rows only", binds,
        )
        rows.extend(dict(zip(["id", "st_number", "warehouse_id", "trip_id", "condition"], row))
                    for row in cur.fetchall())
        if len(rows) > 5000:
            raise TransportPlanError("PLAN_ACTUAL_ROWS_BOUND_5000", "Превышена граница исходных строк")
    rows.sort(key=lambda row: row["id"])
'''+s[b:]
p.write_text(s,encoding="utf-8")
