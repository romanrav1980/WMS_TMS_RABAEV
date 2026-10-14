import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/finance/contracts.py");v=p.read_text(encoding="utf-8");needle="    def invoice_summary"
a=v.index(needle)
v=v[:a]+"    def transport_tariff_sources(self,trip: int,ware: int,actor: str)->dict[str,Any]: ...\n"+v[a:]
out[str(p)]=v
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");v=p.read_text(encoding="utf-8")
a=v.index("    def rate(")
v=v[:a]+'''    def transport_tariff_sources(self,trip: int,ware: int,actor: str)->dict[str,Any]:
        from .transport_tariff_sources import transport_tariff_sources
        return transport_tariff_sources(self.gateway,trip,ware,actor)

'''+v[a:];out[str(p)]=v
p=Path("api/wms_api_server/app/modules/finance/api/logistics_cost_routes.py");v=p.read_text(encoding="utf-8")
v+='''\n@router.get("/trips/{trip_id}/transport-tariff-sources")
def transport_tariff_sources(trip_id: int,warehouse_id: int=Query(gt=0),
                             user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                             service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    try:return service.transport_tariff_sources(trip_id,warehouse_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc
'''
out[str(p)]=v
out["wiki/database/nicora_ni071_transport_tariff_sources_20261012.md"]='''# NI07.1: действующие транспортные тарифы
523–526: live RRL_GET_TT_PRICE и RRL_UPDATE_PRICE — транспортная стоимость; RRL_GET_TT_PRICE_ID читает региональный ключ. RRL_GET_TT_PRICE меняет PAY_REGION/ADDR_PREMIO, затем RRL_UPDATE_PRICE меняет PRICE. Не вызывать их как readonly SELECT.
**Противоречие прежнему ТЗ биллинга:** live TRANSPORT_TASK.stoim_tt суммирует stoim_pall_sb, то есть стоимость товаров по приходной/последней цене; это не сумма тарифа перевозки. Источник524 сохранён tmp/price524.json. Требуется исправить это описание; код valuation не заменять транспортными ставками.
RRL_TRANSPORT_PRICE уже содержит автомобильную/часовую/адресную ставку, компанию, тип машины и региональный PRICE_NAME. Эта таблица пуста в dev525. RRL_TRANSPORT_NORMS содержит длительности, не денежные тарифы.
Добавлен readonly GET /api/finance/logistics-costs/trips/{trip}/transport-tariff-sources?warehouse_id=... . Current rights and every source warehouse checked in one consistent snapshot. Candidates are bounded100, exact decimals/source hashes/match origin explicit; no arbitrary rownum1 or automatic selection. No price, monetary outbox or stock effect.
Actual receipt/address counts are labelled separately; they do not prove actual unloading method or loader work. Existing tariff lacks currency/effective period/vehicle dimensions/unload and loader facts, so source state remains CONFIGURATION_REQUIRED or TARIFF_SOURCE_MISSING.
Next implementation: publish immutable versions anchored in existing tariff rows; actual unloading facts behind existing store/driver command owners; once-only vehicle/point/unload recognition. No zero-price fallback or assumed currency/method.
'''
for name,text in [
("wiki/index.md","- [Транспортный тариф: правильный источник](database/nicora_ni071_transport_tariff_sources_20261012.md): valuation stoim_tt differs from carrier tariff; existing PRICE catalog/readonly source candidates, no arbitrary fee.\n"),
("wiki/log.md","\n12Oct523–526: inspected live transport tariff sources without mutation. Found billingTZ contradiction: stoim_tt is goods valuation; transport fee uses GET_TT_PRICE/UPDATE_PRICE with side effects/ambiguous rownum1. Reused existing PRICE catalog via bounded current-scope source API, exact amounts/hashes; no monetary charge or stock effect. Next immutable norm publication and actual unload fact.\n")]:
 p=Path(name);old=p.read_text(encoding="utf-8");out[str(p)]=text+old if name=="wiki/index.md"else old+text
p=Path("wiki/requirements/transport_billing_tz.md");v=p.read_text(encoding="utf-8")
v="> Уточнение по live Oracle, 12.10.2026: [[../database/nicora_ni071_transport_tariff_sources_20261012]]. TRANSPORT_TASK.stoim_tt — стоимость товаров; фактический пересчёт тарифной цены вызывает RRL_UPDATE_PRICE → RRL_GET_TT_PRICE. Раздел7 ниже — историческое описание, противоречие сохранено явно; не использовать goods valuation как перевозку.\n\n"+v;out[str(p)]=v
print(json.dumps(out))
