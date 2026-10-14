from pathlib import Path
import json
out={}
root=Path("db/migrations/2026-10-11_ni022_admission")
p=Path("db/migrations/2026-10-11_ni022_calendar/002_api.sql")
s=p.read_text(encoding="utf-8").replace(' procedure configure(p_ware number,p_store varchar2,p_body clob,p_actor varchar2,p_result out clob);',' procedure configure(p_ware number,p_store varchar2,p_body clob,p_actor varchar2,p_result out clob);\n procedure delivery_rule(p_ware number,p_store_id number,p_day date,p_offset out number,p_allowed out number,p_proof out clob);',1)
point=s.index(' procedure configure(p_ware number,p_store varchar2,p_body clob,p_actor varchar2,p_result out clob)is')
method=""" procedure delivery_rule(p_ware number,p_store_id number,p_day date,p_offset out number,p_allowed out number,p_proof out clob)is
  v_days varchar2(20);v_same number;v_state varchar2(10);v_version number;v_operation varchar2(100);v_weekday number;b json_object_t:=json_object_t();
 begin
  if p_day is null or p_day!=trunc(p_day)then raise_application_error(-20886,'STORE_CAL_LOCAL_DELIVERY_DATE_REQUIRED');end if;
  begin
   select cal.UTC_OFFSET_MINUTES,cal.DELIVERY_WEEKDAYS,cal.ALLOW_SAME_DAY,ex.DAY_STATE,ex.VERSION_NO,ex.OPERATION_ID
    into p_offset,v_days,v_same,v_state,v_version,v_operation
    from RRL_SAP_STORE_CALENDAR cal
    join RRL_CUSTOMER_STORE_MAP m on m.CUSTOMER_STORE_MAP_ID=cal.CUSTOMER_STORE_MAP_ID and m.ACTIVE=1
    join RRL_CUSTOMER c on c.CUSTOMER_ID=m.CUSTOMER_ID and c.ACTIVE=1
    left join RRL_SAP_STORE_CAL_EXCEPTION ex on ex.WARE_ID=cal.WARE_ID and ex.CUSTOMER_STORE_MAP_ID=cal.CUSTOMER_STORE_MAP_ID
      and ex.DELIVERY_DATE=p_day and ex.VERSION_NO=(select max(latest.VERSION_NO)from RRL_SAP_STORE_CAL_EXCEPTION latest
        where latest.WARE_ID=cal.WARE_ID and latest.CUSTOMER_STORE_MAP_ID=cal.CUSTOMER_STORE_MAP_ID and latest.DELIVERY_DATE=p_day)
    where cal.WARE_ID=p_ware and cal.CUSTOMER_STORE_MAP_ID=p_store_id;
  exception when no_data_found then raise_application_error(-20886,'STORE_CAL_ACTIVE_SOURCE_BOOK_REQUIRED');end;
  v_weekday:=p_day-trunc(p_day,'IW')+1;
  if v_state='OPEN'then p_allowed:=1;elsif v_state='CLOSED'then p_allowed:=0;
   elsif instr(','||v_days||',',','||to_char(v_weekday,'FM9')||',')>0 then p_allowed:=1;else p_allowed:=0;end if;
  b.put('warehouse_id',p_ware);b.put('store_map_id',p_store_id);b.put('delivery_date',to_char(p_day,'YYYY-MM-DD'));
  b.put('utc_offset_minutes',p_offset);b.put('delivery_weekdays',v_days);b.put('allow_same_day',v_same=1);b.put('allowed',p_allowed=1);
  b.put('calendar_basis',case when v_state is null then 'WEEKLY_SOURCE_BOOK'else 'DATE_EXCEPTION'end);
  if v_state is not null then b.put('exception_state',v_state);b.put('exception_version',v_version);b.put('exception_operation_id',v_operation);end if;
  p_proof:=b.to_clob;
 end;
"""
out[str(root/"002_calendar.sql")]=s[:point]+method+s[point:]
p=Path("db/migrations/2026-10-11_ni022_calendar/004_metadata_permission.sql")
s=p.read_text(encoding="utf-8").replace("'customer_rule_edit'","'customer_rule_edit','sap_store_decision_import'")
out[str(root/"005_metadata_permission.sql")]=s
out[str(root/"005b_metadata_body.sql")]=s[s.lower().index("create or replace package body"):]
p=Path("db/migrations/2026-10-07_ni02_store_orders/008_apply.sql")
s=p.read_text(encoding="utf-8");a=s.lower().index("create or replace trigger rrl_sap_store_pick_guard");b=s.lower().index("merge into rrl_schema_migrations",a)
out[str(root/"rollback_pick_guard.sql")]=s[a:b]
p=root/"rollback.sql";s=p.read_text(encoding="utf-8").replace("-- Restore prior SAP pickguard from original008 source checkpoint, preserveotherSourceguards.","@@rollback_pick_guard.sql")
out[str(p)]=s
# Live body-only metadata replaces the same complete canonical specification.
p=root/"apply.sql";out[str(p)]=p.read_text(encoding="utf-8").replace("@@005_metadata_permission.sql","@@005b_metadata_body.sql")
print(json.dumps(out,ensure_ascii=True))
