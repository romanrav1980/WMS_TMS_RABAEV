from pathlib import Path
import json
files={}
report="reports/nicora/2026-10-13/51-ni041-hu-tree-and-scan.md"
files[report]="""# NI04.1 — дерево вложенности и отдельный физический скан
2026-10-14. Развивается существующий warehouse-hus, существующие HU read/commands/журнал; таблиц и второго расчёта состава нет.

## Функционал
Дерево строится по серверным links/root/nodes: внешний контейнер, CASE и товарные листья. Выбор узла показывает идентификаторы, ячейку, версию, количество и резерв. Доступны переходы к составу вложенного контейнера/CASE, внешнему родителю и текущим физическим единицам/кодам партии. Итоги по артикулам берутся из серверного quantities, единицы не смешиваются.
Исходная таблица сохранена в раскрываемом блоке. Историческая отгрузка визуально отделена от текущего состава; действия изменения исторического места отключены.
Смена идентификатора очищает прежнее дерево/таблицу и отключает действия до нового чтения.
Отдельное поле «Скан внешнего грузового места» теперь обязательно для создания, упаковки, вскрытия и движения. Переход по ссылке или выбор узла не заполняют этот скан. Native expected_version, child scan, slot scan, measurements и durable retry прежние.

## Адресное evidence
Реальное чтение HU1069:4bb85f1f15 → CASE1131 → CASELOT с12EA. Переход к CASE показывает внешний родитель; исторический SMALL514.HU:af32399b показывает сохранённый состав и блокирует изменение.
Readonly browser1366: errors=[], business POST=[].
Без отдельного скана нажатие «переместить» не отправило запрос. С заданным WRONG.SCAN.1368 отправлен именно этот scan_container; сервер ответил409 HU_MOVE_TARGET_REQUIRED, поскольку назначение совпадало с исходной ячейкой. Этот отказ подтверждает запрет такого назначения, а не отдельно native-ветку неверного скана. Исходный поиск не был использован как scan_container.
Для операции HU:9c1b6828-3f97-4c3c-917f-b9100b344f07 товарных RRL_EVENTS=0. Узлы/связи после отказа полностью равны исходным. Реальное положительное новое перемещение в этом блоке не выполнялось; ядро движения не менялось.

[Текущее дерево](screenshots/94-ni041-hu-tree.png), [историческое](screenshots/95-ni041-historical-tree.png), [интерфейс после разделения скана](screenshots/96-ni041-explicit-scan.png).
Evidence:tmp/read1365.json,result1366.json,result1368.json,verify1369.json.
SQL: существующий snapshot61.166мс/5,3223buffers; CASEsnapshot20.506мс/1,128buffers. Решение inventory: сохранить native bound200nodes/depth16, никаких дополнительных запросов при выборе узла; новые индексы не нужны, повторный анализ при регулярном>500мс.
Авторская UI-поставка, не независимая приёмка всей перепаковки/оборудования.
"""
page="wiki/components/nicora_ni041_hu_tree_20261014.md"
files[page]="# NI04.1: вложенность грузовых мест\n\n1364–1370. Существующий warehouse-hus: дерево по серверным links, карточка узла/родители/итоги, исторический режим, отдельный физический скан для команд. Выбор по ссылке не заменяет скан. Native ядро и версии не менялись.\n\n[Отчёт51](../../"+report+"): live HU1069/CASE1131/12EA, historicalSMALL514, отсутствиеPOSTбезскана, отказsame-cell/товарныхсобытий0/составсохранён. Положительное новое движение не заявлено.\n"
p=Path("wiki/index.md");files[str(p)]="- [NI04.1: дерево и скан1370](components/nicora_ni041_hu_tree_20261014.md): визуальная вложенность/история/отдельный физический скан, report51.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 ·1370: HU tree/UI separate physical scan, report51; live/history readonly and no-scan prevention, native same-cell refusal leaves composition unchanged. Return gate1363 PASS739/0cycles/74debt/24tests/обаTS. Claude ACK K-0011 подтверждён C-0009.\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");d=json.loads(p.read_text(encoding="utf-8"));d["planRevision"]=65;d["currentSprint"]="NI04.2";d["firstChange"]="NI04.1 tree and physical-scan separation delivered(report51). Continue actual missing picking UI modes through existing equipment contracts. Claude C-0008 acknowledged K-0011; finance files reserved."
for item in d["increments"]:
 if item["id"]=="NI04.1":
  item.setdefault("implementedSlices",[]).append("1364–1370 existing HU hierarchy tree/card/ancestor/history/quantities; separate physical scan not filled by navigation, existing native commands preserved; report51.")
  item["remainingDeliveryWork"]="Дерево и отдельный физический скан реализованы report51; довести оставшиеся сценарии перепаковки и аппаратной работы без изменения готового ядра."
files[str(p)]=json.dumps(d,indent=2,ensure_ascii=False)+"\n"
print(json.dumps(files,ensure_ascii=True))
