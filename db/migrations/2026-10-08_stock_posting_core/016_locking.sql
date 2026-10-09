create or replace package RRL_STOCK_LOCK_API authid definer as
 function resource_lock_id(p_rank number,p_key raw) return number;
 function resource_key(p_kind varchar2,p_a varchar2,p_b varchar2 default null,p_c varchar2 default null) return raw;
 procedure begin_plan;
 procedure acquire_policies(p_plan clob);
 procedure acquire_resources(p_plan clob);
 procedure assert_held(p_rank number,p_key raw);
 procedure assert_policy(p_key raw,p_mode number);
 procedure clear_plan;
end;
/
create or replace package body RRL_STOCK_LOCK_API as
 type held_set is table of boolean index by varchar2(2100);
 type policy_set is table of number index by varchar2(2000);
 g_policies policy_set;
 g_held held_set; g_started number; g_phase varchar2(20); g_tx varchar2(100);
 function remaining_seconds return number is v_elapsed number;
 begin
  v_elapsed:=mod(dbms_utility.get_time-g_started+4294967296,4294967296)/100;
  if v_elapsed>=3 then raise_application_error(-20840,'LOCK_TIMEOUT: total lock budget exhausted'); end if;
  return greatest(0,3-v_elapsed);
 end;
 function resource_lock_id(p_rank number,p_key raw) return number is v raw(32);
 begin
  v:=sys.dbms_crypto.hash(utl_raw.concat(utl_i18n.string_to_raw(to_char(p_rank,'FM990')||':','AL32UTF8'),p_key),sys.dbms_crypto.hash_sh256);
  return mod(to_number(substr(rawtohex(v),1,8),'XXXXXXXX'),800000000);
 end;
 function resource_key(p_kind varchar2,p_a varchar2,p_b varchar2 default null,p_c varchar2 default null) return raw is
  v raw(1000); x raw(32767);
  procedure part(p varchar2) is z raw(32767);
  begin
   if p is null then raise_application_error(-20841,'RESOURCE_KEY_EMPTY'); end if;
   z:=utl_i18n.string_to_raw(p,'AL32UTF8');
   x:=utl_raw.concat(x,utl_i18n.string_to_raw(to_char(utl_raw.length(z),'FM9990')||':','AL32UTF8'),z);
  end;
 begin
  part('2');part(p_kind);part(p_a);
  if p_b is not null then part(p_b); end if;
  if p_c is not null then part(p_c); end if;
  if utl_raw.length(x)>1000 then raise_application_error(-20842,'RESOURCE_KEY_TOO_LONG'); end if;
  v:=x;return v;
 end;
 procedure clear_plan is begin g_held.delete;g_policies.delete;g_phase:=null;g_tx:=null;g_started:=null;end;
 procedure begin_plan is
 begin
  if dbms_transaction.local_transaction_id(false) is not null or g_phase is not null then
   raise_application_error(-20843,'DIRTY_TRANSACTION: no domain pre-locks or pre-writes permitted');
  end if;
  g_started:=dbms_utility.get_time;g_phase:='POLICY';
 end;
 procedure acquire_policies(p_plan clob) is v_result number; v_timeout number;
 begin
  if g_phase!='POLICY' or g_phase is null then raise_application_error(-20844,'LOCK_ORDER: policies must precede rows'); end if;
  for r in(select j.KEY_HEX,j.LOCK_MODE from
   json_table(p_plan,'$[*]' columns(KEY_HEX varchar2(2000) path '$.key_hex',LOCK_MODE number path '$.mode' error on error)) j) loop
   if r.KEY_HEX is null or not regexp_like(r.KEY_HEX,'^([0-9A-F]{2})+$','c')
    or r.LOCK_MODE is null or r.LOCK_MODE not in(4,6) then
    raise_application_error(-20845,'POLICY_PLAN_INVALID');
   end if;
  end loop;
  for r in(select p.LOCK_ID,p.POLICY_KEY,max(j.LOCK_MODE) LOCK_MODE from
    json_table(p_plan,'$[*]' columns(KEY_HEX varchar2(2000) path '$.key_hex',
      LOCK_MODE number path '$.mode' error on error)) j
    join RRL_STOCK_POLICY_GUARD p on p.POLICY_KEY=hextoraw(j.KEY_HEX)
    group by p.LOCK_ID,p.POLICY_KEY order by p.LOCK_ID) loop
   if r.LOCK_MODE is null or r.LOCK_MODE not in(4,6) then raise_application_error(-20845,'POLICY_MODE_INVALID'); end if;
   v_timeout:=floor(remaining_seconds);
   v_result:=sys.dbms_lock.request(r.LOCK_ID,r.LOCK_MODE,v_timeout,true);
   if v_result=1 then raise_application_error(-20840,'LOCK_TIMEOUT: policy fence'); end if;
   if v_result=2 then raise_application_error(-20846,'DEADLOCK_RETRY: policy fence'); end if;
   if v_result!=0 then raise_application_error(-20847,'POLICY_LOCK_PROTOCOL_ERROR: '||v_result); end if;
   g_policies(rawtohex(r.POLICY_KEY)):=r.LOCK_MODE;
  end loop;
  -- Every requested policy must be published. Do not silently skip missing keys.
  for r in(select j.KEY_HEX from json_table(p_plan,'$[*]' columns(KEY_HEX varchar2(2000) path '$.key_hex'))j
    where not exists(select 1 from RRL_STOCK_POLICY_GUARD p where p.POLICY_KEY=hextoraw(j.KEY_HEX))) loop
   raise_application_error(-20848,'POLICY_KEY_NOT_PUBLISHED');
  end loop;
  g_phase:='ROWS';
 end;
 procedure acquire_resources(p_plan clob) is v_rank number;v_id varchar2(2100);v_result number;v_locked number;
 begin
  if g_phase!='ROWS' or g_phase is null then raise_application_error(-20849,'LOCK_ORDER: one complete resource plan required');end if;
  -- Acquire all native mutexes in numeric order before creating or locking any guard row.
  -- Hash collisions only serialize unrelated keys; their common acquisition order prevents cycles.
  -- The policy range 900000000..949999999 is disjoint from resource IDs 0..799999999.
  for r in(select distinct RRL_STOCK_LOCK_API.resource_lock_id(j.RESOURCE_RANK,hextoraw(j.KEY_HEX)) LOCK_ID
   from json_table(p_plan,'$[*]' columns(RESOURCE_RANK number path '$.rank' error on error,
    KEY_HEX varchar2(2000) path '$.key_hex' error on error))j order by LOCK_ID) loop
   v_result:=sys.dbms_lock.request(r.LOCK_ID,6,floor(remaining_seconds),true);
   if v_result=1 then raise_application_error(-20840,'LOCK_TIMEOUT: resource mutex');end if;
   if v_result=2 then raise_application_error(-20846,'DEADLOCK_RETRY: resource mutex');end if;
   if v_result!=0 then raise_application_error(-20847,'RESOURCE_MUTEX_PROTOCOL_ERROR: '||v_result);end if;
  end loop;
  -- All shared keys are now exclusively owned. Set DML replaces one INSERT per unit.
  insert into RRL_STOCK_GUARD(RESOURCE_RANK,RESOURCE_KEY)
   select distinct j.RESOURCE_RANK,hextoraw(j.KEY_HEX) from json_table(p_plan,'$[*]'
    columns(RESOURCE_RANK number path '$.rank',KEY_HEX varchar2(2000) path '$.key_hex'))j
   where not exists(select 1 from RRL_STOCK_GUARD g where g.RESOURCE_RANK=j.RESOURCE_RANK and g.RESOURCE_KEY=hextoraw(j.KEY_HEX));
  -- NOWAIT is sufficient after native ownership. An unexpected external writer gets a whole-operation retry.
  for r in(select /*+ index(g RRL_STOCK_GUARD_PK) */ g.RESOURCE_RANK,g.RESOURCE_KEY
   from RRL_STOCK_GUARD g where (g.RESOURCE_RANK,g.RESOURCE_KEY) in
    (select j.RESOURCE_RANK,hextoraw(j.KEY_HEX) from json_table(p_plan,'$[*]'
     columns(RESOURCE_RANK number path '$.rank',KEY_HEX varchar2(2000) path '$.key_hex'))j)
   order by g.RESOURCE_RANK,g.RESOURCE_KEY) loop
   select RESOURCE_RANK into v_locked from RRL_STOCK_GUARD where RESOURCE_RANK=r.RESOURCE_RANK and RESOURCE_KEY=r.RESOURCE_KEY for update nowait;
   if r.RESOURCE_RANK not in(10,20,30,40,50,60,70) then raise_application_error(-20841,'RESOURCE_PLAN_INVALID');end if;
   v_id:=to_char(r.RESOURCE_RANK,'FM990')||':'||rawtohex(r.RESOURCE_KEY);g_held(v_id):=true;
  end loop;
  g_tx:=dbms_transaction.local_transaction_id(false);g_phase:='HELD';
 end;
 procedure assert_policy(p_key raw,p_mode number) is v_key varchar2(2000):=rawtohex(p_key);
 begin
  if g_phase is null or g_phase!='HELD' or g_tx is null
   or dbms_transaction.local_transaction_id(false) is null
   or g_tx!=dbms_transaction.local_transaction_id(false) or p_mode is null or p_mode not in(4,6)
   or not g_policies.exists(v_key) then raise_application_error(-20850,'POLICY_PLAN_VIOLATION'); end if;
  if g_policies(v_key)<p_mode then raise_application_error(-20850,'POLICY_MODE_INSUFFICIENT'); end if;
 end;
 procedure assert_held(p_rank number,p_key raw) is v_id varchar2(2100);
 begin
  v_id:=to_char(p_rank,'FM990')||':'||rawtohex(p_key);
  if g_phase!='HELD' or g_phase is null or g_tx is null
   or dbms_transaction.local_transaction_id(false) is null
   or g_tx!=dbms_transaction.local_transaction_id(false) or not g_held.exists(v_id) then
   raise_application_error(-20850,'WRITE_PLAN_VIOLATION');
  end if;
 end;
end;
/
