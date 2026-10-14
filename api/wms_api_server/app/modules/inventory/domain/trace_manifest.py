"""Sender composition evidence; never a physical quantity writer."""
from decimal import Decimal
from hashlib import sha256
from typing import Any
import json
from .mark_identity import canonical_mark
from .unit_quantity import unit_quantity

def _text(value: Any,limit: int) -> str:
    if not isinstance(value,str) or not value or len(value.encode())>limit or "\x00" in value:
        raise ValueError("Missing or oversized manifest text")
    return value

def _number(value: Any) -> int:
    if isinstance(value,bool) or not isinstance(value,int) or value<1:
        raise ValueError("Positive manifest integer required")
    return value

def parse_manifest(raw: str) -> dict[str,Any]:
    if len(raw.encode())>4*1024*1024:
        raise ValueError("Manifest exceeds 4 MiB")
    document=json.loads(raw)
    required={"contract_version","source_kind","source_document_id","warehouse_id","pallet_identifier","article","base_uom","policy_version","profile_versions","units","aggregations","document_reference"}
    if not isinstance(document,dict) or set(document)!=required or document["contract_version"]!="WmsTraceManifest.v1" or document["source_kind"] not in {"INVENTORY","MES"}:
        raise ValueError("Exact WmsTraceManifest.v1 contract required")
    for field,limit in [("pallet_identifier",150),("article",160),("base_uom",20),("document_reference",255)]:
        _text(document[field],limit)
    if len(document["pallet_identifier"])>50:
        raise ValueError("Physical legacy pallet identifier exceeds 50 characters")
    for field in ["source_document_id","warehouse_id","policy_version"]:
        _number(document[field])
    if not isinstance(document["units"],list) or not 1<=len(document["units"])<=10000 or not isinstance(document["aggregations"],list) or not 1<=len(document["aggregations"])<=1000:
        raise ValueError("Manifest requires 1..10000 units and 1..1000 aggregates")
    return document

def validate_units(document: dict[str,Any],profiles: dict[tuple[str,str],dict[str,Any]],gtin: str|None) -> dict[str,dict[str,Any]]:
    supplied=document["profile_versions"]
    if not isinstance(supplied,list) or not 1<=len(supplied)<=50:
        raise ValueError("Manifest profile bound exceeded")
    versions={}
    for item in supplied:
        if not isinstance(item,dict) or set(item)!={"system_code","profile_code","version"}:
            raise ValueError("Exact manifest profile version required")
        key=(_text(item["system_code"],40),_text(item["profile_code"],80))
        if key in versions:
            raise ValueError("Duplicate manifest profile")
        versions[key]=_text(item["version"],40)
    if versions!={key:value["version"] for key,value in profiles.items()}:
        raise ValueError("Manifest does not match current WMS profile versions")
    units={};identities={}
    for item in document["units"]:
        if not isinstance(item,dict) or set(item)!={"unit_id","quantity","codes"}:
            raise ValueError("Exact manifest physical unit required")
        unit_id=_text(item["unit_id"],100)
        if unit_id in units:
            raise ValueError("Duplicate physical unit")
        quantity=unit_quantity(_text(item["quantity"],40),document["base_uom"],None)
        codes={}
        if not isinstance(item["codes"],list) or len(item["codes"])!=len(profiles):
            raise ValueError("Every unit requires every current profile exactly once")
        for scan in item["codes"]:
            if not isinstance(scan,dict) or set(scan)!={"system_code","profile_code","code"}:
                raise ValueError("Exact unique code fields required")
            key=(_text(scan["system_code"],40),_text(scan["profile_code"],80));code=_text(scan["code"],4000)
            if key not in profiles or key in codes:
                raise ValueError("Unknown or duplicate physical profile")
            mark=canonical_mark(*key,code,gtin if key[0]=="CRPT" else None)
            if key[0]=="CRPT" and mark["gtin"]!=gtin:
                raise ValueError("Manifest code GTIN does not match article")
            identity=(key[0],mark["identity"])
            if identity in identities and identities[identity]!=unit_id:
                raise ValueError("One unique code identifies multiple units")
            identities[identity]=unit_id;codes[key]=code
        units[unit_id]={"quantity":format(quantity,"f"),"codes":codes}
    return units

def resolve_aggregates(document: dict[str,Any],units: dict[str,dict[str,Any]],profiles: dict[tuple[str,str],dict[str,Any]]) -> list[dict[str,Any]]:
    nodes={};code_keys=set()
    for item in document["aggregations"]:
        required={"aggregation_id","system_code","profile_code","level","code","unit_ids","children"}
        if not isinstance(item,dict) or set(item)!=required:
            raise ValueError("Exact manifest aggregation fields required")
        node_id=_text(item["aggregation_id"],100);profile=(_text(item["system_code"],40),_text(item["profile_code"],80));code=_text(item["code"],4000)
        if node_id in nodes or profile not in profiles or item["level"] not in {"BOX","PALLET"} or not isinstance(item["unit_ids"],list) or not isinstance(item["children"],list):
            raise ValueError("Invalid aggregation identity/profile/level/membership")
        identity=(*profile,sha256(code.encode()).hexdigest())
        if identity in code_keys:
            raise ValueError("Duplicate aggregation code within profile")
        code_keys.add(identity);nodes[node_id]={**item,"profile":profile}
    result=[];total_expanded=0
    for root_id,root in nodes.items():
        pending=[(root_id,(),0)];members=set()
        while pending:
            current,path,depth=pending.pop()
            if current in path or depth>8 or current not in nodes:
                raise ValueError("Unknown/cyclic/too-deep aggregation")
            node=nodes[current]
            if node["profile"]!=root["profile"]:
                raise ValueError("Child aggregation belongs to another profile")
            for unit_id in node["unit_ids"]:
                if not isinstance(unit_id,str) or unit_id not in units or unit_id in members:
                    raise ValueError("Unknown or overlapping aggregation unit")
                members.add(unit_id)
            for child in node["children"]:
                if not isinstance(child,str):
                    raise ValueError("Invalid child aggregation reference")
                pending.append((child,path+(current,),depth+1))
        if not members:
            raise ValueError("Empty aggregation cannot stand for goods")
        total_expanded+=len(members)
        if total_expanded>100000:
            raise ValueError("Expanded manifest membership bound100000")
        result.append({"aggregation_id":root_id,"system_code":root["profile"][0],"profile_code":root["profile"][1],"level":root["level"],"code":root["code"],"code_hash":sha256(root["code"].encode()).hexdigest(),"units":[{"unit_id":uid,"quantity":units[uid]["quantity"],"code":units[uid]["codes"][root["profile"]]}for uid in sorted(members)]})
    return result
