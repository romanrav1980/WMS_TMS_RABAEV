from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/integrations/domain/supply_order.py');s=p.read_text(encoding='utf-8-sig')
start=s.index('    aggregations = []');end=s.index('    return {"sender":',start)
block=s[start:end].replace('    manifests = [n for n in root', '    manifests = [n for n in root')
# Separate sender aggregation decoding from document header/line parsing.
s=s[:start]+'    aggregations = read_supply_aggregations(root,numbers,value)\n'+s[end:]
head='\n\ndef read_supply_aggregations(root: ET.Element,numbers: set[str],value: Callable[[ET.Element,str,int],str]) -> list[dict[str,Any]]:\n'
s+='\n'+head+block+'    return aggregations\n'
s=s.replace('from decimal import Decimal, InvalidOperation','from decimal import Decimal, InvalidOperation\nfrom typing import Any,Callable')
out[str(p)]=s
for name in ['receipt_acknowledgements','supply_orders']:
 p=Path('api/wms_api_server/app/modules/integrations/infrastructure/'+name+'.py');s=p.read_text(encoding='utf-8-sig')
 if 'from typing import Any'not in s:s='from typing import Any\n'+s
 out[str(p)]=s.replace('def _text(value) -> str:', 'def _text(value: Any) -> str:')
p=Path('api/wms_api_server/app/modules/inventory/domain/carrier_shipment.py');s=p.read_text(encoding='utf-8-sig').replace('from fractions import Fraction','from fractions import Fraction\nfrom typing import Any,Sequence')
s=s.replace('def assert_matching_composition(physical_rows, document_rows):','def assert_matching_composition(physical_rows: Sequence[tuple[Any,...]],document_rows: Sequence[tuple[Any,...]]) -> None:')
out[str(p)]=s
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/case_pick_commands.py');s=p.read_text(encoding='utf-8-sig').replace('import json','import json\nfrom typing import Any,Sequence',1)
s=s.replace('def resolve_case_codes(gateway, task_id: int, line_id: int, scans)', 'def resolve_case_codes(gateway: Any, task_id: int, line_id: int, scans: Sequence[Any])')
s=s.replace('def post_case_pick(gateway, task_id: int, line_id: int, request):', 'def post_case_pick(gateway: Any, task_id: int, line_id: int, request: Any) -> dict[str,Any]|None:')
out[str(p)]=s
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/case_pick_policy.py');s=p.read_text(encoding='utf-8-sig')
s='from typing import Any\n'+s
out[str(p)]=s.replace('def case_pick_policy(gateway, task_id:', 'def case_pick_policy(gateway: Any, task_id:')
p=Path('api/wms_api_server/app/modules/inventory/infrastructure/alternative_pick_faces.py');s=p.read_text(encoding='utf-8-sig')
start=s.index('            cursor.execute("""insert into RRL_PICK_FACE_ASSIGNMENT');end=s.index('            return 1',start)
binding=s[start:end]
binding='\n'.join(line[8:]if line.startswith('        ')else line for line in binding.splitlines())
bind_file='''"""Apply one approved empty dynamic face to existing wave/CASE metadata."""
from typing import Any

def bind_alternative_face(cursor: Any,wave_id: int,row_id: int,article: str,old_cell: str,face: int,cell: str,
                          route_cell: int|None,route_sequence: int|None,sequence: int|None,unit_volume: Any,
                          base: str,actor: str,ids: str,source_reservation: int|None) -> None:
'''+binding+'\n'
out['api/wms_api_server/app/modules/inventory/infrastructure/alternative_face_binding.py']=bind_file
call='''            bind_alternative_face(cursor,wave_id,row_id,article,old_cell,face,cell,route_cell,
                route_sequence,sequence,unit_volume,base,actor,ids,source_reservation)
'''
s=s[:start]+call+s[end:]
# Candidate policy is a read query, distinct from reserving/binding the chosen face.
start=s.index('        cursor.execute("""select pf.PICK_FACE_ID');end=s.index('        for face, cell, max_volume',start)
candidate=s[start:end]
newmethod='\n    @staticmethod\n    def _candidates(cursor: Any,warehouse: int,route_id: int|None,old_cell: str) -> list[tuple[Any,...]]:\n'+candidate+'        return candidates\n'
s=s[:start]+'        candidates=self._candidates(cursor,warehouse,route_id,old_cell)\n'+s[end:]
s+=newmethod
s=s.replace('from typing import Any','from typing import Any\nfrom .alternative_face_binding import bind_alternative_face',1)
s=s.replace('def _route(self, cursor, wave_id, warehouse, route_id, row_id, article, old_cell, demand, source_reservation, actor, pick_task, pallet):','def _route(self,cursor: Any,wave_id: int,warehouse: int,route_id: int|None,row_id: int,article: str,old_cell: str,demand: Decimal,source_reservation: int|None,actor: str,pick_task: int|None,pallet: str|None) -> int:')
s=s.replace('def _release_empty(cursor, warehouse:', 'def _release_empty(cursor: Any, warehouse:')
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
