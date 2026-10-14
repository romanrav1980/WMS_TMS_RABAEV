from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8")
files={}
p="api/wms_api_server/app/services/picking_service.py";s=read(p)
start=s.index("    def get_wave(self, pick_wave_id:")
split=s.index('        wave = rows[0]',start)
prefix=s[start:split]
prefix=prefix.replace('def get_wave(self,','def get_wave_header(self,',1)
s=s[:start]+prefix+'        return rows[0]\n\n    def get_wave(self, pick_wave_id: int) -> dict[str, Any] | None:\n        wave = self.get_wave_header(pick_wave_id)\n        if wave is None:\n            return None\n'+s[split+len('        wave = rows[0]\n'):]
files[p]=s
p="api/wms_api_server/app/modules/inventory/public.py";files[p]=read(p)+"\nfrom .infrastructure.wave_queue_reads import WaveQueueReads\n\ndef build_wave_queue_reads() -> WaveQueueReads:\n    return WaveQueueReads(OracleGateway())\n"
p="api/wms_api_server/app/routers/picking.py";s=read(p)
s=s.replace('from ..services.picking_service import PickingService','from ..services.picking_service import PickingService\nfrom ..modules.inventory.public import build_wave_queue_reads')
start=s.index('def list_pick_waves(');end=s.index('\n\n@router.post',start)
part=s[start:end].replace('_user: AdminUser','user: AdminUser')
part=part.replace('return PickingService().list_waves(', 'return build_wave_queue_reads().waves(user.username,ware_id,lambda gateway,warehouse:PickingService(gateway).list_waves(')
part=part.replace('ware_id=ware_id,','ware_id=warehouse,')
pos=part.rfind('    )');part=part[:pos]+part[pos:].replace('    )','    ))',1)
s=s[:start]+part+s[end:]
for name,method in [('get_pick_wave','get_wave'),('get_pick_wave_readiness','get_wave_readiness'),
 ('list_pick_wave_reservations','list_wave_reservations'),('list_pick_wave_replenishment_tasks','list_wave_replenishment_tasks'),('list_pick_wave_tasks','list_wave_tasks')]:
 start=s.index('def '+name+'(');end=s.index('\n\n@router.',start)
 part=s[start:end].replace('_user: AdminUser','user: AdminUser')
 needle='PickingService().'+method+'(pick_wave_id'
 assert needle in part,name
 part=part.replace(needle,'build_wave_queue_reads().wave(pick_wave_id,user.username,lambda gateway:PickingService(gateway).'+method+'(pick_wave_id',1)
 lines=part.splitlines()
 for i,line in enumerate(lines):
  if 'build_wave_queue_reads().wave('in line:lines[i]=line+')'
 part='\n'.join(lines)
 s=s[:start]+part+s[end:]
anchor='@router.get("/waves/{pick_wave_id}")'
new='''@router.get("/waves/{pick_wave_id}/header")
def get_pick_wave_header(
    pick_wave_id: int,
    user: AdminUser = Depends(require_permission(PICK_WAVE_VIEW_PERMISSION)),
) -> dict:
    return build_wave_queue_reads().wave(
        pick_wave_id,user.username,lambda gateway:PickingService(gateway).get_wave_header(pick_wave_id))


'''
s=s.replace(anchor,new+anchor,1)
files[p]=s
print(json.dumps(files,ensure_ascii=True))
