"""Bounded ARTMAS10 envelope reader; does not invent customer extension mappings."""
from hashlib import sha256
import xml.etree.ElementTree as ET

MAX_IDOC_BYTES = 4 * 1024 * 1024


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def fields(node: ET.Element) -> dict[str, str]:
    result: dict[str, str] = {}
    for child in node:
        if len(child):
            continue
        name = local_name(child.tag)
        if name in result:
            raise ValueError(f"Duplicate IDoc field: {name}")
        result[name] = (child.text or "").strip()
    return result


def read_artmas10(raw: bytes) -> dict:
    if not raw or len(raw) > MAX_IDOC_BYTES:
        raise ValueError("IDoc must contain 1 byte to 4 MiB.")
    xml = raw.decode("utf-8-sig")
    upper = xml.upper()
    if "<!DOCTYPE" in upper or "<!ENTITY" in upper:
        raise ValueError("DTD and entity declarations are forbidden.")
    root = ET.fromstring(xml)
    idocs = [node for node in root.iter() if local_name(node.tag) == "IDOC"]
    if len(idocs) != 1:
        raise ValueError("Send exactly one IDOC per request.")
    idoc = idocs[0]
    controls = [n for n in idoc if local_name(n.tag) == "EDI_DC40"]
    if len(controls) != 1:
        raise ValueError("Exactly one EDI_DC40 control record is required.")
    control = fields(controls[0])
    if control.get("MESTYP") != "ARTMAS" or control.get("IDOCTYP") != "ARTMAS10":
        raise ValueError("Expected MESTYP=ARTMAS and IDOCTYP=ARTMAS10.")
    for name, length in [("DOCNUM", 16), ("SNDPRN", 100)]:
        if not control.get(name) or len(control[name]) > length:
            raise ValueError(f"Missing or oversized EDI_DC40.{name}")
    if len(control.get("CIMTYP", "")) > 80:
        raise ValueError("EDI_DC40.CIMTYP exceeds 80 characters.")
    if not control["DOCNUM"].isdigit():
        raise ValueError("SAP DOCNUM must be numeric")
    records: list[dict] = []
    materials: set[str] = set()
    for node in idoc.iter():
        tag = local_name(node.tag)
        if not tag.startswith("E1") and not tag.startswith("Z"):
            continue
        data = fields(node)
        material = data.get("MATERIAL")
        if material:
            materials.add(material)
        records.append({"segment": tag, "fields": data, "attributes": dict(node.attrib)})
        if len(records) > 10000:
            raise ValueError("IDoc exceeds 10000 segments.")
    if not any(r["segment"] == "E1BPE1MATHEAD" for r in records):
        raise ValueError("ARTMAS requires E1BPE1MATHEAD.")
    if not materials:
        raise ValueError("ARTMAS contains no MATERIAL identifiers.")
    # FUNCTION, X segments, languages, UoMs and customer fields are retained;
    # receiving the envelope is not applying an article or confirming a delivery.
    return {"sender": control["SNDPRN"], "docnum": control["DOCNUM"],
            "message_type": "ARTMAS", "basic_type": "ARTMAS10",
            "extension": control.get("CIMTYP") or None, "control": control,
            "materials": sorted(materials), "segments": records,
            "payload_hash": sha256(raw).hexdigest(), "raw_xml": raw.decode("utf-8")}
