from pathlib import Path
root=Path('api/wms_api_server/app')
p=root/'modules/inventory/infrastructure/interwarehouse.py';s=p.read_text(encoding='utf-8')
start=s.find('                composition = json.dumps(')
end=s.index('                cur.execute("""insert into RRL_INTERWARE_PLAN',max(start,0))
if start>=0:s=s[:start]+'                cur.setinputsizes(result_body=oracledb.DB_TYPE_CLOB,arrival=oracledb.DB_TYPE_TIMESTAMP_TZ,ready=oracledb.DB_TYPE_TIMESTAMP_TZ)\n'+s[end:]
p.write_text(s,encoding='utf-8')
p=root/'modules/inventory/public.py';s=p.read_text(encoding='utf-8')
if 'def build_interwarehouse(' not in s:
 p.write_text(s+'\nfrom .contracts_interwarehouse import InterwarehousePort,interwarehouse_service\nfrom .api.interwarehouse_routes import router as interwarehouse_router\nfrom .infrastructure.interwarehouse import Interwarehouse\n\ndef build_interwarehouse(gateway: Any) -> InterwarehousePort:\n    return Interwarehouse(gateway)\n',encoding='utf-8')
p=root/'main.py';s=p.read_text(encoding='utf-8')
if 'app.include_router(interwarehouse_router)' not in s:
 p.write_text(s+'\nfrom .modules.inventory.public import interwarehouse_router,interwarehouse_service\nfrom .interwarehouse_composition import build_interwarehouse_service\napp.include_router(interwarehouse_router)\napp.dependency_overrides[interwarehouse_service]=build_interwarehouse_service\n',encoding='utf-8')
p=Path('db/migrations/2026-10-10_ni061_two_legs/002_guards.sql');s=p.read_text(encoding='utf-8')
needle=" select count(*)into n from RRL_STORE_RECEIPT_FACT"
extra=""" select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID and ACTIVE_FLAG=1;
 if n!=1 then raise_application_error(-20886,'INTERWARE_SINGLE_ST_REQUIRED');end if;
 select count(*)into n from RRL_REMAINS where UID_POLETA=:new.ROOT_UID and(nvl(REMAIN,0)!=0 or nvl(HARD_RESERVED_BASE,0)!=0);
 if n!=0 then raise_application_error(-20886,'INTERWARE_SOURCE_STOCK_ALREADY_PRESENT');end if;
 select count(*)into n from RRL_PALLETS p where p.UID_PALLET=:new.ROOT_UID and(
 exists(select 1 from RRL_SKU_RECEIPT_PROFILE m where m.ARTICUL=p.ARTICUL)or
 exists(select 1 from RRL_SKU_RECEIPT_POLICY m where m.ARTICUL=p.ARTICUL and m.MARKING_REQUIRED=1)or
 exists(select 1 from RRL_FINISHED_GOODS_SKU m where m.ARTICUL=p.ARTICUL and m.CRPT_REQUIRED=1));
 if n!=0 then raise_application_error(-20886,'INTERWARE_MARKED_UNIT_FLOW_REQUIRED');end if;
 if nvl(json_value(:new.SOURCE_COMPOSITION_JSON,'$.physical_unit_count' returning number),0)!=0 or
 nvl(json_value(:new.SOURCE_COMPOSITION_JSON,'$.leaf_count' returning number),0)!=1 or
 nvl(json_value(:new.SOURCE_COMPOSITION_JSON,'$.top_place_count' returning number),0)!=1 then
 raise_application_error(-20886,'INTERWARE_SINGLE_ORDINARY_PLACE_REQUIRED');end if;
"""
if 'INTERWARE_SINGLE_ORDINARY_PLACE_REQUIRED' not in s:p.write_text(s.replace(needle,extra+needle,1),encoding='utf-8')
