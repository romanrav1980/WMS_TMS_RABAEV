from pathlib import Path
import json
p=Path("api/wms_api_server/app/services/picking_service.py");s=p.read_text(encoding="utf-8")
a=s.index("    def get_wave_header(");b=s.index("    def get_wave(self,",a);part=s[a:b]
lines=part.splitlines();header="from typing import Any\n\n\ndef read_wave_header(gateway: Any, pick_wave_id: int) -> dict[str, Any] | None:\n"
body='\n'.join(line[4:]if line.startswith('    ')else line for line in lines[1:]).replace('self.gateway','gateway')
module=header+body+'\n'
service=s[:a]+"""    def get_wave_header(self, pick_wave_id: int) -> dict[str, Any] | None:
        from ..modules.inventory.public import existing_wave_header
        return existing_wave_header(self.gateway,pick_wave_id)

"""+s[b:]
pub=Path("api/wms_api_server/app/modules/inventory/public.py")
files={str(p):service,"api/wms_api_server/app/modules/inventory/infrastructure/wave_header.py":module,str(pub):pub.read_text(encoding="utf-8")+"\nfrom .infrastructure.wave_header import read_wave_header as existing_wave_header\n"}
print(json.dumps(files,ensure_ascii=True))
