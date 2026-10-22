"""Real receipt and legal-attribute checks on one fresh marked TRADECASE fixture."""
from datetime import datetime, timezone
import base64
import json
import os
from pathlib import Path
import secrets
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).parent))
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS

OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T03'


def xml_call(path,element,status):
    auth=base64.b64encode((os.environ['TRADECASE_ADMIN_USER']+':'+os.environ['TRADECASE_ADMIN_PASSWORD']).encode()).decode()
    req=Request('http://127.0.0.1:8088'+path,ET.tostring(element,encoding='utf-8'),
                {'Authorization':'Basic '+auth,'Content-Type':'application/xml'},method='POST')
    started=time.perf_counter()
    try:
        with urlopen(req,timeout=35)as r: code,value=r.status,json.loads(r.read())
    except HTTPError as e: code,value=e.code,json.loads(e.read())
    CALLS.append(dict(method='POST',path=path,status=code,elapsed_ms=round((time.perf_counter()-started)*1000,2),response=value))
    assert code==status,(code,value)
    return value


def fields(node,values):
    for key,value in values.items(): ET.SubElement(node,key).text=str(value)


def ean(prefix):
    return prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(prefix)))%10)%10)


def setup():
    tag=uuid4().hex[:8];ware=210000000+int(tag[:6],16);article='TC03'+tag.upper()
    receive,storage,pick='T3R'+tag,'T3S'+tag,'T3P'+tag
    gtin=ean('290'+str(int(tag,16)).zfill(10)[-10:]);sscc=ean('690000000'+str(int(tag,16)).zfill(8)[-8:])
    actor,role,password='TC03'+tag,'TC03'+tag,secrets.token_hex(24)
    doc=ET.Element('ARTMAS10');idoc=ET.SubElement(doc,'IDOC');control=ET.SubElement(idoc,'EDI_DC40')
    fields(control,dict(MESTYP='ARTMAS',IDOCTYP='ARTMAS10',DOCNUM=str(1000000000000000+int(tag,16)),SNDPRN='TC03.QA.SAP',CREDAT='20261019',CRETIM='100000'))
    for segment,values in [('E1BPE1MATHEAD',{}),('E1BPE1MARART',dict(BASE_UOM='EA',EAN_UPC=gtin)),('E1BPE1MAKTRT',dict(LANGU_ISO='EN',MATL_DESC='TRADECASE QA '+tag)),('E1BPE1MARMRT',dict(ALT_UNIT='EA',NUMERATOR=1,DENOMINATR=1,EAN_UPC=gtin)),('E1BPE1MARMRT',dict(ALT_UNIT='BOX',NUMERATOR=10,DENOMINATR=1,EAN_UPC=ean('291'+gtin[3:13])))]:
        fields(ET.SubElement(idoc,segment),dict(MATERIAL=article,**values))
    xml_call('/api/integrations/sap/artmas',doc,202)
    with oracle_connection() as c:
        q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
        q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
        try:
            q.execute('update RRL_ARTICULS set TYPE_W=0 where ACTICUL=:a',a=article);assert q.rowcount==1
            q.execute("insert into RRL_WARES(ID,NAME,PREFIX,DEFAULT_RECEIVE_CELL)values(:w,:n,'T3',:r)",w=ware,n='TRADECASE QA '+tag,r=receive)
            q.execute("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT)values(:w,'NONE',0)",w=ware)
            for cell,is_pick in ((receive,0),(storage,0),(pick,1)):
                q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:w,0,0,0,:p,0,0,0)',cell=cell,w=ware,p=is_pick)
                q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
            q.execute("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX,SOURCE_PICK_MODE)values(:w,:a,:p,0,0,'AFTER_PUTAWAY')",w=ware,a=article,p=pick)
            c.commit()
        except BaseException:c.rollback();raise
        finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
        q.execute("insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,ACTIVE,VERSION_NO)values('WAREHOUSE',:w,'TRADECASE QA stock',1,1)",w=str(ware))
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:p,'TRADECASE QA stock','TC03QA',:w,0,1)",id=actor,p=password,w=ware)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:r,'TRADECASE QA stock',1,1)",r=role)
        for permission in ('tradecase_view','tradecase_stock_bind'):
            q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:r,:p)',r=role,p=permission)
        q.execute("""insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)
            values(:r,:a,:r,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '12'hour,'admin','Isolated TRADECASE stock acceptance',1)""",r=role,a=actor,w=str(ware))
        q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG');marker=q.fetchone()[0];c.commit()
    expect(200,http('PUT',f'/api/finished-goods/skus/{article}/receiving-policy',dict(expected_version=0,marking_required=True,serialized_weight_boxes=False,profiles=[dict(system_code='CRPT',profile_code='TOBACCO',profile_version='TC03',scan_mode='UNIT')])))
    return dict(tag=tag,warehouse_id=ware,article=article,receive=receive,storage=storage,pick=pick,gtin=gtin,pallet=sscc,actor=actor,role=role,password=password,slow_marker=marker)


def run(f):
    quantity = int(f.get('receipt_quantity', 250))
    assert 100 < quantity <= 1000 and quantity % 10 == 0, quantity
    ware=f['warehouse_id'];path=f'/api/tradecase/warehouses/{ware}';stock=path+'/stock'
    expect(200,http('PUT',path+'/site',dict(operation_id='T3.site.'+f['tag'],expected_version=0,source_id='TC03.SAP',active_skm='TC03.SKM',planning_source='SAP',enabled=True,reason='Isolated native stock acceptance')))
    def send(identifier,payload):
        return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id=uuid4().hex,source_id='TC03.SAP',warehouse_id=ware,document_id=identifier,version=1,occurred_at=datetime.now(timezone.utc).isoformat(),payload=payload)))
    for owner in ('SNS','BLC'):send(owner,dict(entity_type='OWNER',title=owner))
    send('A',dict(entity_type='SKU',title='QA tobacco leaf units',wms_article_id=f['article'],units_per_box=10,permitted_mrc=['200']))
    for cell,zone in ((f['receive'],'RECEIVE'),(f['storage'],'STORAGE'),(f['pick'],'PICK')):
        body=dict(operation_id='T3.cell.'+cell,expected_version=0,zone_kind=zone,reason='Isolated acceptance cell rule')
        if zone=='PICK':body['owner_id']='SNS'
        expect(200,http('PUT',stock+'/cells/'+cell,body))
    supply=ET.Element('WarehouseSupplyOrder',version='1');fields(supply,dict(Sender='TC03.QA.SAP',MessageId='T3.SUPPLY.'+f['tag'],OrderNumber='T3.'+f['tag'],Revision=1,WarehouseId=ware,ReceiveCell=f['receive'],Supplier='TRADECASE QA sender'))
    line=ET.SubElement(ET.SubElement(supply,'Lines'),'Line');fields(line,dict(LineNumber='1',Material=f['article']));ET.SubElement(line,'Quantity',unit='EA').text=str(quantity)
    imported=xml_call('/api/integrations/sap/supply-orders',supply,202)
    units=[dict(unit_id=str(i),quantity='1',codes=[dict(system_code='CRPT',profile_code='TOBACCO',code=f['gtin']+f['tag'][:3]+str(i).zfill(4))])for i in range(1,quantity+1)]
    received=expect(201,http('POST',f"/api/receiving/supply-orders/{imported['order_id']}/pallets",dict(operation_id='T3.receive.'+f['tag'],line_number='1',pallet_identifier=f['pallet'],quantity=str(quantity),supplier_batch='TC03.'+f['tag'],expiry_date='2030-01-01',gross_weight=str(quantity),units=units)))
    f.update(sap_order_id=imported['order_id'],task_id=received['task_id'],codes=[u['codes'][0]for u in units])
    send('SUPPLY',dict(entity_type='SUPPLY',wms_article_id=f['article'],sap_order_id=imported['order_id'],sap_line_id='1',sku_id='A',owner_id='SNS',mrc='200',pallet_identifier=f['pallet'],supplier_batch='TC03.'+f['tag'],expiry_date='2030-01-01',composition_source='SAP',codes=f['codes']))
    body=dict(operation_id='T3.bind.'+f['tag'],supply_id='SUPPLY',expected_supply_version=1,scanned_pallet=f['pallet'])
    expect(403,http('POST',stock+'/bind',body,f['actor'],f['password']))
    grant=dict(operation_id='T3.grant0.'+f['tag'],expected_version=0,username=f['actor'],owner_id='SNS',can_view=True,can_operate=False,reason='Read only before capture acceptance')
    expect(200,http('PUT',stock+'/owner-grants',grant));expect(403,http('POST',stock+'/bind',body,f['actor'],f['password']))
    grant.update(operation_id='T3.grant1.'+f['tag'],expected_version=1,can_operate=True)
    expect(200,http('PUT',stock+'/owner-grants',grant))
    bound=expect(200,http('POST',stock+'/bind',body,f['actor'],f['password']));assert bound['bound_units']==quantity and bound['mark_state']=='PENDING'
    assert expect(200,http('POST',stock+'/bind',body,f['actor'],f['password']))['replayed']
    view=expect(200,http('GET',stock+'?limit=100',actor=f['actor'],password=f['password']));assert len(view['items'])==100 and view['has_more']
    assert all(item['owner_id']=='SNS'and item['mark_state']=='PENDING'for item in view['items'])
    with oracle_connection()as c:
        q=c.cursor();q.execute('select TO_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:t',t=f['task_id']);target=q.fetchone()[0]
    expect(200,http('POST',f"/api/receiving/putaway/{f['task_id']}/complete",dict(scanned_pallet=f['pallet'],scanned_from_cell=f['receive'],scanned_to_cell=target)))
    f['current_cell']=target
    # Metadata cannot relabel occupied stock as a different owner's picking range.
    wrong=dict(operation_id='T3.wrongowner.'+f['tag'],expected_version=1,zone_kind='PICK',owner_id='BLC',reason='Reject wrong owner on occupied cell')
    error=expect(409,http('PUT',stock+'/cells/'+target,wrong));assert 'TRADE_PICK_OWNER_RANGE'in error['detail']['code'],error
    grant.update(operation_id='T3.revoke.'+f['tag'],expected_version=2,can_view=False,can_operate=False)
    expect(200,http('PUT',stock+'/owner-grants',grant));assert not expect(200,http('GET',stock,actor=f['actor'],password=f['password']))['items']
    expect(403,http('POST',stock+'/bind',body,f['actor'],f['password']))
    with oracle_connection()as c:
        q=c.cursor();q.execute("select RRL_STOCK_ELIGIBILITY.reason(:pallet_uid,:cell,:ware,1,null,null,'ALLOCATE')from dual",pallet_uid=f['pallet'],cell=target,ware=ware)
        reason=q.fetchone()[0];assert reason=='TRADE_CODE_VALIDATION_PENDING',reason
        q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:pallet_uid and CELL=:cell',pallet_uid=f['pallet'],cell=target);assert q.fetchone()==(quantity,0)
        q.execute("select count(*)from user_objects where status='INVALID'and object_name not like'BIN$%'");assert q.fetchone()[0]==0
        try:q.execute("update RRL_TRADE_STOCK_ATTR set MRC=201 where CAPTURE_WARE_ID=:w",w=ware)
        except Exception as e:assert 'TRADE_STOCK_WRITE_FORBIDDEN'in str(e)
        else:raise AssertionError('Direct attribute DML was not denied')
        c.rollback()
        q.execute('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 40 rows only',n=f['slow_marker'])
        slow=[list(x)for x in q]
    return dict(status='PASS',leaf_units=quantity,boxes_equivalent=quantity//10,physical_quantity=quantity,hard_reserved=0,mark_state='PENDING',admission_reason=reason,slow_sql=slow)


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True);fixture=None;report={}
    try:
        fixture=setup();report=run(fixture)
    except Exception as e:
        report=dict(status='FAIL',error=str(e));raise
    finally:
        if fixture:
            with oracle_connection()as c:
                q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:id and USER_GROUP='TC03QA'",id=fixture['actor'])
                q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:id',id=fixture['role']);c.commit()
            fixture.pop('password',None);report['fixture']=fixture
        report['http']=CALLS
        file=OUT/('stock-acceptance-'+uuid4().hex[:8]+'.json');file.write_text(json.dumps(report,indent=2,ensure_ascii=True,default=str),encoding='utf-8')
        (OUT/'latest.json').write_text(json.dumps(dict(file=str(file.relative_to(ROOT)),status=report['status'])),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],warehouse_id=fixture['warehouse_id'],http_calls=len(CALLS),file=str(file.relative_to(ROOT)))))
