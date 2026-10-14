from pathlib import Path
p=Path('api/wms_api_server/app/routers/gps.py');s=p.read_text(encoding='utf-8');assert 'AND TRUNC(TS) = TRUNC(:d)' in s;s=s.replace('AND TRUNC(TS) = TRUNC(:d)','AND TS >= :d AND TS < :d + 1');p.write_text(s,encoding='utf-8')
