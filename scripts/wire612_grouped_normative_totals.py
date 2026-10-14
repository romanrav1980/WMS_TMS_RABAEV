from pathlib import Path
p=Path("api/wms_api_server/app/modules/finance/infrastructure/transport_cost_read.py");v=p.read_text(encoding="utf-8")
v=v.replace('from .cost_access import require_warehouse','from .cost_access import require_warehouse\nfrom .normative_totals_read import confirmed_totals')
v=v.replace("select r.RESULT_JSON,to_char(RRL_NORM_COST_CORRECTION.confirmed_total(r.OPERATION_ID),'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']')from RRL_LOGISTICS_COST_RUN r","select r.RESULT_JSON from RRL_LOGISTICS_COST_RUN r")
v=v.replace('items=[{**read_oracle_json(row[0]),"confirmed_total":row[1]}for row in rows]',
'''items=[read_oracle_json(row[0])for row in rows]
        current=confirmed_totals(cursor,{item["operation_id"]:item["total"]for item in items})
        items=[{**item,"confirmed_total":current[item["operation_id"]]}for item in items]''')
v=v.replace('select r.OPERATION_ID,r.TT_ID,r.CURRENCY,json_value(r.RESULT_JSON,\'$.total\'),\n         to_char(RRL_NORM_COST_CORRECTION.confirmed_total(r.OPERATION_ID),\'TM9\',q\'[NLS_NUMERIC_CHARACTERS=\'.,\']\')',
'select r.OPERATION_ID,r.TT_ID,r.CURRENCY,json_value(r.RESULT_JSON,\'$.total\')')
v=v.replace('return [{"operation_id":op,"trip_id":trip,"currency":currency,"original_total":original,"confirmed_total":current}for op,trip,currency,original,current in rows]',
'''current=confirmed_totals(cursor,{op:original for op,trip,currency,original in rows})
        return [{"operation_id":op,"trip_id":trip,"currency":currency,"original_total":original,"confirmed_total":current[op]}for op,trip,currency,original in rows]''')
p.write_text(v,encoding="utf-8")
print("612 invoice/latest-source totals use one scoped indexed grouped sum, native authorisation/CAS writer unchanged.")
