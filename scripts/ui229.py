raise SystemExit("Retired authoring generator: use final SQL/current manifest and fresh affected-owner checkpoint; never overwrite later runtime")
from pathlib import Path
import json
out={};d=Path("admin/wms_admin_frontend/src/features/delivery")
p=d/"contracts.ts";s=p.read_text(encoding="utf-8")
s='''export interface StoreUnitScan {system_code:string;profile_code:string;code:string}
export interface StoreMarkControl {
 supported:boolean;reason?:string;physical_unit_count?:number;expected_scan_count?:number;
 profiles?:Array<{system_code:string;profile_code:string;profile_version:string;scan_mode:string}>;
}
'''+s
s=s.replace("export interface StorePreview {","export interface StorePreview {\n marked_unit_control?: StoreMarkControl;")
s=s.replace("export interface ReceiptBody {","export interface ReceiptBody {\n scans?: StoreUnitScan[];");out[str(p)]=s
p=d/"StoreAdmissionPanel.tsx";s=p.read_text(encoding="utf-8")
s=s.replace('import { StoreBoxMassPanel','import { StoreMarkPanel } from "./StoreMarkPanel";\nimport { StoreBoxMassPanel',1)
s=s.replace("StoreDisposition,WeightEvidence","StoreDisposition,WeightEvidence,StoreUnitScan")
s=s.replace("evidence?:WeightEvidence)=>","evidence?:WeightEvidence,scans?:StoreUnitScan[])=>")
s=s.replace(' const weight=',' const [scans,setScans]=useState<StoreUnitScan[]>([]);\n const weight=',1)
s=s.replace("!preview.requires_marked_recipient_flow&&","(!preview.requires_marked_recipient_flow||(preview.marked_unit_control?.supported&&scans.length===preview.marked_unit_control.expected_scan_count))&&")
s=s.replace('}:undefined);','}:undefined,scans.length?scans:undefined);')
s=s.replace("  <StoreBoxMassPanel preview={preview}/>","  <StoreMarkPanel preview={preview} username={credentials.username} disabled={disabled} onScans={setScans}/>\n  <StoreBoxMassPanel preview={preview}/>")
s=s.replace('forceCounts={weight&&act}', 'allowDiscrepancy={!preview.requires_marked_recipient_flow} forceCounts={weight&&act}')
out[str(p)]=s
p=d/"StoreDispositionPanel.tsx";s=p.read_text(encoding="utf-8").replace("forceCounts=false}","forceCounts=false,allowDiscrepancy=true}").replace("forceCounts?:boolean;","forceCounts?:boolean;allowDiscrepancy?:boolean;")
s=s.replace('disabled={disabled||forceCounts}','disabled={disabled||forceCounts||!allowDiscrepancy}');out[str(p)]=s
p=d/"StoreReceiptPanel.tsx";s=p.read_text(encoding="utf-8").replace('confirm={(rows,note,evidence)=>flow.confirm(scan,cameras,rows,note,evidence)}','confirm={(rows,note,evidence,scans)=>flow.confirm(scan,cameras,rows,note,evidence,scans)}')
s=s.replace("Для этого места требуется сверка маркированных единиц и применимые внешние подтверждения.","Сверьте уникальные коды по обязательным профилям товара. Государственное подтверждение учитывается отдельно.")
out[str(p)]=s
p=d/"useStoreReceipt.ts";s=p.read_text(encoding="utf-8").replace("StoreDisposition, WeightEvidence","StoreDisposition, WeightEvidence, StoreUnitScan")
s=s.replace("evidence?: WeightEvidence)","evidence?: WeightEvidence, scans?: StoreUnitScan[])")
s=s.replace("...evidence}};","...evidence,...(scans?.length?{scans}:{})}};");out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
