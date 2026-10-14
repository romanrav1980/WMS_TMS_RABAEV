"""Expose existing transport tariff sources without invoking mutating price functions."""
import json
from hashlib import sha256
from typing import Any
from ..contracts import LogisticsCostError
from .cost_access import require_warehouse
from ...platform.public import read_oracle_json


def transport_tariff_sources(gateway: Any,trip: int,ware: int,actor: str)->dict[str,Any]:
    with gateway.transaction("Read existing transport tariff sources")as cursor:
        cursor.execute("set transaction read only")
        require_warehouse(cursor,ware,actor,"transport_dispatch_view")
        cursor.execute("select distinct WARE_ID from RRL_TT_HU_LOAD_FACT where TT_ID=:trip union select distinct WARE_ID from RRL_SBORKA_PALLETS where TRANSTASK_ID=:trip",trip=trip)
        warehouses=[int(row[0])for row in cursor.fetchall()if row[0]is not None]
        if not warehouses or ware not in warehouses or len(warehouses)>200:
            raise LogisticsCostError("COST_TRIP_WAREHOUSE_SOURCE_REQUIRED","Нет источника рейса на выбранном складе")
        for source_ware in sorted(warehouses):
            require_warehouse(cursor,source_ware,actor,"transport_dispatch_view")
        cursor.execute("""select t.TRANSTYPE,t.TRANSPORT,t.CONDITION,v.DOVERENNOST_OT,
        to_char(t.PRICE,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
        to_char(t.HOURS,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),RRL_GET_TT_PRICE_ID(t.ID)
        from RRL_TRANSPORT_TASK t left join RRL_TR_VODITEL v on v.ID=t.VODITEL_ID
        where t.ID=:trip""",trip=trip)
        rows=cursor.fetchall()
        if len(rows)!=1:
            raise LogisticsCostError("COST_TRIP_SOURCE_AMBIGUOUS","Неоднозначный рейс или водитель")
        vehicle_type,vehicle,state,company,current_price,hours,region_key=rows[0]
        cursor.execute("""select p.ID,p.PRICE_NAME,p.COMPANY,p.TYPE_TR,
        to_char(p.PRICE,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
        to_char(p.PRICE_FOR_HOURS,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
        to_char(p.PRICE_FOR_ADDR,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
        to_char(p.NORM_HOURS,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')
        ,h.RESULT_JSON from RRL_TRANSPORT_PRICE p
        left join RRL_TRANSPORT_NORM_HEAD nh on nh.SOURCE_PRICE_ID=p.ID and nh.WARE_ID=:ware
        left join RRL_TRANSPORT_NORM_HISTORY h on h.SOURCE_PRICE_ID=nh.SOURCE_PRICE_ID and h.VERSION_NO=nh.VERSION_NO
        where (p.COMPANY=:company or p.COMPANY='DEFAULT')and
        (p.PRICE_NAME=:region_key or p.PRICE_NAME=:type_key)
        order by p.ID,p.PRICE_NAME,p.COMPANY fetch first 101 rows only""",
                       ware=ware,company=company,region_key=region_key,type_key="["+str(vehicle_type)+"]")
        candidates=cursor.fetchall()
        if len(candidates)>100:
            raise LogisticsCostError("COST_TARIFF_SOURCE_BOUND","Не более 100 подходящих исходных тарифов")
        result=[]
        for values in candidates:
            names=("id","price_name","company","vehicle_type","vehicle_rate","hour_rate","point_rate","norm_hours")
            row=dict(zip(names,values[:8]))
            row["source_hash"]=sha256(json.dumps(row,sort_keys=True,separators=(",",":")).encode()).hexdigest()
            row["match_kind"]=("REGION"if row["price_name"]==region_key else "VEHICLE_TYPE")+("_CARRIER"if row["company"]==company else "_DEFAULT")
            row["published_norm"]=read_oracle_json(values[8])if values[8]is not None else None
            result.append(row)
        cursor.execute("""select count(*),count(distinct r.STORE_ADDR)from RRL_STORE_RECEIPT_FACT r
        join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID
        join RRL_STOCK_OPERATION op on op.OPERATION_ID=r.OPERATION_ID and op.STATE='APPLIED'
        where l.TT_ID=:trip""",trip=trip)
        receipt_count,receipt_addresses=cursor.fetchone()
        return {"trip_id":trip,"warehouse_id":ware,"source_warehouses":sorted(warehouses),
                "vehicle":vehicle,"vehicle_type":vehicle_type,"carrier":company,"trip_state":state,
                "legacy_region_key":region_key,"current_carrier_price":current_price,"recorded_hours":hours,
                "candidates":result,"selection_state":"CONFIGURATION_REQUIRED"if result else "TARIFF_SOURCE_MISSING",
                "actual_receipt_count":receipt_count,"receipt_address_count":receipt_addresses,
                "receipt_addresses_are_not_unloading_method_proof":True,
                "missing_contract_fields":["currency","effective_period","vehicle_dimensions","actual_unloading_method","loader_fact"],
                "tariff_selected":False,"price_changed":False,"cost_posted":False,"stock_changed":False}
