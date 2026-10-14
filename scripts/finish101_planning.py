from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-10_ni063_tare_assembly/002_planning.sql");s=p.read_text(encoding="utf-8-sig")
s=s.replace(" procedure require_case(p_task number,p_ware number,p_type number);"," function case_booking(p_task number,p_ware number,p_type number) return varchar2;\n procedure require_case(p_task number,p_ware number,p_type number);",1)
s=s.replace(" procedure require_case(p_task number,p_ware number,p_type number) is"," function case_booking(p_task number,p_ware number,p_type number) return varchar2 is",1)
s=s.replace("depth number:=0;","depth number:=0;v_book varchar2(100);",1)
s=s.replace("if n=1 then return;end if;","if n=1 then select OPERATION_ID into v_book from RRL_TARE_BOOK where PLACE_KIND='CASE' and PLACE_ID=to_char(p_task,'TM9') and OWNER_WARE_ID=p_ware and PALLET_TYPE_ID=p_type and STATUS='HELD';return v_book;end if;",1)
s=s.replace("exception when no_data_found then raise_application_error(-20886,'CASE_ASSEMBLY_GOOD_TARE_BOOK_REQUIRED');end;","exception when no_data_found then return null;end;",1)
s=s.replace("if n!=1 then raise_application_error(-20886,'CASE_ASSEMBLY_GOOD_TARE_BOOK_REQUIRED');end if;\n end;","if n!=1 then return null;end if;\n select OPERATION_ID into v_book from RRL_TARE_BOOK where PLACE_KIND='HU' and PLACE_ID=parent_uid and OWNER_WARE_ID=p_ware and PALLET_TYPE_ID=p_type and STATUS='HELD';return v_book;\n end;\n procedure require_case(p_task number,p_ware number,p_type number) is\n begin if case_booking(p_task,p_ware,p_type) is null then raise_application_error(-20886,'CASE_ASSEMBLY_GOOD_TARE_BOOK_REQUIRED');end if;end;",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8-sig")+'''
from .contracts_tare_assembly import TareAssemblyPort,tare_assembly_service
from .api.tare_assembly_routes import router as tare_assembly_router
from .infrastructure.tare_assembly import TareAssembly,case_snapshot as existing_case_tare_snapshot

def build_tare_assembly(gateway: Any) -> TareAssemblyPort:
    return TareAssembly(gateway)
''';out[str(p)]=s
p=Path("api/wms_api_server/app/tare_composition.py");s=p.read_text(encoding="utf-8-sig")+'''
from .modules.inventory.public import TareAssemblyPort,build_tare_assembly

def build_tare_for_assembly() -> TareAssemblyPort:
    return build_tare_assembly(OracleGateway())
''';out[str(p)]=s
p=Path("api/wms_api_server/app/main.py");s=p.read_text(encoding="utf-8-sig")+'''
from .modules.inventory.public import tare_assembly_router,tare_assembly_service
from .tare_composition import build_tare_for_assembly
app.include_router(tare_assembly_router)
app.dependency_overrides[tare_assembly_service]=build_tare_for_assembly
''';out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8-sig").replace('{"TARE_DAMAGE",','{"TARE_BOOK", "TARE_BOOK_CANCEL", "TARE_DAMAGE",');out[str(p)]=s
p=Path("api/wms_api_server/app/services/case_pick_service.py");s=p.read_text(encoding="utf-8-sig")
needle="        return task\n";assert s.count(needle)==1
s=s.replace(needle,"        from ..modules.inventory.public import existing_case_tare_snapshot\n        task['tare']=existing_case_tare_snapshot(self.gateway,case_pick_task_id)\n"+needle)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
