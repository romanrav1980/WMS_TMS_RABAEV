import json
from pathlib import Path
out={}
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.md");s=p.read_text(encoding="utf-8")
s=s.replace("**Revision 12, 11 октября 2026 года.**","**Revision 17, 12 октября 2026 года.**",1)
s=s.replace("**Текущий — [NI08.1](execution/active/ni08_1.md), in_progress; зависимые доработки NI05.2 и сверки NI07.2 выполняются на существующих владельцах**.","**Текущий — [NI07.1](execution/active/ni07_1.md); реализованные части остальных спринтов и открытый остаток отражены в JSON и последних ticket-записях.**",1)
s=s.replace("Следующий конкретный пробел NI06.1 — marked source:","Исторический пробел на этапе217–224 (закрыт последующими284–447) — marked source:")
section="""
## Фактическое обновление 12 октября, revision17

Новые изменения используют действующие WMS/TMS и RABAEV. Зафиксированы конкретные рабочие цепочки, полного завершения всех18 спринтов нет. Реализован и адресно подтверждён NI03.1; остальные17 содержат реализованные части и открытый объём.

| Спринт | Последний реализованный результат | Открытый остаток |
|---|---|---|
| NI06.1 | Два плеча многотоварного места: original ST → whole HU receipt → task → existing onward ST/load/depart → buyer3 по каждому SKU; repeated physical loss/recovery сохраняет ключи | Partial/aggregate-only groups, temperature decisions/rerouting, detached loading/high-leaf batching |
| NI04.3 | Локальная отмена исходной коробки/родителей; immutable journal/current-origin scan guard; quantity/codes preserved | Новая юридическая агрегация, остальные scan flows, real adapters/ACK |
| NI06.2 | REFUSED1 → supplier existingST/QC/load/depart; DAMAGED1 → independent disposal; existing custody/receipt/PUT; original buyer3/missing2 unchanged | Aggregate-only/multi-place custody, quality inspection for REUSE, real ERP/Gov decisions |
| NI07.1 | Same-last-period norm revisions/native date-version choice; BOX1 charge3/v2 frozen; exact scoped invoice/trip grouping | Ordinary BOX assembly clock, multiple assembly days inside one load, remaining norms/real financial ERP |

Остальные карточки не снимаются с плана из-за отсутствия новых записей в этой таблице. Их существующие implementedSlices сохраняются. Следующее функциональное действие: NI07.1 — достоверный источник сборки ordinary BOX, затем несколько расчётных дат CASE в одном load с единственным начислением источника; до реализации такой mixed load расчёт явно отказывается. Затем NI06.1/NI06.2 оставшиеся способы маркировки и custody, NI06.3 тара, NI07.2 закрытие и NI08.1 реальные ограничения.

Данные о стране/режиме водителей, окончательные SAP/XML и государственные сервисы должны подтверждаться реальными конфигурациями. TEST, PENDING, локальный journal и авторские случаи не заменяют внешний ACK или независимую приёмку. Последние задания Qwen подготовлены в каталогах NI04.3/NI06.2/NI07.1. Публикации GitHub не было.

Доказательства: [group delivery](../../database/retailcase_ni061_group_delivery_20261012.md), [aggregation lifecycle](../../database/retailcase_ni043_aggregation_lifecycle_20261012.md), [exception returns](../../database/retailcase_ni062_exception_returns_20261012.md), [financial revisions/summary](../../database/retailcase_ni071_revision_summary_20261012.md). API509 current, live Oracle VALID, protectedP20/H20 retained; saved return receipts replay after completed supplier/disposal, finance trip summary3GEL.
"""
s=s.replace("## Закрытый технический этап",section+"\n## Закрытый технический этап",1);out[str(p)]=s
p=Path("wiki/index.md");out[str(p)]="- [Актуальный план RETAILCASE, revision17](requirements/retailcase_delivery_v55/implementation_plan.md):12Oct18increments/1addressed-implemented+17remaining; group delivery, aggregation cancellation, exception returns, period revision+invoice summary.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n-12.10.2026 509–510: living MD synchronized to JSONrevision17, currentNI07.1; historical marked interwarehouse blocker explicitly superseded by284–447. Eighteen increments retained, no false full completion. API509 latest actualtrip3GEL/old returns replay after supplier/disposal/buyer3/caps unchanged/liveVALID/protected20.\n"
print(json.dumps(out))
