from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py");s=p.read_text(encoding="utf-8")
s=s.replace('"warehouse_placed_deliveries":placed,','"warehouse_placed_deliveries":sum(int(p["warehouse_placement_completed"])for p in incoming["plans"]),\n        "incoming_accounted_placed_deliveries":placed,')
out[p.as_posix()]=s
p=Path("admin/wms_admin_frontend/src/components/TransportCoordination.tsx");s=p.read_text(encoding="utf-8")
s=s.replace("warehouse_placed_deliveries:number;","warehouse_placed_deliveries:number;incoming_accounted_placed_deliveries?:number;")
s=s.replace('incoming:{expected_deliveries:number;ready_deliveries:number};','incoming:{expected_deliveries:number;ready_deliveries:number;plans?:{operation_id:string;receipt_complete:number;received_quantity:string;short_quantity:string;shortage_resolved:number;confirmed_short_quantity:string}[]};')
s=s.replace('{" "}размещено: {result.warehouse_placed_deliveries};','{" "}полностью принято и размещено: {result.warehouse_placed_deliveries};\n    {" "}принятая часть размещена и расхождение разрешено: {result.incoming_accounted_placed_deliveries??result.warehouse_placed_deliveries};')
s=s.replace('   <p>Погруженных мест в истории:', '''   {result.incoming.plans?.filter(p=>p.receipt_complete===0&&p.shortage_resolved===1).map(p=><p key={p.operation_id}>Поставка {p.operation_id}: принято {p.received_quantity}, подтверждена недостача {p.confirmed_short_quantity}. Полная физическая приёмка не подтверждена.</p>)}
   <p>Погруженных мест в истории:''',1)
out[p.as_posix()]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('row.receipt_complete', 'row.receipt_complete') # Keep original queue naming.
s=s.replace('say(intent.path==="/shortage-reports"?','say(intent.path==="/shortage-reports"?',1)
# Read incoming labels actual accepted/confirmed; response currently rendered by the existing incoming board.
needle='timingText('
# Queue already renders accepted/discrepancy. Keep old source quantity declaration and add confirmed text in shortage panel.
s=s.replace('"Ответственность не завершена")+" · "+(r.discrepancy_reason||"")','"Ответственность не завершена")+" · "+(r.loss_confirmed?"подтверждённая недостача":"открытая недостача")+" · "+(r.discrepancy_reason||"")',1)
out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
