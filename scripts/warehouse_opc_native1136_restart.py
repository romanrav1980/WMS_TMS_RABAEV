"""Restart only the existing TEST1136 OPC server with its original keys/profile.

No HTTP/Oracle calls, certificate generation, profile rewriting or measurement
archive. Explicit root release is required before starting the fixture.
"""
import argparse
import asyncio
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


async def serve(seconds):
    from asyncua import Server,ua
    from asyncua.common.structures104 import new_struct,new_struct_field
    from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_profile import OpcScaleProfile
    root=ROOT/'runtime/warehouse-opc-native1136'
    path=root/'commissioned-test-profile.json';original=path.read_bytes();profile=OpcScaleProfile.load(path)
    assert profile.data['device_id']=='WHREQ15.SCALE'
    assert original==(root/'frozen-first-commissioned-profile.json').read_bytes()
    security=profile.data['security'];certificate=root/security['server_certificate']
    assert hashlib.sha256(certificate.read_bytes()).hexdigest().upper()==security['server_sha256'].upper()
    server=Server();await server.init();server.set_endpoint(profile.data['endpoint'])
    await server.set_application_uri(profile.data['server_application_uri'])
    await server.load_certificate(certificate);await server.load_private_key(root/'server.pem')
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt])
    index=await server.register_namespace(profile.data['model_namespace_uri'])
    dtype,_=await new_struct(server,index,'WeightType',[new_struct_field(f,ua.VariantType.Double)for f in('Gross','Net','Tare')])
    await server.load_data_type_definitions();parent=await server.nodes.objects.add_object(index,'TestScale')
    def control():
        value=json.loads((root/'approved-test-gross.json').read_text(encoding='utf-8-sig'))
        if value.get('owner_approved')is not True or value.get('gross_kg')not in['0','0.5','1.5']:raise ValueError('TEST_CONTROL_INVALID')
        return float(value['gross_kg'])
    for field,mapping in profile.data['nodes'].items():
        assert mapping['identifier_type']=='i'and mapping['namespace_uri']==profile.data['model_namespace_uri']
        node_id=ua.NodeId(mapping['identifier'],index)
        if field=='current_weight':node=await parent.add_variable(node_id,field,ua.WeightType(Gross=1.5,Net=1.5,Tare=0.),datatype=dtype.nodeid)
        elif field=='engineering_units':node=await parent.add_variable(node_id,field,ua.EUInformation(NamespaceUri=profile.data['unit_namespace_uri'],UnitId=profile.data['kg_unit_id']))
        elif field=='tare_mode':node=await parent.add_variable(node_id,field,profile.data['no_tare_mode'])
        else:node=await parent.add_variable(node_id,field,False)
        def read(nodeid,attr,field=field):
            gross=control();now=datetime.now(timezone.utc)
            if field=='current_weight':value=ua.WeightType(Gross=gross,Net=gross,Tare=0.)
            elif field=='engineering_units':value=ua.EUInformation(NamespaceUri=profile.data['unit_namespace_uri'],UnitId=profile.data['kg_unit_id'])
            elif field=='tare_mode':value=profile.data['no_tare_mode']
            else:value={'stable':True,'center_zero':gross==0.,'overload':False,'underload':False}[field]
            data=ua.DataValue(ua.Variant(value));data.StatusCode=ua.StatusCode(0);data.SourceTimestamp=now;data.ServerTimestamp=now;return data
        server.set_attribute_value_callback(node.nodeid,read)
    await server.start()
    try:
        assert path.read_bytes()==original
        print(json.dumps(dict(state='PINNED_TEST_SERVER_RESTARTED',seconds=seconds,profile_unchanged=True,physical_hardware=False)),flush=True)
        await asyncio.sleep(seconds)
    finally:await server.stop();assert path.read_bytes()==original


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute-restart',action='store_true');parser.add_argument('--seconds',type=int,default=1800);args=parser.parse_args()
    if not args.execute_restart:print('PREPARED_ONLY: root release required');return
    if not 0<args.seconds<=3600:raise ValueError('Bounded TEST server lifetime required')
    asyncio.run(serve(args.seconds))


if __name__=='__main__':main()
