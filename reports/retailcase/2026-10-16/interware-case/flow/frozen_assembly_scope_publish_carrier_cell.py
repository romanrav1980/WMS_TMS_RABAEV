from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).parent))
import assembly_scope_fixture as f
x=json.loads((f.BASE/'fixture.json').read_text());g=f.OracleGateway();cell='CPT_'+str(x['warehouse_id'])
assert not g.fetch_all('select CELL from RRL_CELLS where CELL=:c',{'c':cell})
out=f.BASE/'carrier-cell-publication.json'
report=dict(state='PREPARED',cell=cell,warehouse=x['warehouse_id'],quantity_effect=False,reason='Fresh warehouse onboarding omitted system CASE carrier cell and its published lock key; retain failed native POLICY_KEY_NOT_PUBLISHED evidence')
with out.open('x',encoding='utf-8')as stream:json.dump(report,stream,indent=2)
with f.stock_configuration_transaction(g,f.NOTE,'admin','warehouse_settings_edit')as c:
 c.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:cell,:w,0,0,0,0,1,0,0,0)",cell=cell,w=x['warehouse_id'])
 c.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
report['state']='PUBLISHED';out.write_text(json.dumps(report,indent=2),encoding='utf-8');print('Fresh warehouse CASE system cell published; no quantity effect')
