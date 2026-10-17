"""Mass-free, informational native SHIPPING_GROSS read contract; not a capture or QC decision."""
from dataclasses import dataclass,field
from datetime import datetime
import hashlib
import json
import re
from typing import Any
from .domain.models import CompositionIdentity,HuMassError,identity,utc_instant


def unique_object(pairs:list[tuple[str,Any]])->dict[str,Any]:
    result:dict[str,Any]={}
    for key,value in pairs:
        if key in result:raise HuMassError('SHIPPING_GROSS_DUPLICATE_JSON_KEY')
        result[key]=value
    return result


@dataclass(frozen=True)
class ShippingGrossReadInput:
    handling_unit_identifier:str
    scan_container:str
    expected_root_version:int

    def __post_init__(self)->None:
        identity(self.handling_unit_identifier);identity(self.scan_container)
        if type(self.expected_root_version)is not int or self.expected_root_version<0:
            raise HuMassError('SHIPPING_GROSS_ROOT_VERSION_REQUIRED')

    def canonical_json(self)->str:
        return json.dumps(dict(handling_unit_identifier=self.handling_unit_identifier,
            scan_container=self.scan_container,expected_root_version=self.expected_root_version),
            ensure_ascii=True,sort_keys=True,separators=(',',':'))


@dataclass(frozen=True)
class ShippingGrossExpectations:
    """Native plan reference; parsing does not grant admission or authenticate it."""
    plan_id:str
    plan_version:int
    signature:str


def parse_expectations(value:Any)->ShippingGrossExpectations|None:
    if value is None:return None
    if not isinstance(value,dict)or set(value)!={'domain','version','plan_id','plan_version','signature'}:
        raise ValueError('expectation token shape')
    if value['domain']!='CONSOLIDATION_EXPECTATIONS'or type(value['version'])is not int or value['version']!=1:
        raise ValueError('expectation domain/version')
    identity(value['plan_id'])
    if len(value['plan_id'].encode('utf-8'))>100 or type(value['plan_version'])is not int or value['plan_version']<1:
        raise ValueError('expectation plan identity/version')
    if not isinstance(value['signature'],str)or not re.fullmatch('[A-F0-9]{64}',value['signature']):
        raise ValueError('expectation signature')
    return ShippingGrossExpectations(value['plan_id'],value['plan_version'],value['signature'])


@dataclass(frozen=True)
class FrozenShippingGrossRead:
    composition:CompositionIdentity
    projection_json:str
    frozen_at:datetime
    expires_at:datetime
    producer:str
    consolidation_expectations:ShippingGrossExpectations|None
    # Digest consistency is not authentication, native admission, a lease or a QC grant.
    quality_release_approved:bool=field(default=False,init=False)
    stock_posted:bool=field(default=False,init=False)
    capture_archived:bool=field(default=False,init=False)


def parse_shipping_gross_read(raw:str,request:ShippingGrossReadInput)->FrozenShippingGrossRead:
    try:
        if len(raw.encode('utf-8'))>262144:raise ValueError('envelope bound')
        data=json.loads(raw,object_pairs_hook=unique_object)
        expected={'signature_domain','signature_version','composition_signature','projection_json','producer',
                  'frozen_at','expires_at','quality_release_approved','stock_posted','capture_archived'}
        if set(data)!=expected or any(data[k]is not False for k in ('quality_release_approved','stock_posted','capture_archived')):
            raise ValueError('informational envelope')
        if data['producer']!='RRL_SHIPPING_GROSS_READ.freeze' or data['signature_domain']!='SHIPPING_GROSS'or type(data['signature_version'])is not int or data['signature_version']!=1:
            raise ValueError('producer/domain')
        wire=data['projection_json']
        if not isinstance(wire,str)or len(wire.encode('utf-8'))>131072:raise ValueError('projection bound')
        if hashlib.sha256(wire.encode('utf-8')).hexdigest().upper()!=data['composition_signature']:raise ValueError('native projection digest')
        p=json.loads(wire,object_pairs_hook=unique_object)
        expectations=parse_expectations(p['consolidation_expectations'])
        if p['signature_domain']!='SHIPPING_GROSS'or type(p['signature_version'])is not int or p['signature_version']!=1:
            raise ValueError('projection domain')
        if p['root_version']!=request.expected_root_version or type(p['root_version'])is not int:raise ValueError('root version')
        if type(p['warehouse_id'])is not int or p['warehouse_id']<1:raise ValueError('physical warehouse')
        identity(p['cell']);identity(p['root_uid'])
        if not 2<=len(p['nodes'])<=200 or len(p['links'])>200 or not 1<=len(p['shipments'])<=200 or len(p['compiler_references'])>1000:
            raise ValueError('native closure bounds')
        roots=[node for node in p['nodes']if node['uid']==p['root_uid']]
        if len(roots)!=1 or roots[0]['kind']!='CONTAINER'or roots[0]['version']!=p['root_version']:raise ValueError('physical root')
        if request.handling_unit_identifier not in (p['root_uid'],roots[0].get('sscc'))or request.scan_container not in (p['root_uid'],roots[0].get('sscc')):
            raise ValueError('scan binding')
        frozen,expiry=datetime.fromisoformat(data['frozen_at']),datetime.fromisoformat(data['expires_at'])
        seconds=(utc_instant(expiry)-utc_instant(frozen)).total_seconds()
        if not 0<seconds<=120:raise ValueError('freeze expiry')
        composition=CompositionIdentity(p['root_uid'],p['root_version'],'SHIPPING_GROSS',1,data['composition_signature'])
        return FrozenShippingGrossRead(composition,wire,frozen,expiry,data['producer'],expectations)
    except (ValueError,TypeError,KeyError,AttributeError)as error:
        raise HuMassError('SHIPPING_GROSS_NATIVE_READ_REJECTED')from error
