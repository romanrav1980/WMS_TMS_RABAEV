-- Refuse operational rollback while retained booked CASE links exist; forward repair preserves facts.
declare n number;begin select count(*)into n from RRL_WMS_HU_LINK h join RRL_TARE_BOOK b on b.PLACE_KIND='CASE'and b.PLACE_ID=to_char(h.CHILD_CASE_TASK_ID,'TM9')and b.STATUS='HELD'where h.ACTIVE_FLAG=1;if n>0 then raise_application_error(-20808,'NESTED_TARE_FORWARD_REPAIR_REQUIRED');end if;end;
/
@@000_before_hu.sql
@@000_before_root.sql
@@000_before_handover.sql
@@000_before_guard.sql
