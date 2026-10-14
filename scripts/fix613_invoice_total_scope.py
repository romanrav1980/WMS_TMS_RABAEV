from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py");v=p.read_text(encoding="utf-8")
v=v.replace("totals={};confirmed_totals={}","totals={};confirmed_currency_totals={}")
v=v.replace('confirmed_totals[code]=confirmed_totals.get(code,Decimal(0))+confirmed','confirmed_currency_totals[code]=confirmed_currency_totals.get(code,Decimal(0))+confirmed')
v=v.replace('format(confirmed_totals[code],"f")','format(confirmed_currency_totals[code],"f")')
p.write_text(v,encoding="utf-8")
print("613 invoice currency accumulator does not shadow grouped read function.")
