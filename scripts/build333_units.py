from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_marked_consolidation");out={}
old=Path("db/migrations/2026-10-12_ni061_nested_onward/008_unit_source.sql").read_text(encoding="utf-8")
new=old.replace("stock_nodes number:=0;","stock_nodes number:=0;selected_nodes number:=0;")
new=new.replace("tree.get_number('leaf_count')!=1","tree.get_number('leaf_count')<1",1)
new=new.replace("if candidate.get_string('kind')='STOCK'then node:=candidate;stock_nodes:=stock_nodes+1;","if candidate.get_string('kind')='STOCK'then stock_nodes:=stock_nodes+1;if candidate.get_string('uid')=p_uid then node:=candidate;selected_nodes:=selected_nodes+1;end if;",1)
new=new.replace("if stock_nodes!=1 then","if selected_nodes!=1 or stock_nodes!=tree.get_number('leaf_count')then",1)
new=new.replace("if n!=nvl(tree.get_number('physical_unit_count'),0)or","if(tree.get_number('leaf_count')=1 and n!=nvl(tree.get_number('physical_unit_count'),0))or",1)
assert new!=old
out[(d/"000_before_units.sql").as_posix()]=old;out[(d/"001_units.sql").as_posix()]=new
print(json.dumps(out))
