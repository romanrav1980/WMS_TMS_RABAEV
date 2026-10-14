from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/delivery/infrastructure/order_delivery.py");s=p.read_text(encoding="utf-8")
old="""            select receipt.LOAD_OPERATION_ID,line.LOT_UID,receipt.OPERATION_ID RECEIPT_OPERATION,issue.STATUS CASE_STATUS,"""
new="""            with requested as(
              select VALUE ORIGINAL_LOAD from json_table(:loads,'$[*]' columns(VALUE varchar2(100) path '$'))
            ), delivery_loads as(
              select requested.ORIGINAL_LOAD,requested.ORIGINAL_LOAD FINAL_LOAD from requested
               where not exists(select 1 from RRL_INTERWARE_PLAN p where p.SOURCE_LOAD_OPERATION_ID=requested.ORIGINAL_LOAD)
              union all
              select requested.ORIGINAL_LOAD,d.OPERATION_ID FINAL_LOAD from requested
               join RRL_INTERWARE_ONWARD_DISPATCH d on d.SOURCE_LOAD_OPERATION_ID=requested.ORIGINAL_LOAD
               join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=d.OPERATION_ID and f.STATUS='DEPARTED'
            )
            select lineage.ORIGINAL_LOAD LOAD_OPERATION_ID,receipt.LOAD_OPERATION_ID ACTUAL_FINAL_LOAD_OPERATION_ID,line.LOT_UID,receipt.OPERATION_ID RECEIPT_OPERATION,issue.STATUS CASE_STATUS,"""
assert old in s;s=s.replace(old,new,1)
s=s.replace("from RRL_STORE_RECEIPT_FACT receipt join RRL_STORE_RECEIPT_LINE line on line.OPERATION_ID=receipt.OPERATION_ID","from delivery_loads lineage join RRL_STORE_RECEIPT_FACT receipt on receipt.LOAD_OPERATION_ID=lineage.FINAL_LOAD join RRL_STORE_RECEIPT_LINE line on line.OPERATION_ID=receipt.OPERATION_ID",1)
s=s.replace("             where receipt.LOAD_OPERATION_ID in(select VALUE from json_table(:loads,'$[*]' columns(VALUE varchar2(100) path '$')))\n","",1)
# Public provenance shows original-to-final route without another shipped quantity.
s=s.replace("result.update(order_no=header[0],original_document_status=header[1])","result.update(order_no=header[0],original_document_status=header[1],receipt_lineage=[{\"original_load_operation_id\":row[\"load_operation_id\"],\"actual_final_load_operation_id\":row[\"actual_final_load_operation_id\"],\"receipt_operation_id\":row[\"receipt_operation\"],\"lot_uid\":row[\"lot_uid\"]}for row in receipt])",1)
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/interwarehouse.js");s=p.read_text(encoding="utf-8")
s=s.replace('document.querySelectorAll("main input").forEach(n=>n.value="");','document.querySelectorAll("main input").forEach(n=>{n.value="";if(n.type==="checkbox")n.checked=false;});')
s=s.replace('if(saved.shipment_identifier)el("iwOnwardResult")','if(intent.path==="/prepare-onward")el("iwLegacyAddress").checked=false;if(saved.shipment_identifier)el("iwOnwardResult")')
s=s.replace(' el("iwLoad").addEventListener',' el("iwOnwardReceipt").addEventListener("change",()=>{el("iwLegacyAddress").checked=false;});\n el("iwLoad").addEventListener',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
