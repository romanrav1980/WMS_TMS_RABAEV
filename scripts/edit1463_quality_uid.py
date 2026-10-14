from pathlib import Path
import re
p=Path('db/migrations/2026-10-14_ni051_scoped_quality/002_reader.sql');s=p.read_text(encoding='utf-8');s=re.sub(r'\buid\b','v_uid',s).replace("'v_uid'","'uid'");p.write_text(s,encoding='utf-8')
p=Path('scripts/case1462_quality_proof.py');s=p.read_text(encoding='utf-8-sig').replace(':uid',':p_uid').replace(',uid=uid)',',p_uid=uid)');p.write_text(s,encoding='utf-8')
