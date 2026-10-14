from pathlib import Path
import json
d='db/migrations/2026-10-12_ni061_group_receive'
p=Path('tmp/native413_unit.sql');t=p.read_text(encoding='utf-8')
needle="  if n!=1 then raise_application_error(-20863,'INTERWARE_UNIT_RECEIPT_PLAN_REQUIRED');end if;"
add="""  if n=0 then
   select count(*)into n from RRL_STOCK_OPERATION o join json_table(o.RESOLVED_PLAN_JSON,'$.domain'columns(
    GROUP_FLAG varchar2(5)path '$.group_receipt',TARGET_CELL varchar2(60)path '$.receive_cell',
    nested path '$.lots[*]'columns(LOT_UID varchar2(200)path '$.uid',SOURCE_CELL varchar2(60)path '$.issued_manifest.source_cell',QTY_TEXT varchar2(60)path '$.quantity',UNITS_JSON clob format json path '$.issued_manifest.units')))g
    on g.GROUP_FLAG='true'and g.LOT_UID=p_uid and g.SOURCE_CELL=p_source_cell and g.TARGET_CELL=p_target_cell and g.QTY_TEXT=RRL_STOCK_PLAN_HELPER.decimal_text(p_qty)and dbms_lob.compare(g.UNITS_JSON,p_units)=0
    where o.OPERATION_ID=op and o.COMMAND_TYPE='INTERWARE_RECEIVE'and o.STATE='IN_FLIGHT';
  end if;
"""+needle
assert needle in t;t=t.replace(needle,add,1)
out={d+'/000_before_units.sql':p.read_text(encoding='utf-8'),d+'/006a_units.sql':t}
p=Path(d+'/apply.sql');old=p.read_text(encoding='utf-8').replace('@@006_recompile.sql','@@006a_units.sql\n@@006_recompile.sql');out[p.as_posix()]=old
p=Path(d+'/rollback.sql');old=p.read_text(encoding='utf-8').replace('@@000_before_rec.sql','@@000_before_rec.sql\n@@000_before_units.sql');out[p.as_posix()]=old
print(json.dumps(out))
