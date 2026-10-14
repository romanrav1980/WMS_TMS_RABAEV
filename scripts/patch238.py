from pathlib import Path
import json
out={};folder="db/migrations/2026-10-11_ni061_phase_timing/"
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py");s=p.read_text(encoding="utf-8");out[folder+"000_before_interwarehouse.py"]=s
a=s.index("    def queue(");s=s[:a]+"""    def queue(self, ware_id: int, actor: str) -> list[dict[str, Any]]:
        from .interwarehouse_queue import InterwarehouseQueue
        return InterwarehouseQueue(self.gateway).read(ware_id,actor)
"""
s=s.replace("            from fastapi import HTTPException\n","").replace('raise HTTPException(422,str(exc)) from exc','raise StoreReturnReceiveError("INTERWARE_SCAN_INVALID",str(exc),422) from exc');out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py");s=p.read_text(encoding="utf-8");out[folder+"000_before_interwarehouse_routes.py"]=s
needle="    except StockPostingError as exc:\n"
a=s.index(needle,s.index("def physical("));s=s[:a]+"""    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":True}) from exc
"""+s[a:];out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8");out[folder+"000_before_interwarehouse.js"]=s
a=s.index("p.textContent=");b=s.index(";return p;",a)
s=s[:b]+""";if(row.arrival_timing&&row.gate_timing)p.textContent+=" · прибытие: "+row.arrival_timing.state+" (задержка "+row.arrival_timing.delay_seconds+" с) · у ворот: "+row.gate_timing.state+" (задержка "+row.gate_timing.delay_seconds+" с). Постановка у ворот не заменяет контроль и разрешение отправления."""+s[b:]
# Existing renderer variable is r, not assumed row; adapt from its actual surrounding expression.
if ".map(r=>"in s[max(0,a-200):a]:s=s[:a]+s[a:].replace("row.arrival_timing","r.arrival_timing").replace("row.gate_timing","r.gate_timing")
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
