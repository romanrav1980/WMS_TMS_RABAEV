from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).parent))
import assembly_scope_fixture as f
x=json.loads((f.BASE/'fixture.json').read_text());g=f.OracleGateway()
out=f.BASE/'box-conversion-repair.json';assert not out.exists()
before=g.fetch_all("select INPUT_UOM,BASE_UOM,NUMERATOR,DENOMINATOR,POLICY_VERSION from RRL_STOCK_UOM_CONVERSION where ARTICUL=:a order by INPUT_UOM",{'a':x['article']})
source=g.fetch_all("select INPUT_UOM,BASE_UOM,NUMERATOR,DENOMINATOR,POLICY_VERSION from RRL_STOCK_UOM_CONVERSION where ARTICUL='REUSE.QA:cdbf4c0962' order by INPUT_UOM")
assert any(r['input_uom']=='BOX'and r['base_uom']=='EA'for r in source)
report=dict(before=before,source_policy=source,reason='Fresh fixture omitted BOX capacity conversion; clone only missing original exact conversions, no quantities',state='PREPARED')
with out.open('x',encoding='utf-8')as stream:json.dump(report,stream,indent=2)
with f.stock_configuration_transaction(g,f.NOTE,'admin','warehouse_settings_edit')as c:
 c.execute("""insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)
 select :a,s.INPUT_UOM,s.BASE_UOM,s.POLICY_VERSION,s.NUMERATOR,s.DENOMINATOR,s.BASE_SCALE,:note
 from RRL_STOCK_UOM_CONVERSION s where s.ARTICUL='REUSE.QA:cdbf4c0962'
 and not exists(select 1 from RRL_STOCK_UOM_CONVERSION t where t.ARTICUL=:a and t.INPUT_UOM=s.INPUT_UOM and t.BASE_UOM=s.BASE_UOM)""",a=x['article'],note=f.NOTE)
report['state']='METADATA_REPAIRED';out.write_text(json.dumps(report,indent=2),encoding='utf-8')
svc=f.PickingService(g);x['launch']=svc.launch_wave(x['wave'],f.PickWaveActionRequest(updated_by='admin',operation_id=x['prefix']+'.LAUNCH'));f.save(x)
tasks=g.fetch_all('select CASE_PICK_TASK_ID,CONTENT_VERSION,SSCC from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w',{'w':x['wave']});assert len(tasks)==1
x.update(task_id=tasks[0]['case_pick_task_id'],case_before=tasks[0]);f.save(x)
lines=g.fetch_all('select CASE_PICK_LINE_ID,PLANNED_QTY,CELL_CODE from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:t',{'t':x['task_id']});assert len(lines)==1 and lines[0]['planned_qty']==1 and lines[0]['cell_code']==x['cell']
x['case_line_id']=lines[0]['case_pick_line_id'];f.save(x)
f.post(x,'WAVE_PICK_RELEASE',{'wave_id':x['wave']},{},'RELEASE')
x['state']='FRESH_CASE_READY';f.save(x)
print(json.dumps({k:x[k]for k in('state','warehouse_id','task_id','case_line_id','actor')}))
