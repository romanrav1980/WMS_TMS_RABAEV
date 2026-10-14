exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
out={};d='db/migrations/2026-10-12_ni061_group_placement'
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_HU_CMD'and TYPE='PACKAGE BODY'order by LINE")
 body='create or replace '+'\n'.join(x[0].rstrip('\r\n')for x in q)+'\n/\n'
 out[d+'/000_before_hu_cmd.sql']=body
 needle="     v_mode:=case when x.get_number('case_task_id') is not null"
 a=body.index(needle);b=body.index('\n',a)
 addition="""
     if v.has('group_placement')then
      declare gp json_object_t:=v.get_object('group_placement');wire clob;n number;begin
       wire:=gp.get_array('lines').to_clob;
       select count(*)into n from json_table(wire,'$[*]'columns(U varchar2(200)path '$.uid',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))g
       where g.U=v_leaf_uid and RRL_STOCK_MATH.quantity(g.Q)=v_qty and g.B=v_base;
       if d.get_string('command_type')!='HU_TASK_COMPLETE'or gp.get_string('from_cell')!=v_from or gp.get_string('target_cell')!=v_target or gp.get_number('warehouse_id')!=v_ware or n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_PUTAWAY_LEAF_REQUIRED');end if;
       v_mode:='PUTAWAY';
      end;
     end if;
"""
 body=body[:b]+addition+body[b:];out[d+'/005a_hu_cmd.sql']=body
 for filename,needle,replacement in [('apply.sql','@@005_recompile.sql','@@005a_hu_cmd.sql\n@@005_recompile.sql'),('rollback.sql','@@000_before_hu_task.sql','@@000_before_hu_task.sql\n@@000_before_hu_cmd.sql')]:
  p=Path(d+'/'+filename);out[p.as_posix()]=p.read_text(encoding='utf-8').replace(needle,replacement,1)
 q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
 try:
  saved=json.loads(Path('tmp/context406.json').read_text(encoding='utf-8'))
  q.execute('update RRL_CELLS set IS_SYSTEM=0 where CELL=:cell and WARE_ID=:ware',cell=saved['group_put_cell'],ware=saved['group_plan']['target_warehouse_id']);c.commit()
 finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
print(json.dumps(out))
