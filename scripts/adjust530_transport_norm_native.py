import json
from pathlib import Path
p=Path("db/migrations/2026-10-12_ni071_transport_norms/002_norm_api.sql")
v=p.read_text(encoding="utf-8")
a=v.index("  begin\n   select REQUEST_JSON")
b=v.index("  currency_value:=",a)
saved=v[a:b]
needle="  select *into price from RRL_TRANSPORT_PRICE where ID=price_id for update;\n"
assert v.count(needle)==1
v=v.replace(needle,needle+"  -- Same-op sender may have waited for another transaction to commit.\n"+saved)
v=v.replace("price.PRICE_FOR_ADDR<0 or price.PRICE_NAME", """price.PRICE_FOR_ADDR<0 or price.PRICE>=1e18 or price.PRICE_FOR_HOURS>=1e18 or price.PRICE_FOR_ADDR>=1e18 or
   price.PRICE*1e9!=trunc(price.PRICE*1e9)or price.PRICE_FOR_HOURS*1e9!=trunc(price.PRICE_FOR_HOURS*1e9)or
   price.PRICE_FOR_ADDR*1e9!=trunc(price.PRICE_FOR_ADDR*1e9)or price.PRICE_NAME""")
out={str(p):v}
out["wiki/database/retailcase_ni071_transport_norms_20261012.md"]='''# NI07.1: публикация норм из существующего тарифа
Подготовлено529–530, применение ожидается.
Finance owner; существующая RRL_TRANSPORT_PRICE сохраняется единственным источником автомобильной/часовой/адресной ставки. Публикация снимает точный snapshot конкретной строки ID; неоднозначный ID/нет ставки/неверный тип отказаны. Новая таблица цен не создаётся, legacy строки/PRICE рейса не изменяются.
RRL_TRANSPORT_NORM_HEAD/HISTORY сохраняют склад, версию, исходную строку, operation, actor, действующую дату, явную валюту/часовой пояс/тип/класс машины и отдельные ставки rolling/manual unload/loader. Reason/reference обязательны. История immutable, native guarded writer. Публикация не есть начисление и не заменяет реальные факты выгрузки.
Одна короткая транзакция: lock original price row → recheck saved operation → head/history. Одинаковый operation+JSON+actor returns original result, изменённый payload отказан; версия current. При конфликте unique operation savepoint rollback снимает спекулятивную версию перед чтением победителя. Late rollback не затрагивает caller work до savepoint. Legacy источник без FK/PK проверяется exact single-row SELECT FOR UPDATE; дубль ID не выбирается произвольно.
Миграция2026-10-12-529-versioned-existing-transport-norms; additive2 tables/index/package/guards only, original tariff data untouched. Rollback разрешён без history, иначе forward repair.
Next: typed publish API and bounded current reads; isolated legacy row positive publication/concurrency/replay/rollback. Actual unload/loader evidence and money recognition remain next functional tickets.
'''
for name,entry in [
("wiki/index.md","- [Публикация транспортных норм](database/retailcase_ni071_transport_norms_20261012.md): checkpoint529–530, snapshot existing tariff/current version/period/currency/size/unload; apply pending.\n"),
("wiki/log.md","\n12Oct529–530 checkpoint: prepared additive immutable norm publication anchored to existing price row, no legacy tariff/TTPRICE/stock mutation. Same source row serialisation and saved-op recheck, collision savepoint rollback, future monetary/unload facts separate.\n")]:
 p=Path(name);v=p.read_text(encoding="utf-8");out[str(p)]=entry+v if name=="wiki/index.md"else v+entry
print(json.dumps(out))
