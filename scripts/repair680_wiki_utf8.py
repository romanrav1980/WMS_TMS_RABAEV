from pathlib import Path
import re
p=Path("wiki/components/retailcase_ni062_custody_recovery_20261012.md")
s=p.read_text(encoding="utf-8")
s=re.sub(r"Checkpoint661:.*", "Checkpoint661: действия и видимые строки привязаны к загруженному контексту. Смена пользователя или магазина не отправляет старый intent с новыми credentials. Ошибка удаления подтверждённого отказа сохраняет исходник. Offline quality gate PASS: 24 architecture/tooling cases и оба TypeScript; предупреждение только о pytest cache.",s)
p.write_text(s,encoding="utf-8")
p=Path("wiki/database/retailcase_ni061_group_aggregation_20261012.md")
s=p.read_text(encoding="utf-8")
s=re.sub(r"667 applied:.*","667 applied: первая компиляция выявила SQL-вызов метода JSON object; исправлено предварительным присваиванием CLOB. Live USER_ERRORS=[] / INVALID=[]. UI668 поддерживает UNIT/BOX/PALLET по текущим карточкам; одна ограниченная SQL-матрица scan_profiles, SOURCE_JSON неизменён. JS/architecture PASS. Fresh669 source — отдельный источник; protected404/405/406 не повторять.",s)
s=re.sub(r"Checkpoint674 prepared:.*","Checkpoint674 prepared: смешанный case673 выявил глобальную проверку direct_scan по системе/профилю. QR одного товара ошибочно блокировал PALLET другого товара того же профиля. Общий native validator уточнён по текущему физическому UID; локальная копия правила удалена. Оба source/hash/paired rollback сохранены до применения; количество и блокировки не менялись.",s)
p.write_text(s,encoding="utf-8")
p=Path("wiki/index.md");s=p.read_text(encoding="utf-8")
lines=s.splitlines()
labels={
"NI01.1 checkpoint678":"- [NI01.1 checkpoint678: склад этикетки](components/retailcase_ni011_receipt_label_access_20261012.md): native scope для issue/HTML/ZPL/confirm/USED; actor contract; label fixture отсутствует.",
"NI06.1 checkpoint676":"- [NI06.1 checkpoint676: группа UNIT + BOX + PALLET](database/retailcase_ni061_group_aggregation_20261012.md): native667/674 VALID, actual673 P3H0 each / old6units9codes / rollback / HTTP675; plan28.",
"NI06.1 checkpoint667":"- [NI06.1 checkpoint667: агрегационная приёмка группы](database/retailcase_ni061_group_aggregation_20261012.md): reuse общего native validator; итоговый положительный кейс673 указан на странице.",
"NI06.1 checkpoint664":"- [NI06.1 checkpoint664: продолжение межскладского списка](components/retailcase_ni061_group_queue_20261012.md): прежний API/экран, текущие WARE/actor, bounded keyset; многорядная приёмка открыта.",
}
for i,line in enumerate(lines):
 for marker,new in labels.items():
  if marker in line and "???" in line:lines[i]=new
p.write_text("\n".join(lines)+"\n",encoding="utf-8")
p=Path("wiki/log.md");s=p.read_text(encoding="utf-8")
s=re.sub(r"12\.10\.2026 checkpoint664:.*","12.10.2026 checkpoint664: existing grouped worklist has limit/keyset and next page in original UI. Actual663 one-source/native empty continuation/422 bounds PASS; no stock writes. SQL16.959/44.225ms: bounded query retained; inventory plan review before scale. [[components/retailcase_ni061_group_queue_20261012]].",s)
p.write_text(s+"\n12.10.2026 checkpoint680: repaired question-mark loss introduced by PowerShell stdin encoding in recent maintained wiki notes; source files/raw evidence preserved. Future Russian edits use UTF-8 file-backed scripts.\n",encoding="utf-8")
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.md");s=p.read_text(encoding="utf-8").replace("**Текущий — [NI06.2](execution/active/ni06_2.md);","**Текущий — [NI06.1](execution/active/ni06_1.md);")
p.write_text(s,encoding="utf-8")
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md")
s=p.read_text(encoding="utf-8")
s="\n".join("667–676: whole group UNIT/BOX/PALLET through existing root; shared direct-mode validator uses physical UID. Actual673 P3H0 each/six oldunits/ninecodes/oneTOP/rollback/replay and HTTP675 PASS. Partial/browser/hardware/real ACK remain. [[database/retailcase_ni061_group_aggregation_20261012]]." if line.startswith("667")and "???"in line else line for line in s.splitlines())+"\n"
p.write_text(s,encoding="utf-8")
