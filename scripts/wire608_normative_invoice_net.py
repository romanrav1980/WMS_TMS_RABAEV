from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py");v=p.read_text(encoding="utf-8")
a='cursor.execute("""select r.RESULT_JSON from RRL_LOGISTICS_COST_RUN r\n         join RRL_TRANSPORT_COST_CLAIM'
b='cursor.execute("""select r.RESULT_JSON,to_char(RRL_NORM_COST_CORRECTION.confirmed_total(r.OPERATION_ID),\'TM9\',q\'[NLS_NUMERIC_CHARACTERS=\'.,\']\')from RRL_LOGISTICS_COST_RUN r\n         join RRL_TRANSPORT_COST_CLAIM'
assert a in v;v=v.replace(a,b,1)
v=v.replace('items=[read_oracle_json(row[0])for row in rows]\n        totals={}','items=[{**read_oracle_json(row[0]),"confirmed_total":row[1]}for row in rows]\n        totals={};confirmed_totals={}')
v=v.replace('totals[code]=totals.get(code,Decimal(0))+value','totals[code]=totals.get(code,Decimal(0))+value\n                confirmed=Decimal(item["confirmed_total"])\n                if not confirmed.is_finite()or confirmed<0:raise LogisticsCostError("NORMATIVE_CONFIRMED_TOTAL_INVALID","Некорректный подтверждённый итог")\n                confirmed_totals[code]=confirmed_totals.get(code,Decimal(0))+confirmed')
v=v.replace('{"currency":code,"amount":format(value,"f")}','{"currency":code,"amount":format(value,"f"),"confirmed_amount":format(confirmed_totals[code],"f")}')
p.write_text(v,encoding="utf-8")
p=Path("admin/wms_admin_frontend/src/features/finance/BillingTransportCosts.tsx");v=p.read_text(encoding="utf-8")
v=v.replace('total:string;currency:string;','total:string;confirmed_total:string;currency:string;')
v=v.replace('currency:string;amount:string}>','currency:string;amount:string;confirmed_amount:string}>')
v=v.replace('{t.amount} {t.currency} ·','Исходно {t.amount}, с корректировками {t.confirmed_amount} {t.currency} ·')
v=v.replace('{item.total} {item.currency}, норма','исходно {item.total}, с корректировками {item.confirmed_total} {item.currency}, норма')
p.write_text(v,encoding="utf-8")
print("608 invoice separates original and current confirmed normative totals without adding carrier invoice price.")
