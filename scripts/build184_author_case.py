from pathlib import Path
import json
s=Path("scripts/ni042_weighted_case_existing_case.py").read_text(encoding="utf-8")
s=s.replace('article="QW182"+tag.upper()','article="QW184"+tag.upper()').replace('lot="CASE182.QA:"','lot="CASE184.QA:"')
s=s.replace("values(:id,:ware,:cell,null,'admin')","values(:id,:ware,:cell,.2,'admin')")
s=s.replace('"cell":dst,"article":article,"quantity":"19.6"','"cell":src,"article":article,"quantity":"19.6"')
s=s.replace('{"barcode":v,"codes":[]}for v in labels','{"barcode":v,"codes":[],"gross_weight_kg":"10.1","volume_m3":"0.030","measurement_reference":"OWN184:declared physical box"}for v in labels')
s=s.replace('  post("WAVE_PICK_RELEASE",{},{"wave_id":wave})','''  q.execute("select RRL_STOCK_REPL_CAPACITY.unit_volume(:p_cell,:p_article),RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(:p_cell,:p_article,null)from dual",p_cell=dst,p_article=article);ratio,budget=q.fetchone();assert abs(ratio-.03/9.8)<1e-12 and budget>9.8
  q.execute("select RRL_WEIGHT_BOX_CAPACITY.physical_volume(:p_uid,:p_cell,19.6)from dual",p_uid=lot,p_cell=dst);assert abs(q.fetchone()[0]-.06)<1e-12
  post("WAVE_PICK_RELEASE",{},{"wave_id":wave})''')
s=s.replace('PASS182 actual weighted barcode','PASS184 actual weighted replenishment/full physical volume.06/BOX-to-KG conversion absent/weighted barcode')
print(json.dumps({"scripts/ni042_weight_box_capacity_case.py":s},ensure_ascii=True))
