"""Real HTTP/Oracle demand+capacity calculation; metadata-only, no shipment claim."""
from datetime import datetime,timedelta,timezone
import json
import os
from pathlib import Path
import sys
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import make_fixture,http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-21/T09';OUT.mkdir(parents=True,exist_ok=True)


def run(f):
    w=f['warehouse_id'];tag='ALLOC21.'+str(w);base=f'/api/tradecase/warehouses/{w}'
    now=datetime.now(timezone.utc);depart=now+timedelta(hours=12);report=dict(status='FAIL',warehouse_id=w,checks=[])
    def send(kind,key,payload,version=1):
        return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id=tag+'.'+kind+'.'+key+'.'+str(version),source_id='SAP_QA',warehouse_id=w,
            document_id=key,version=version,occurred_at=now.isoformat(),payload=dict(entity_type=kind,**payload))))
    expect(200,http('PUT',base+'/site',dict(operation_id=tag+'.site',expected_version=0,source_id='SAP_QA',active_skm='SKM_QA',planning_source='SAP',enabled=True,reason='Isolated read-only need allocation')))
    for owner in ['SNS','BLC']:send('OWNER',owner,dict(title=owner))
    with oracle_connection()as conn:
        q=conn.cursor();q.execute("select EXTERNAL_ID,BODY_JSON from RRL_TRADE_DOCUMENT where WARE_ID=224274301 and ENTITY_TYPE='SKU'and EXTERNAL_ID in('A','B')")
        skus={k:v if isinstance(v,dict)else json.loads(v.read()if hasattr(v,'read')else v)for k,v in q};assert len(skus)==2
    for k,sku in skus.items():send('SKU',k,{x:v for x,v in sku.items()if x!='entity_type'})
    for i in range(1,4):send('RECIPIENT','C'+str(i),dict(title=['Hub','Branch','Store'][i-1],target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode='IN_TRANSIT',min_osg_days=0,lead_time_days=0))
    for oid,c,sku,mrc,n in [('O101','C1','A','200','200'),('O102','C2','A','200','150'),('O103','C3','B','220','250')]:
        send('ORDER',oid,dict(recipient_id=c,planned_ship_at=depart.isoformat(),lines=[dict(line_id='1',sku_id=sku,source_owner_id='SNS',target_owner_id='BLC',mrc=mrc,quantity=n,uom='BOX',min_osg_days=0)]))
    plate=tag.replace('.','');vehicle=expect(201,http('POST','/api/admin/transport/vehicles',dict(num_plat=plate,transtype_id='10',max_weight_kg=8000,max_pallets=33,sobstvennyy=True)))['id']
    source=expect(200,http('GET',f'/api/admin/transport/vehicles/{vehicle}/profile'))
    expect(200,http('POST','/api/admin/transport/vehicle-profiles',dict(operation_id=tag+'.body',vehicle_id=vehicle,expected_source_hash=source['base_hash'],expected_version=source['version'],vehicle_size_class='QA_ALLOCATION',
        cargo_length_mm=13200,cargo_width_mm=2500,cargo_height_mm=2000,outer_height_mm=3000,outer_length_mm=14000,
        floor_variants=[dict(code='QA33EURO',limits=[dict(pallet_type_id=1,max_places=33)])],reason='Synthetic allocation fixture, not a physical measurement',evidence_reference='TEST_SOURCE_ONLY')))
    send('TRIP','R1',dict(vehicle_id=plate,planning_source='SAP',planned_departure_at=depart.isoformat(),capacity_kg='8000',capacity_m3='66',orders=[dict(order_id=o,line_id='1',quantity=n)for o,n in [('O101','200'),('O102','150'),('O103','250')]]))
    def need(c,sku,forecast,target,available,primary,**changes):
        value=dict(recipient_id=c,sku_id=sku,recipient_version=1,sku_version=1,snapshot_at=now.isoformat(),period_from=now.isoformat(),period_until=(now+timedelta(days=3)).isoformat(),uom='BOX',forecast_quantity=forecast,target_quantity=target,available_quantity=available,received_in_available=True,
            supplies=[dict(supply_id='MAIN.'+c,version=1,quantity=primary,uom='BOX',status='PLANNED',confirmed=True,current_trip=True,expected_at=depart.isoformat()),dict(supply_id='TRANSIT.'+c,version=1,quantity='20',uom='BOX',status='IN_TRANSIT',confirmed=True,current_trip=False,expected_at=depart.isoformat())]);value.update(changes);return value
    a=need('C2','A','240','50','80','150');b=need('C3','B','320','40','60','250')
    send('NEED','N.A',a);send('NEED','N.B',b)
    path=base+'/trips/R1/topup-preview';body=dict(need_ids=['N.A','N.B'],max_age_minutes=60)
    value=expect(200,http('POST',path,body));assert [x['proposed_boxes']for x in value['items']]==[40,20]
    assert [x['uncovered_boxes']for x in value['items']]==['0','10']and value['topup_order_created']is False
    report.update(first=value,trip_id='R1',need_ids=body['need_ids']);report['checks'].append('40A+20B; primary600 preserved; ten B remain')
    duplicate=expect(200,http('POST',path,body));assert duplicate['calculation_signature']==value['calculation_signature']
    reverse=expect(200,http('POST',path,dict(body,need_ids=['N.B','N.A'])));assert [x['proposed_boxes']for x in reverse['items']]==[30,30]
    assert reverse['calculation_signature']!=value['calculation_signature'];report['checks'].append('same input same signature; changed priority30B+30A')
    expect(422,http('POST',path,dict(body,need_ids=['N.A','N.A'])))
    send('NEED','N.BAD',dict(a,supplies=[]));expect(409,http('POST',path,dict(body,need_ids=['N.BAD'])))
    send('NEED','N.OLD',dict(a,snapshot_at=(now-timedelta(minutes=61)).isoformat()));expect(409,http('POST',path,dict(body,need_ids=['N.OLD'])))
    send('NEED','N.A2',a);expect(409,http('POST',path,dict(body,need_ids=['N.A','N.A2'])))
    expect(404,http('POST',path,dict(body,need_ids=['MISSING'])));report['checks'].append('duplicate pair/ID, stale, primary mismatch and missing source blocked')
    expect(403,http('POST',path,body,f['actor'],f['password']))
    grant=dict(operation_id=tag+'.grant',expected_version=0,username=f['actor'],owner_id='SNS',can_view=True,can_operate=False,reason='Read-only allocation owner scope')
    expect(200,http('PUT',base+'/stock/owner-grants',grant));scoped=expect(200,http('POST',path,body,f['actor'],f['password']));assert scoped['calculation_signature']==value['calculation_signature']
    expect(200,http('PUT',base+'/stock/owner-grants',dict(grant,operation_id=tag+'.revoke',expected_version=1,can_view=False)))
    expect(403,http('POST',path,body,f['actor'],f['password']));report['checks'].append('owner grant/revoke changes access, not result')
    old=expect(200,http('GET',base+'/trips/R1/capacity?sku_id=A&requested_boxes=80'));assert old['fitting_boxes']==60
    one=expect(200,http('GET',base+'/needs/N.A?max_age_minutes=60'));assert one['additional_boxes']=='40';report['checks'].append('existing capacity and need readers retain behavior')
    report['status']='PASS';return report


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin'
    with oracle_connection()as conn:
        q=conn.cursor();q.execute("select PASS from RUSERS where ID='admin'");os.environ['TRADECASE_ADMIN_PASSWORD']=q.fetchone()[0]
    f=None;report=dict(status='FAIL')
    try:f=make_fixture();report.update(run(f))
    except Exception as exc:report['error']=str(exc);raise
    finally:
        if f:
            with oracle_connection()as conn:
                q=conn.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC19QA'",a=f['actor'])
                q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=f['role']);conn.commit()
                q.execute('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID',n=f['slow_marker']);report['slow_sql']=[list(r)for r in q]
                q.execute('select count(*)from RRL_PALLETS');assert q.fetchone()[0]==f['physical_before']
                report['fixture']={k:v for k,v in f.items()if k!='password'}
        report['http']=CALLS;(OUT/('allocation-'+str(f['warehouse_id']if f else uuid4().hex)+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],warehouse_id=f['warehouse_id'],checks=report['checks'])))
