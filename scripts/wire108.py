from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/public.py");out[str(p)]=p.read_text(encoding="utf-8-sig")+'''
from .contracts_supplier_return import SupplierReturnPort,supplier_return_service
from .api.supplier_return_routes import router as supplier_return_router
from .infrastructure.supplier_return import SupplierReturn

def build_supplier_return(gateway: Any) -> SupplierReturnPort:
    return SupplierReturn(gateway)
'''
out["api/wms_api_server/app/supplier_return_composition.py"]='''from .oracle_gateway import OracleGateway
from .modules.inventory.public import SupplierReturnPort,build_supplier_return

def build_supplier_return_service() -> SupplierReturnPort:
    return build_supplier_return(OracleGateway())
'''
p=Path("api/wms_api_server/app/main.py");out[str(p)]=p.read_text(encoding="utf-8-sig")+'''
from .modules.inventory.public import supplier_return_router,supplier_return_service
from .supplier_return_composition import build_supplier_return_service
app.include_router(supplier_return_router)
app.dependency_overrides[supplier_return_service]=build_supplier_return_service
'''
p=Path("api/wms_api_server/app/modules/inventory/api/supplier_return_routes.py");s=p.read_text(encoding="utf-8-sig").replace("def failure(exc: StoreReturnReceiveError)","def failure(exc: StoreReturnReceiveError,operation_id: str|None=None)",1).replace('"outcome_confirmed":exc.status==409','"operation_id":operation_id,"outcome_confirmed":exc.status==409',1).replace("except StoreReturnReceiveError as exc:raise failure(exc) from exc","except StoreReturnReceiveError as exc:raise failure(exc,body.operation_id) from exc",1);out[str(p)]=s
p=Path("db/migrations/2026-10-10_ni062_supplier_dispatch/005_guards.sql");s=p.read_text(encoding="utf-8-sig")+r"""
create or replace trigger RRL_SUP_RETURN_ST_SOURCE_GUARD before update of PALLET_UID,WARE_ID,RETURN_SUPPLIER_ID on RRL_SBORKA_PALLETS for each row
declare n number;
begin
 if nvl(:new.PALLET_UID,'~')=nvl(:old.PALLET_UID,'~')and nvl(:new.WARE_ID,-1)=nvl(:old.WARE_ID,-1)and nvl(:new.RETURN_SUPPLIER_ID,'~')=nvl(:old.RETURN_SUPPLIER_ID,'~')then return;end if;
 select count(*)into n from RRL_STORE_RETURN_SUP_BIND where ST_ID=:old.ID;
 if n!=0 then raise_application_error(-20863,'SUP_RETURN_PREPARED_SOURCE_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_SUP_RETURN_ROWS_SOURCE_GUARD before insert or delete or update of PALLET_UID,ARTICUL,EI,QUANTITY on RRL_SBORKA_PALLET_ROWS for each row
declare n number;
begin
 if updating and nvl(:new.PALLET_UID,'~')=nvl(:old.PALLET_UID,'~')and nvl(:new.ARTICUL,'~')=nvl(:old.ARTICUL,'~')and nvl(:new.EI,'~')=nvl(:old.EI,'~')and nvl(:new.QUANTITY,-1)=nvl(:old.QUANTITY,-1)then return;end if;
 select count(*)into n from RRL_STORE_RETURN_SUP_BIND where ST_IDENTIFIER=:new.PALLET_UID or ST_IDENTIFIER=:old.PALLET_UID;
 if n!=0 then raise_application_error(-20863,'SUP_RETURN_PREPARED_ROWS_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_STORE_SUPPLIER_CARGO_GUARD before insert on RRL_STORE_RECEIPT_FACT for each row
declare n number;
begin
 select count(*)into n from RRL_TT_HU_LOAD_ST m join RRL_SBORKA_PALLETS st on st.ID=m.SBORKA_PALLET_ID where m.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and st.RETURN_SUPPLIER_ID is not null;
 if n!=0 then raise_application_error(-20886,'STORE_RECEIPT_SUPPLIER_CARGO_NOT_ALLOWED');end if;
end;
/
"""
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
