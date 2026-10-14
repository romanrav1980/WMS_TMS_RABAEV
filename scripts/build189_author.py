from pathlib import Path
import json
t=Path("scripts/ni042_warehouse_scale_use_case.py").read_text(encoding="utf-8").replace("188","189")
t=t.replace("values(:article,1,0,1,'admin')","values(:article,1,0,0,'admin')").replace("values(:id,:ware,:cell,.2,'admin')","values(:id,:ware,:cell,null,'admin')")
start=t.index('  post("INVENTORY_REGISTER_LOT"');end=t.index('\n  q.execute("select min(CUSTOMER_ID)',start)
t=t[:start]+'''  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"10","expiry_date":"2030-01-01","price":0,"reason":"Own189 loose unmarked KG"},{"revision_id":revision})'''+t[end:]
t=t.replace(":article,9.8,'KG'",":article,10,'KG'")
start=t.index('  q.execute("select RRL_STOCK_REPL_CAPACITY.unit_volume');end=t.index('  post("WAVE_PICK_RELEASE"',start);t=t[:start]+t[end:]
start=t.index('  q.execute("select u.UNIT_ID');end=t.index('  sender=',start);t=t[:start]+t[end:]
t=t.replace('"basis":"GROSS"','"basis":"NET"').replace('"scan_product":labels[0]','"scan_product":article').replace('"weight_kg":"10.1"','"weight_kg":"9.6"').replace('"weight_kg":"10.13"','"weight_kg":"9.63"')
t=t.replace('capture["weight_kg"]=="10.1"','capture["weight_kg"]=="9.6"')
t=t.replace('"weighted_box_barcode":labels[0],','').replace('/weighted-box','/weigh-line')
t=t.replace('"weighted_box_barcode":labels[1]','"scan_container":carrier+":CHANGED"')
t=t.replace('str(q.fetchone()[0])=="9.8"','str(q.fetchone()[0])=="9.6"').replace('round(p,1)==19.6 and round(h,1)==9.8','round(p,1)==10 and round(h,1)==10')
t=t.replace('  print("PASS189 existing weighted replenishment/full physical volume.06/BOX-to-KG conversion absent/weighted barcode -> existing CASE_CONFIRM9.8KG/one physical box/replay no second movement/changed barcode409/source total19.6 H9.8",operation,flush=True)','  q.execute("select STATUS from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line",p_line=line);assert q.fetchone()==("PARTIAL",)\n  print("PASS189 loose NET9.6/current KG unmarked/root exact saved replay/once-only USE/changed request409/P10H10/CASE PARTIAL remaining.4 preserved",operation,flush=True)')
print(json.dumps({"scripts/ni042_warehouse_scale_net_case.py":t},ensure_ascii=True))
