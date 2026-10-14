from pathlib import Path
import json
files={}
p=Path("api/wms_api_server/app/modules/fulfillment/domain/automatic_layout.py");s=p.read_text(encoding="utf-8").replace(" / 1_000_000"," / 1_000_000_000");files[str(p)]=s
p=Path("scripts/check1116_auto_layout.py");s=p.read_text(encoding="utf-8").replace('["40","30","20"]','["400","300","200"]');files[str(p)]=s
p=Path("wiki/components/nicora_ni021_auto_preparation_20261013.md");s=p.read_text(encoding="utf-8").replace("Объём считается из исторических DIMKORcm и переводится вм³ точно.","Объём считается из действующего DIMKOR в миллиметрах (article_logistics/тест271:40cm→400mm), произведение переводится вм³ делением на10^9. Архив2011 не доказывает единицы действующей карточки; первоначальное предположение оcm исправлено до runtime записи.")
s+="\n1117: расчёт/API/shared writer/UI реализованы; live позитив/повтор/конкуренция ещё ожидают. Command блокирует source/config, затем RRL_COMPL_SEQ SHARE WAIT3 (включая отсутствующие строки), затем карточки SKU в стабильном порядке, затем legacy ORDERS. Manual использует тот же порядок; cached result возвращается до блокировок справочника. Короткое глобальное ограждение sequence требуется из-за отсутствия уникальной карты/version; владелец fulfillment, замена на версионированный scope при росте contention.\n"
files[str(p)]=s
p=Path("wiki/index.md");files[str(p)]="- [NI02.1 implementation1117](components/nicora_ni021_auto_preparation_20261013.md): расчёт/API/UI, actual mm→m³, locks/shared writer; live acceptance pending.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 /1117: новый automatic_layout/AutomaticPreparation, auto preview/run/resolve, общий legacy writer, форма и durable intent. Архитектура698/0cycles/76debt PASS; exact domain cases PASS. Исправлено предположение единиц: действующий SAP mapping хранит DIMKORmm, объём /10^9. Позитивная live запись ещё не выполнена,2047 отвергается по норме1<коробки24.\n"
print(json.dumps(files,ensure_ascii=True))
