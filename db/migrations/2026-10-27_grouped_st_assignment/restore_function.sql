create or replace function RRL_TT_ADD_PALL(TT_ID int,ST_NUMBER1 varchar2) return varchar2 is
  target_id number:=case when TT_ID>0 then TT_ID else null end;
  trips sys.odcinumberlist:=sys.odcinumberlist();
  st_ids sys.odcinumberlist:=sys.odcinumberlist();
  old_trips sys.odcinumberlist:=sys.odcinumberlist();
  actual_trip number; actual_condition number; task_state varchar2(100);
  deleted_flag number; bill number; result varchar2(1024); found number:=0;
begin
  if ST_NUMBER1 is null or length(ST_NUMBER1)>200 or TT_ID is null or TT_ID<0 then
    raise_application_error(-20886,'TRIP_ASSIGNMENT_INPUT_INVALID');
  end if;
  -- Discover without locking, then TT ascending -> actual ST ID ascending.
  -- Concurrent membership changes invalidate the snapshot; never acquire another TT late.
  for r in(select ID,TRANSTASK_ID from RRL_SBORKA_PALLETS where ST_NUMBER=ST_NUMBER1 order by ID)loop
    st_ids.extend;st_ids(st_ids.count):=r.ID;old_trips.extend;old_trips(old_trips.count):=nvl(r.TRANSTASK_ID,0);
    if st_ids.count>200 then raise_application_error(-20886,'ST_ASSIGNMENT_BATCH_BOUND');end if;
  end loop;
  if st_ids.count=0 then raise_application_error(-20886,'ST_ASSIGNMENT_NOT_FOUND');end if;
  for r in(select distinct t from(
    select column_value t from table(old_trips) where column_value>0
    union select target_id from dual where target_id is not null)order by t)loop
    trips.extend;trips(trips.count):=r.t;
  end loop;
  for i in 1..trips.count loop
    select CONDITION,DELETED,PAY_ORDER_ID into task_state,deleted_flag,bill
      from RRL_TRANSPORT_TASK where ID=trips(i) for update;
    if nvl(deleted_flag,0)!=0 or task_state='Отгружен' or nvl(bill,0)>0 then
      raise_application_error(-20886,'TRIP_MEMBERSHIP_CHANGE_FORBIDDEN');
    end if;
  end loop;
  for i in 1..st_ids.count loop
    select TRANSTASK_ID,CONDITION into actual_trip,actual_condition from RRL_SBORKA_PALLETS where ID=st_ids(i) for update;
    if nvl(actual_trip,0)!=old_trips(i) then raise_application_error(-20886,'TRIP_MEMBERSHIP_SNAPSHOT_CHANGED');end if;
    if nvl(actual_trip,0)!=nvl(target_id,0) then
      if actual_condition=2 then raise_application_error(-20886,'SHIPPED_ST_REASSIGNMENT_FORBIDDEN');end if;
      if target_id is not null and actual_trip is not null and actual_trip>0 then
        raise_application_error(-20886,'ST_ALREADY_ASSIGNED_TO_ANOTHER_TRIP');
      end if;
      select count(*) into found from RRL_TT_HU_LOAD_ST where SBORKA_PALLET_ID=st_ids(i) and ACTIVE_FLAG=1;
      if found>0 then raise_application_error(-20886,'LOADED_ST_REASSIGNMENT_FORBIDDEN');end if;
    end if;
  end loop;
  select count(*) into found from RRL_SBORKA_PALLETS where ST_NUMBER=ST_NUMBER1;
  if found!=st_ids.count then raise_application_error(-20886,'ST_ASSIGNMENT_SNAPSHOT_CHANGED');end if;
  -- Exact declared IDs only: no late-discovered rows, no commit in a legacy function.
  for i in 1..st_ids.count loop
    RRL_TT_MEMBERSHIP_CTX_API.begin_member(st_ids(i),target_id);
    update RRL_SBORKA_PALLETS set TRANSTASK_ID=target_id where ID=st_ids(i);
    RRL_TT_MEMBERSHIP_CTX_API.end_member;
  end loop;
  for i in 1..trips.count loop
    result:=RRL_TT_REGIONS(trips(i));
    update RRL_TRANSPORT_TASK set TEMP_REGION=result where ID=trips(i);
  end loop;
  return nvl(result,'OK');
exception when others then RRL_TT_MEMBERSHIP_CTX_API.end_member;raise;
end;
/
