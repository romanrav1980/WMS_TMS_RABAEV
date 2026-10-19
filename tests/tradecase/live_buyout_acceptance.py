"""Synthetic SKM business answers through real Oracle/API on owned storage stock."""
import sys,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-19/T05/storage-9ca5d9a2.json';WARE=220266073;TAG='9ca5d9a2'
s=json.loads(OUT.read_text())if OUT.exists()else dict(status='RUNNING',warehouse_id=WARE,tag=TAG,occurred_at=datetime.now(timezone.utc).isoformat(),buyout_id='TC5.BO.'+TAG,basis_id='TC5.BASIS.'+TAG)
history=s.get('http',[])
def save():s['http']=history+CALLS;OUT.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
def sql(query,**values):
    with oracle_connection()as c:q=c.cursor();q.execute(query,values);return q.fetchall()
def source(kind,identifier,payload,version=1):
    return expect(200,http('POST','/api/tradecase/messages',dict(schema_version=1,event_id='TC5.SOURCE.'+identifier+'.'+str(version),source_id='TC03.SAP',warehouse_id=WARE,document_id=identifier,version=version,occurred_at=s['occurred_at'],payload=dict(entity_type=kind,**payload))))
def config(label,expected,enabled=True,skm='TC03.SKM'):
    return http('PUT',f'/api/tradecase/warehouses/{WARE}/site',dict(operation_id='TC5.CONFIG.'+label+'.'+TAG,expected_version=expected,source_id='TC03.SAP',active_skm=skm,planning_source='SAP',enabled=enabled,reason='Isolated ownership transfer acceptance'))
def owners():return sql('select a.OWNER_ID,count(*)from RRL_TRADE_STOCK_ATTR a where a.CAPTURE_WARE_ID=:w group by a.OWNER_ID order by a.OWNER_ID',w=WARE)
try:
    assert sql('select NAME from RRL_WARES where ID=:w',w=WARE)[0][0]=='TRADECASE QA '+TAG
    if not s.get('unit_keys'):
        keys=sql("select PHYSICAL_UNIT_KEY from RRL_TRADE_STOCK_ATTR where CAPTURE_WARE_ID=:w and OWNER_ID='SNS'and MARK_STATE='VALID'order by PHYSICAL_UNIT_KEY",w=WARE)
        assert len(keys)==250;s['unit_keys']=[r[0]for r in keys];save()
    base=f'/api/tradecase/warehouses/{WARE}/buyouts'
    basis=dict(recipient_id='TC5.BUYER',order_kind='BUYOUT',buyout_mode='BEFORE_PICK',planned_ship_at='2026-10-19T12:00:00+03:00',lines=[dict(line_id='1',sku_id='A',source_owner_id='SNS',target_owner_id='BLC',mrc='200',quantity='250',uom='EA',min_osg_days=0)])
    if not s.get('bases'):
        source('RECIPIENT','TC5.BUYER',dict(title='TRADECASE financial QA',target_owner_id='BLC',permitted_source_owners=['SNS'],buyout_mode='BEFORE_PICK',lead_time_days=0,min_osg_days=0))
        source('ORDER',s['basis_id'],basis);source('ORDER',s['basis_id']+'.OTHER',basis);s['bases']=True;save()
    request=dict(operation_id='TC5.REQUEST.'+TAG,buyout_id=s['buyout_id'],basis_order_id=s['basis_id'],basis_line_id='1',expected_basis_version=1,unit_keys=s['unit_keys'])
    if not s.get('request_result'):
        s['request_result']=expect(200,http('POST',base,request));assert s['request_result']['owner_changes']==0;save()
    if not s.get('request_checks'):
        assert expect(200,http('POST',base,request))['replayed']
        alias=dict(request,operation_id='TC5.REQUEST.ALIAS.'+TAG);assert expect(200,http('POST',base,alias))['business_replayed']
        competitor=dict(request,operation_id='TC5.REQUEST.COMPETITOR.'+TAG,buyout_id=s['buyout_id']+'.OTHER',basis_order_id=s['basis_id']+'.OTHER')
        denied=expect(409,http('POST',base,competitor));assert 'ALREADY_HELD'in denied['detail']['code'],denied
        expect(409,config('SWITCH',1,skm='TC03.NEXT'))
        assert owners()==[('SNS',250)]
        s['request_checks']=True;save()
    if not s.get('paused'):
        expect(200,config('PAUSE',1,enabled=False));s['paused']=True;save()
    if not s.get('atomic_rollback'):
        failed=dict(operation_id='TC5.RESULT.BAD.'+TAG,buyout_id=s['buyout_id'],expected_version=1,skm_id='TC03.SKM',external_event_id='TC5.BAD.'+TAG,external_document_id='TC5.DOC.'+TAG,occurred_at=s['occurred_at'],items=[dict(physical_unit_key=s['unit_keys'][0],outcome='CONFIRMED'),dict(physical_unit_key='f'*64,outcome='CONFIRMED')])
        expect(409,http('POST',base+'/results',failed));assert owners()==[('SNS',250)]
        assert sql('select VERSION_NO,PENDING_UNITS from RRL_TRADE_BUYOUT where BUYOUT_ID=:b',b=s['buyout_id'])==[(1,250)]
        s['atomic_rollback']=True;save()
    partial=dict(operation_id='TC5.RESULT.PART.'+TAG,buyout_id=s['buyout_id'],expected_version=1,skm_id='TC03.SKM',external_event_id='TC5.PART.'+TAG,external_document_id='TC5.DOC.'+TAG,occurred_at=s['occurred_at'],items=[dict(physical_unit_key=k,outcome='CONFIRMED')for k in s['unit_keys'][:200]])
    if not s.get('partial_result'):
        r=expect(200,http('POST',base+'/results',partial));assert r['confirmed_units']==200 and r['pending_units']==50 and r['requires_sorting']is True,r
        s['partial_result']=r;save()
    if not s.get('partial_checks'):
        assert expect(200,http('POST',base+'/results',partial))['replayed']
        assert expect(200,http('POST',base+'/results',dict(partial,operation_id='TC5.RESULT.ALIAS.'+TAG)))['business_replayed']
        assert owners()==[('BLC',200),('SNS',50)]
        contradictory=dict(partial,operation_id='TC5.RESULT.REVERSE.'+TAG,expected_version=2,external_event_id='TC5.REVERSE.'+TAG,items=[dict(physical_unit_key=s['unit_keys'][0],outcome='REJECTED',reason='Must not reverse a completed transfer')])
        expect(409,http('POST',base+'/results',contradictory));assert owners()==[('BLC',200),('SNS',50)]
        detail=expect(200,http('GET',base+'/'+s['buyout_id']));assert detail['requires_sorting']is True
        s['partial_checks']=True;save()
    if not s.get('cancelled'):
        expect(200,config('RESUME',2));source('ORDER',s['basis_id'],dict(basis,cancelled=True),2);s['cancelled']=True;save()
    if not s.get('late_result'):
        final=dict(operation_id='TC5.RESULT.LATE.'+TAG,buyout_id=s['buyout_id'],expected_version=2,skm_id='TC03.SKM',external_event_id='TC5.LATE.'+TAG,external_document_id='TC5.DOC.'+TAG,occurred_at=s['occurred_at'],items=[dict(physical_unit_key=k,outcome='CONFIRMED')for k in s['unit_keys'][200:]])
        r=expect(200,http('POST',base+'/results',final));assert r['confirmed_units']==250 and r['pending_units']==0 and r['requires_sorting']is False,r
        s['late_result']=r;save()
    assert owners()==[('BLC',250)]
    assert sql("select STATUS from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='ORDER'and EXTERNAL_ID=:b",w=WARE,b=s['basis_id'])==[('CANCELLED',)]
    assert sql('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=WARE)==[(250,0)]
    assert sql("select count(*)from user_objects where status='INVALID'and object_name not like'BIN$%'")==[(0,)]
    s['regulatory_journal']=sql("select OPERATION_TYPE,count(*)from RRL_REG_OPERATION_JOURNAL where ENTITY_TYPE='TRADE_BUYOUT'and ENTITY_ID=:b group by OPERATION_TYPE order by OPERATION_TYPE",b=s['buyout_id']);assert s['regulatory_journal']==[('BUYOUT_REQUEST',1),('BUYOUT_RESULT',2)]
    if s.get('error'):s.setdefault('prior_failures',[]).append(dict(error=s.pop('error'),corrected_by='2026-10-19-tradecase-buyout-external-key'))
    s.update(status='PASS',physical_quantity=250,hard_reserved=0,provider='LOCAL_SYNTHETIC_ONLY',box_aggregation='NOT_PROVEN');save();print(json.dumps(dict(status=s['status'],buyout_id=s['buyout_id'],file=str(OUT),http_calls=len(CALLS))))
except Exception as e:s.update(status='FAIL',error=str(e));save();raise
