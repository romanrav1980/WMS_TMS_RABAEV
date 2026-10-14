from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("class StoreUnitScan(BaseModel):","class StoreUnitScan(BaseModel):\n    disposition: Literal[\"ACCEPTED\",\"REFUSED\",\"DAMAGED\"]=\"ACCEPTED\"");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/domain/mark_identity.py");s=p.read_text(encoding="utf-8");start=s.index('\ndef normalize_unit_scan_codes(')
s=s[:start]+'''\ndef normalize_unit_scan_codes(scans: list[dict[str, str]]) -> list[dict[str, str]]:
    """One canonical identity/hash contract; optional physical recipient disposition."""
    from hashlib import sha256
    result=[]
    for scan in scans:
        action=scan.get("disposition","ACCEPTED")
        if action not in ("ACCEPTED","REFUSED","DAMAGED"):
            raise ValueError("Only a present physical unit can be scanned as accepted, refused or damaged")
        item={"system_code":scan["system_code"],"profile_code":scan["profile_code"],
              "code_hash":sha256(canonical_mark(scan["system_code"],scan["profile_code"],scan["code"])["identity"].encode("utf-8")).hexdigest()}
        if action!="ACCEPTED":
            item["disposition"]=action
        result.append(item)
    return result
''';out[str(p)]=s
d=Path("admin/wms_admin_frontend/src/features/delivery")
p=d/"contracts.ts";s=p.read_text(encoding="utf-8").replace("StoreUnitScan {system_code:string;profile_code:string;code:string}","StoreUnitScan {system_code:string;profile_code:string;code:string;disposition?:\"ACCEPTED\"|\"REFUSED\"|\"DAMAGED\"}")
s=s.replace(" marked_unit_control?: StoreMarkControl;"," marked_unit_control?: StoreMarkControl;\n marked_partial_control?: boolean;");out[str(p)]=s
p=d/"StoreMarkPanel.tsx";s=p.read_text(encoding="utf-8").replace(' const draftKey=',' const [disposition,setDisposition]=useState<"ACCEPTED"|"REFUSED"|"DAMAGED">("ACCEPTED");\n const draftKey=',1)
s=s.replace('p.profile_code===x.profile_code)))','p.profile_code===x.profile_code)&&(!x.disposition||["ACCEPTED","REFUSED","DAMAGED"].includes(x.disposition))))')
s=s.replace('profile_code:selected.profile_code,code}','profile_code:selected.profile_code,code,...(disposition!=="ACCEPTED"?{disposition}:{})}')
s=s.replace('  <label>QR единицы','  {preview.marked_partial_control&&<label>Решение для сканируемой единицы<select value={disposition} onChange={e=>setDisposition(e.target.value as typeof disposition)}><option value="ACCEPTED">Принято</option><option value="REFUSED">Отказ</option><option value="DAMAGED">Повреждено</option></select></label>}\n  <label>QR единицы',1)
s=s.replace('  <p role="status">','  {preview.marked_partial_control&&<p>Для одной штуки сканируйте все обязательные профили с одинаковым решением. Полностью отсутствующие штуки будут учтены как недостача; укажите соответствующие количества и причину расхождения.</p>}\n  <p role="status">',1)
out[str(p)]=s
p=d/"StoreAdmissionPanel.tsx";s=p.read_text(encoding="utf-8").replace('scans.length===preview.marked_unit_control.expected_scan_count','(preview.marked_partial_control?scans.length<=(preview.marked_unit_control.expected_scan_count||0):scans.length===preview.marked_unit_control.expected_scan_count)')
s=s.replace('allowDiscrepancy={!preview.requires_marked_recipient_flow}','allowDiscrepancy={!preview.requires_marked_recipient_flow||!!preview.marked_partial_control}');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
