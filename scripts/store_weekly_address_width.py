from pathlib import Path
p=Path('scripts/build_store_weekly_migration.py')
s=p.read_text(encoding='utf-8-sig');needle="(p/'002_route_schedule.sql').write_text"
s=s.replace(needle,"r=r.replace('varchar2(200)','varchar2(255)')\n"+needle)
p.write_text(s,encoding='utf-8')
