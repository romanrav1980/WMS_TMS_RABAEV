from pathlib import Path
import json
base=Path("db/migrations/2026-10-08_stock_posting_core");folder=Path("db/migrations/2026-10-10_ni063_booked_handover")
s=(base/"411_checkpoint_before_booked_handover.sql").read_text(encoding="utf-8-sig")
s="\n".join(line for line in s.splitlines() if line.strip())+"\n"
s=s.replace("v_offer_id varchar2(100);","v_offer_id varchar2(100);v_books json_array_t:=json_array_t();",1)
needle="if kind in('TARE_OFFER','TARE_ACCEPT') and v_from_kind='WAREHOUSE' then RRL_TARE_PLANNING.assert_available(v_from,v_from_qty,v_qty);end if;"
assert needle in s
s=s.replace(needle,"if kind in('TARE_OFFER','TARE_ACCEPT') then\n RRL_STOCK_TARE_HANDOVER.describe_books(p_request,kind,v_offer_id,v_owner,v_type,v_condition,v_from_kind,v_tt,v_vehicle,v_qty,v_books);p_domain.put('booked_places',v_books);\n if v_from_kind='WAREHOUSE' then RRL_TARE_PLANNING.assert_available(v_from,v_from_qty+v_books.get_size,v_qty);end if;end if;",1)
needle="p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;"
assert needle in s
s=s.replace(needle,"if kind in('TARE_OFFER','TARE_ACCEPT') then RRL_STOCK_TARE_HANDOVER.declare_books(v.get_array('booked_places'),case when kind='TARE_OFFER' then p_operation else v.get_string('offer_operation_id')end,r);end if;\n "+needle,1)
needle="values(op,v_from,v_to,v_tt,v_vehicle,v_vehicle_num,v_store,v_owner,v_type,v_condition,v_from_kind,v_from_id,v_to_kind,v_to_id,v_qty,p_actor);"
assert needle in s
s=s.replace(needle,needle+"\n  RRL_STOCK_TARE_HANDOVER.persist_offer(op,v.get_array('booked_places'));",1)
needle="values(op,v_offer,v_qty,v_offered-v_qty,p_actor);"
assert needle in s
s=s.replace(needle,needle+"\n   RRL_STOCK_TARE_HANDOVER.transfer_books(v.get_array('booked_places'),op,p_actor);",1)
guard=Path("db/migrations/2026-10-10_ni063_tare_assembly/008_book_guards.sql").read_text(encoding="utf-8-sig")
guard=guard.replace(":new.STATUS!='CANCELLED'",":new.STATUS not in('CANCELLED','TRANSFERRED')",1)
guard=guard.replace("RRL_TARE_ASSERT_WRITE('RRL_TARE_BOOK',:new.OPERATION_ID,'TARE_BOOK_CANCEL');","RRL_TARE_ASSERT_WRITE('RRL_TARE_BOOK',:new.OPERATION_ID,case when :new.STATUS='TRANSFERRED' then 'TARE_ACCEPT' else 'TARE_BOOK_CANCEL' end);",1)
guard+='''
create or replace trigger RRL_TARE_OFFER_BOOK_GUARD before insert or update or delete on RRL_TARE_OFFER_BOOK for each row
begin
 if not inserting then raise_application_error(-20863,'TARE_OFFER_BOOK_HISTORY_IMMUTABLE');end if;
 if :new.OFFER_OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_ROOT_OPERATION_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_OFFER_BOOK',:new.OFFER_OPERATION_ID||':'||:new.BOOK_OPERATION_ID,'TARE_OFFER');
end;
/
'''
out={str(folder/"003_tare_command.sql"):s,str(folder/"004_guards.sql"):guard}
print(json.dumps(out,ensure_ascii=True))
