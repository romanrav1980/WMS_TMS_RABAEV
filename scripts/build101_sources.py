from pathlib import Path
import json
base=Path("db/migrations/2026-10-08_stock_posting_core");folder=Path("db/migrations/2026-10-10_ni063_tare_assembly")
tare=(base/"408_checkpoint_before_tare_assembly.sql").read_text(encoding="utf-8-sig")
needle="if kind='TARE_COUNT' and(m.get_number('expected_version')"
assert needle in tare
tare=tare.replace(needle,"if kind='TARE_COUNT' and v_qty<RRL_TARE_PLANNING.held_quantity(v_to) then raise_application_error(-20886,'TARE_COUNT_BELOW_ASSEMBLY_HOLD');end if;\n if kind in('TARE_OFFER','TARE_ACCEPT') and v_from_kind='WAREHOUSE' then RRL_TARE_PLANNING.assert_available(v_from,v_from_qty,v_qty);end if;\n "+needle,1)
resolve=(base/"409_checkpoint_before_tare_assembly.sql").read_text(encoding="utf-8-sig")
needle="if v_qty>v_from_qty then raise_application_error(-20886,'TARE_SOURCE_QUANTITY_UNAVAILABLE');end if;"
assert needle in resolve
resolve=resolve.replace(needle,needle+"\n if kind='TARE_DAMAGE' and v_holder='WAREHOUSE' then RRL_TARE_PLANNING.assert_available(v_from,v_from_qty,v_qty);end if;",1)
# Keep the established TT -> vehicle -> balance native-row order.
loop_line=next(line for line in resolve.splitlines() if "for row_record in(select BALANCE_KEY" in line)
resolve=resolve.replace(loop_line+"\n","",1).replace(" describe_command(p_request,p_actor,fresh);",loop_line+"\n describe_command(p_request,p_actor,fresh);",1)
root=(base/"410_checkpoint_before_tare_assembly.sql").read_text(encoding="utf-8-sig")
needle="elsif g_kind in('TARE_DAMAGE','TARE_WRITE_OFF') then"
root=root.replace(needle,"elsif g_kind in('TARE_BOOK','TARE_BOOK_CANCEL') then RRL_STOCK_TARE_BOOK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n  "+needle,1)
needle="elsif g_kind in('TARE_DAMAGE','TARE_WRITE_OFF') then RRL_STOCK_TARE_RESOLVE.execute_command"
root=root.replace(needle,"elsif g_kind in('TARE_BOOK','TARE_BOOK_CANCEL') then RRL_STOCK_TARE_BOOK_CMD.execute_command(g_request,g_actor,p_result);\n  "+needle,1)
guard=Path("db/migrations/2026-10-10_ni063_tare_resolution/007_guards.sql").read_text(encoding="utf-8-sig")
guard=guard.replace("v_kind in('TARE_COUNT','TARE_ACCEPT','TARE_DAMAGE','TARE_WRITE_OFF')","v_kind in('TARE_COUNT','TARE_ACCEPT','TARE_DAMAGE','TARE_WRITE_OFF','TARE_BOOK','TARE_BOOK_CANCEL')")
out={str(folder/"004_tare_command.sql"):tare,str(folder/"005_resolution_command.sql"):resolve,str(folder/"006_root.sql"):root,str(folder/"007_balance_guards.sql"):guard}
print(json.dumps({p:"\n".join(line for line in text.splitlines() if line.strip())+"\n" for p,text in out.items()},ensure_ascii=True))
