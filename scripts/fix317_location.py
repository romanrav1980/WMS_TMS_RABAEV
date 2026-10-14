from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_nested_placement");out={}
body="\n".join(line.rstrip()for line in Path("tmp/317_rrl_stock_hu_cmd_body.sql").read_text(encoding="utf-8").splitlines())+"\n"
out[(d/"000_before_hu_cmd.sql").as_posix()]="create or replace "+body+"\n/\n"
needle="     v_mode:=case when x.get_number('case_task_id') is not null";a=body.index(needle);b=body.index("\n",a)
body=body[:b]+"""
     if v.has('interwarehouse_placement')then
      declare iw json_object_t:=v.get_object('interwarehouse_placement');begin
       if d.get_string('command_type')!='HU_TASK_COMPLETE'or iw.get_string('uid')!=v_leaf_uid or iw.get_string('from_cell')!=v_from or iw.get_string('target_cell')!=v_target or iw.get_number('warehouse_id')!=v_ware or RRL_STOCK_MATH.quantity(iw.get_string('quantity'))!=v_qty then raise_application_error(-20886,'INTERWARE_HU_PUTAWAY_EXACT_RECEIPT_REQUIRED');end if;
       v_mode:='PUTAWAY';
      end;
     end if;
"""+body[b:]
out[(d/"008_hu_cmd.sql").as_posix()]="create or replace "+body+"\n/\n"
p=d/"apply.sql";out[p.as_posix()]=p.read_text(encoding="utf-8").replace("@@006_recompile.sql","@@008_hu_cmd.sql\n@@006_recompile.sql")
p=d/"rollback.sql";out[p.as_posix()]=p.read_text(encoding="utf-8").replace("@@006_recompile.sql","@@000_before_hu_cmd.sql\n@@006_recompile.sql")
print(json.dumps(out))
