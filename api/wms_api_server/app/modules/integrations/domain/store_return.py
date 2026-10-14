"""Explicit assumed gateway contract; no claim of a SAP standard IDoc."""
import base64
from hashlib import sha256
import re
import xml.etree.ElementTree as ET

MAX_RETURN_XML_BYTES=16384


def read_store_return(raw: bytes) -> dict[str,object]:
    if not raw or len(raw)>MAX_RETURN_XML_BYTES:
        raise ValueError("Return XML must contain1..16384 bytes")
    xml=raw.decode("utf-8")
    if "<!DOCTYPE" in xml.upper() or "<!ENTITY" in xml.upper():
        raise ValueError("DTD and entities are forbidden")
    root=ET.fromstring(xml)
    version=root.attrib.get("version")
    if root.tag!="WarehouseStoreReturn" or version not in {"1","2"} or root.attrib!={"version":version}:
        raise ValueError("Expected WarehouseStoreReturn version1 or2 without namespaces")
    fields={"Sender":100,"MessageId":100,"ReturnDocumentNumber":100,"ApprovalOperationId":100,
            "OriginalReceiptOperationId":100,"OriginalLineNumber":10,"WarehouseId":18,"ReceiveCell":255,
            "Article":160,"LotId":200,"Quantity":40,"Disposition":20}
    if version=="2":fields["OriginalReceiptDisposition"]=10
    if len(root)!=len(fields) or any(node.tag not in fields for node in root):
        raise ValueError("Exactly the mapped return fields are required")
    values: dict[str,str]={}
    for node in root:
        if node.tag in values or len(node):
            raise ValueError("Duplicate or nested scalar return field")
        if node.tag!="Quantity" and node.attrib:
            raise ValueError("Unexpected return field attributes")
        text=node.text or ""
        if not text or text!=text.strip() or len(text.encode("utf-8"))>fields[node.tag]:
            raise ValueError("Missing, padded or oversized return field "+node.tag)
        values[node.tag]=text
    quantity=next(node for node in root if node.tag=="Quantity")
    if set(quantity.attrib)!={"unit"} or not quantity.attrib["unit"] or len(quantity.attrib["unit"].encode())>20:
        raise ValueError("Quantity requires one BASE unit")
    if not re.fullmatch(r"[0-9]{1,18}(\.[0-9]{1,9})?",values["Quantity"]):
        raise ValueError("Return quantity requires exact positive decimal")
    if not values["OriginalLineNumber"].isdigit() or not 1<=int(values["OriginalLineNumber"])<=200:
        raise ValueError("Original line must be1..200")
    if not values["WarehouseId"].isdigit() or int(values["WarehouseId"])<1:
        raise ValueError("Warehouse recipient must be positive")
    if values["Disposition"] not in {"REUSE","SUPPLIER","DISPOSAL"}:
        raise ValueError("Unknown return disposition")
    basis=values.get("OriginalReceiptDisposition","ACCEPTED")
    if basis not in {"ACCEPTED","REFUSED","DAMAGED"}:
        raise ValueError("Original receipt disposition must be ACCEPTED/REFUSED/DAMAGED")
    sender,message=values["Sender"],values["MessageId"]
    return {"operation_id":"SAP.RETURN:"+sha256((sender+"\x00"+message).encode()).hexdigest(),
            "approval_operation_id":values["ApprovalOperationId"],
            "metadata":{**({"return_basis":basis}if version=="2"else {}),"sender":sender,"message_id":message,"return_document":values["ReturnDocumentNumber"],
                "receipt_operation_id":values["OriginalReceiptOperationId"],"line_no":int(values["OriginalLineNumber"]),
                "warehouse_id":int(values["WarehouseId"]),"receive_cell":values["ReceiveCell"],
                "article":values["Article"],"lot_uid":values["LotId"],"quantity":values["Quantity"],
                "base_uom":quantity.attrib["unit"],"disposition":values["Disposition"],
                "raw_base64":base64.b64encode(raw).decode("ascii"),"payload_hash":sha256(raw).hexdigest()}}
