from pathlib import Path
import difflib
p=Path('db/migrations/2026-10-14_ni022_store_access_dimensions')
for before,after in [('000_before_rules_package_body.sql','002_plan_rules.sql'),('000_before_rrl_stock_hu_load_core.sql','003_load.sql'),('000_before_rrl_stock_trip_depart_cmd.sql','004_depart.sql')]:
 print(after)
 print(''.join(difflib.unified_diff((p/before).read_text(encoding='utf-8').splitlines(True),(p/after).read_text(encoding='utf-8-sig').splitlines(True),n=12)))
