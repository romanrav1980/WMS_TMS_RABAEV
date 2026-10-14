from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_reviews.py");s=p.read_text(encoding="utf-8")
start=s.index("def canonical(");end=s.index("class DayReviews:",start)
functions=s[start:end]
domain=Path("api/wms_api_server/app/modules/finance/domain/day_review_material.py")
domain.write_text('"""Canonical content of a frozen review, shared without infrastructure cycles."""\nfrom datetime import datetime\nfrom hashlib import sha256\nimport json\n\n'+functions,encoding="utf-8")
s=s[:start]+s[end:]
s=s.replace("from hashlib import sha256\n","").replace("import json\n","").replace("from .day_reconciliation import DayReconciliation","from .day_reconciliation import DayReconciliation\nfrom ..domain.day_review_material import canonical, material")
p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/modules/finance/infrastructure/day_inspections.py");s=p.read_text(encoding="utf-8").replace("from .day_reviews import canonical, material","from ..domain.day_review_material import canonical, material").replace("from datetime import date\n","");p.write_text(s,encoding="utf-8")
p=Path("db/migrations/2026-10-12_ni072_shipping_inspection/001_schema.sql");s=p.read_text(encoding="utf-8")
start=s.index("merge into RIGHTS")
s=s[:start]+"""merge into RIGHTS r using(select 'GLOBAL_ADMIN'USER_GROUP,'warehouse_day_inspection_confirm'RIGHT1 from dual)s
on(r.USER_GROUP=s.USER_GROUP and upper(r.RIGHT1)=upper(s.RIGHT1))
when not matched then insert(RIGHT1,USER_GROUP,ID,DESCR)
values(s.RIGHT1,s.USER_GROUP,(select nvl(max(ID),0)+1 from RIGHTS),'Подтверждение осмотра грузовой зоны начальником склада');
/
"""
p.write_text(s,encoding="utf-8")
for name in("scripts/checkpoint694_inspection.py","db/migrations/2026-10-12_ni072_shipping_inspection/rollback.sql"):
 p=Path(name);s=p.read_text(encoding="utf-8").replace("ID='warehouse_day_inspection_confirm'","upper(RIGHT1)='WAREHOUSE_DAY_INSPECTION_CONFIRM'");p.write_text(s,encoding="utf-8")
