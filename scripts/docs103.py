from pathlib import Path
import json
out={}
p=Path("scripts/build103.py");s=p.read_text(encoding="utf-8-sig");begin=s.index('out[str(folder/"apply.sql")]=');end=s.index('out[str(folder/"rollback.sql")]',begin)
s=s[:begin]+'out[str(folder/"apply.sql")]=Path("db/migrations/2026-10-10_ni063_fullpal_tare/apply.sql").read_text(encoding="utf-8-sig")\n'+s[end:];out[str(p)]=s
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));m["components"]=[x.replace("../2026-10-10_ni063_tare_assembly/003_command.sql","../2026-10-10_ni063_fullpal_tare/001_command.sql") for x in m["components"]];out[str(p)]=json.dumps(m,indent=2)+"\n"
p=Path("wiki-raw/wms_admin_ui_reference/tare-assembly.html");s=p.read_text(encoding="utf-8-sig").replace("Верхнее место должно быть поддоном или ролл-кейджем.","Верхнее место — поддон, ролл-кейдж или самостоятельная товарная паллета FULLPAL. Для товарной паллеты выберите тип поддона.");out[str(p)]=s
p=Path("wiki/index.md");out["wiki/index.updated.tmp"]="- [Тара самостоятельной FULLPAL](database/nicora_ni063_fullpal_tare_20261010.md):103 APPLIED, original STOCK/current cell/BOOK/existing single load/current driver accept, warehouse0 vehicle1.\n"+p.read_text(encoding="utf-8-sig")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n2026-10-10:103 APPLIED reused existing STOCK/FULLPAL root for BOOK and actual handover; author PASS original single physical load/current driver accept/free0/ware0vehicle1, no fictitious outer HU or second goods event.102 slow association queries30–40ms: keep FK/PK indexes and bounded100; NI06.3 owner inspect plan if volume grows.\n"
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni06_3.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nTicket103: [тара самостоятельной FULLPAL](../../../../database/nicora_ni063_fullpal_tare_20261010.md), STOCK root/one current cell/PALLET type/hold reused by actual single load and existing handover.\n"
out["wiki/database/nicora_ni063_fullpal_tare_20261010.md"]="""# NI06.3 — самостоятельная товарная паллета,103
2026-10-10-103-standalone-stock-pallet-tare APPLIED RABAEV/orcl,9 statements/0 errors; BOOK_CMD VALID. Использованы прежние BOOK/HU identity, существующая товарная RRL_PALLETS и single LOAD_SHIPMENT. Дополнительная внешняя пустая паллета не создаётся.

STOCK root допускается при одной актуальной положительной RRL_REMAINS CELL, текущем складе, физическом типе PALLET, отсутствии родителя/CASE carrier/already loaded. Stock closure входит в прежний Root план; current stock_version/cell повторно проверяются после блокировок. Товарное количество не является количеством тары: одна самостоятельная паллета — один hold. CANCEL непустой паллеты отказан.

[Одноразовый сценарий](../../scripts/ni063_fullpal_tare_case.py) PASS: фактическая STOCK/FULLPAL3, BOOK1/free0, штатное whole picking move и existing ST bind, whole same-warehouse relocation, single actual load; current dedicated driver ACCEPT/replay закрывает claim и даёт warehouse0/vehicle1. Goods event для tare accept0, дополнительного контейнера нет. Только собственные P/H fixture очищены прежним Root; immutable history остаётся.

Межскладское перемещение физически занятой тары не получает новый custody автоматически; требуется отдельный межскладской процесс. Полный NI06.3 ещё открыт: недостача/план потребности, repack, moving damaged lineage/independent acceptance.
"""
out["задания на проведения тестов/NI06.3/103_тара_FULLPAL.md"]="""# Qwen — NI06.3,103
Новый собственный STOCK/FULLPAL fixture: один положительный current cell, PALLET type, BOOK1, existing picking move/ST binding, standalone load, independent driver ACCEPT. Тара warehouse-1/vehicle+1, goods только исходная погрузка, original claim TRANSFERRED/replay.
Отказы: TROLLEY type для STOCK, split UID по двум положительным ячейкам, CASE carrier child, upper parent, foreign warehouse, empty-source/already-loaded, CANCEL nonempty. Никакого fake PP/снятия HARD/изменения товары от BOOK.
После actual case longest SQL bounded analysis; не запускать одноразовый author-case повторно.
"""
print(json.dumps(out,ensure_ascii=True))
