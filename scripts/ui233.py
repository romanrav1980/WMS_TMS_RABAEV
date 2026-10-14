from pathlib import Path
import json
out={}
p=Path("admin/wms_admin_frontend/src/features/delivery/StoreMarkPanel.tsx");s=p.read_text(encoding="utf-8").replace("preview:StorePreview;","preview:Pick<StorePreview,'marked_unit_control'|'marked_partial_control'|'store_address'|'load_operation_id'|'composition_signature'|'requires_marked_recipient_flow'|'already_received'>;");out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/delivery/custodyApi.ts");s=p.read_text(encoding="utf-8").replace('import type { ReceiptCredentials }','import type { ReceiptCredentials, StoreUnitScan, StoreMarkControl }')
s=s.replace("export type ReturnStorePlace={","export type ReturnStorePlace={marked_unit_control?:StoreMarkControl|null;")
s=s.replace("export type ReturnDriverPlace={","export type ReturnDriverPlace={marked_unit_control?:StoreMarkControl|null;")
s=s.replace("export type CustodyBody={operation_id","export type CustodyBody={scans?:StoreUnitScan[];operation_id")
s=s.replace("|{operation_id:string;handover_operation_id","|{scans?:StoreUnitScan[];operation_id:string;handover_operation_id");out[str(p)]=s
p=Path("admin/wms_admin_frontend/src/features/delivery/ReturnCustodyPanel.tsx");s=p.read_text(encoding="utf-8").replace('import { useReturnCustody }','import { StoreMarkPanel } from "./StoreMarkPanel";\nimport type { StoreUnitScan } from "./contracts";\nimport { useReturnCustody }')
s=s.replace("function StoreHandover({row,confirm,disabled}:{row:ReturnStorePlace;confirm:(body:{","function StoreHandover({row,confirm,disabled,username}:{username:string;row:ReturnStorePlace;confirm:(body:{scans?:StoreUnitScan[];")
s=s.replace("function DriverPickup({row,confirm,disabled}:{row:ReturnDriverPlace;confirm:(body:{","function DriverPickup({row,confirm,disabled,username}:{username:string;row:ReturnDriverPlace;confirm:(body:{scans?:StoreUnitScan[];")
s=s.replace(' const [scan,setScan]=useState("");', ' const [scan,setScan]=useState("");') # preserve original grouped state
s=s.replace(' return <fieldset disabled={disabled}><p>', ' const [scans,setScans]=useState<StoreUnitScan[]>([]);\n const control=row.marked_unit_control;const markReady=!control||(control.supported&&scans.length===control.expected_scan_count);\n return <fieldset disabled={disabled}><p>')
s=s.replace('  <button disabled={!scan||!mass||!quantity}', '''  <StoreMarkPanel username={username} disabled={disabled} onScans={setScans} preview={{marked_unit_control:control||undefined,store_address:row.store_addr,load_operation_id:"RETURN.HANDOVER:"+row.transport_operation_id,composition_signature:JSON.stringify(control),requires_marked_recipient_flow:!!control,already_received:false}}/>
  <button disabled={!markReady||!scan||!mass||!quantity}''')
s=s.replace("physical_places:row.physical_places})","physical_places:row.physical_places,...(control?{scans}:{})})")
s=s.replace('  <button disabled={!vehicle||!scan}', '''  <StoreMarkPanel username={username} disabled={disabled} onScans={setScans} preview={{marked_unit_control:control||undefined,store_address:row.store_addr,load_operation_id:"RETURN.PICKUP:"+row.handover_operation_id,composition_signature:JSON.stringify(control),requires_marked_recipient_flow:!!control,already_received:false}}/>
  <button disabled={!markReady||!vehicle||!scan}''')
s=s.replace("scan_pallet:scan})","scan_pallet:scan,...(control?{scans}:{})})")
s=s.replace("row={row} disabled={flow.busy","row={row} username={username} disabled={flow.busy");out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
