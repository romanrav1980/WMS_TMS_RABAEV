from pathlib import Path
p=Path('scripts/store_weekly_native_conversion_bench.py');s=p.read_text(encoding='utf-8-sig').replace("'declare '+code+''' v_result date;begin", "'declare v_result date;'+code+''' begin").replace("'declare '+code+''' v_result date;failed boolean:=false;begin", "'declare v_result date;failed boolean:=false;'+code+''' begin")
p.write_text(s,encoding='utf-8')
