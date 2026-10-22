create or replace package RRL_TRADE_QUALITY_CASE_API authid definer as
 -- Quality exceptions of a TRADECASE site. OPEN (controller; pallet already in a quarantine cell, existing RRL_QUALITY_HOLD created)
 -- -> DEFECT | RELEASED (controller; RELEASED releases the hold) -> WAITING_POSTING (management approves the write-off of a DEFECT)
 -- -> POSTED only by the posting kind TRADE_QUALITY_WRITE_OFF (RRL_STOCK_QUALITY_WRITEOFF, real stock effect). The external SAP/SKM
 -- answer is a separate state read from the outgoing document. Every case command holds the pallet's STOCK lock (same as posting).
 procedure command(p_ware number,p_request clob,p_actor varchar2,p_result out clob);
 function overview(p_ware number,p_actor varchar2)return clob;
 function case_detail(p_ware number,p_actor varchar2,p_case number)return clob;
 -- Raises QUALITY_CASE_BLOCKS_RELEASE when an active case holds the pallet (UI pre-check; the native guard is root's candidate).
 procedure assert_release(p_ware number,p_actor varchar2,p_uid varchar2);
 -- 1 when every owner of the pallet/case/cell is readable; used inside SQL so hidden rows are filtered before any limit.
 function pallet_visible(p_actor varchar2,p_ware number,p_uid varchar2)return number;
 function case_visible(p_actor varchar2,p_ware number,p_case number)return number;
 function cell_visible(p_actor varchar2,p_ware number,p_cell varchar2)return number;
 -- Canonical composition hash of the pallet now; the write-off owner compares it with the frozen one.
 function composition_hash(p_uid varchar2)return varchar2;
end;
/
create or replace package body RRL_TRADE_QUALITY_CASE_API as
 procedure fail(p_code varchar2)is begin raise_application_error(-20911,p_code);end;
 function sha(p_text clob)return varchar2 is begin return lower(rawtohex(sys.dbms_crypto.hash(p_text,sys.dbms_crypto.hash_sh256)));end;
 function stamp(p_value timestamp with time zone)return varchar2 is
 begin return case when p_value is null then null else to_char(p_value at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"')end;end;
 function num(p_value number)return varchar2 is begin return RRL_STOCK_PLAN_HELPER.decimal_text(p_value);end;

 -- Same order as the other TRADECASE writers: current access revision, then the site row, then the case.
 procedure lock_site(p_ware number)is n number;
 begin
  lock table RRL_ACCESS_REV in share mode wait 5;
  select ENABLED into n from RRL_TRADE_SITE where WARE_ID=p_ware for update;
  if n<>1 then fail('TRADE_SITE_DISABLED');end if;
 exception when no_data_found then fail('TRADE_SITE_REQUIRED');
 end;

 -- The pallet's STOCK lock, the same dbms_lock the posting runner takes at rank 50: a case command and any stock command on the
 -- pallet are serialized, so composition checks and the hold are never raced by a move or a pick. Released on commit.
 procedure lock_stock(p_uid varchar2)is n number;
 begin
  n:=sys.dbms_lock.request(RRL_STOCK_LOCK_API.resource_lock_id(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid)),6,5,true);
  if n not in(0,4)then raise_application_error(-20890,'QUALITY_STOCK_LOCK_BUSY');end if;  -- busy: retry the same operation_id
 end;

 -- RRL_ACCESS_API.allowed returns 0 for a deleted RUSERS row first (alive), GLOBAL_ADMIN included.
 procedure require(p_actor varchar2,p_permission varchar2,p_ware number)is n number;
 begin
  select RRL_ACCESS_API.allowed(p_actor,p_permission,'WAREHOUSE',to_char(p_ware))into n from dual;
  if n<>1 then raise_application_error(-20882,'QUALITY_ACCESS_DENIED');end if;
 end;

 function pallet_visible(p_actor varchar2,p_ware number,p_uid varchar2)return number is n number;
 begin
  select count(*)into n from RRL_WMS_RECEIPT_UNIT u left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
   where u.CURRENT_UID=p_uid and u.STOCK_STATUS<>'ISSUED'
   and(a.OWNER_ID is null or RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,p_ware,a.OWNER_ID,0)<>1);
  return case when n=0 then 1 else 0 end;  -- an unowned unit is never shown as "visible" on a trade site
 end;

 function case_visible(p_actor varchar2,p_ware number,p_case number)return number is n number;
 begin
  select count(*)into n from RRL_TRADE_QUALITY_CASE_UNIT cu left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY
   where cu.CASE_ID=p_case and(a.OWNER_ID is null or RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,p_ware,a.OWNER_ID,0)<>1);
  return case when n=0 then 1 else 0 end;
 end;

 function cell_visible(p_actor varchar2,p_ware number,p_cell varchar2)return number is n number;
 begin
  -- Fail closed like pallet_visible: a code without an owner hides the cell.
  select count(*)into n from RRL_WMS_RECEIPT_UNIT u left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
   where u.CURRENT_CELL=p_cell and u.STOCK_STATUS<>'ISSUED'and(a.OWNER_ID is null or RRL_TRADE_STOCK_GUARD.owner_allowed(p_actor,p_ware,a.OWNER_ID,0)<>1);
  return case when n=0 then 1 else 0 end;
 end;

 -- Owners of the case: hidden -> "not found" (nothing leaks); readable without write -> TRADE_OWNER_ACCESS_DENIED.
 procedure require_case_owners(p_actor varchar2,p_ware number,p_case number,p_write number)is
 begin
  if case_visible(p_actor,p_ware,p_case)<>1 then fail('QUALITY_CASE_NOT_FOUND');end if;
  if p_write=1 then
   for o in(select distinct a.OWNER_ID from RRL_TRADE_QUALITY_CASE_UNIT cu join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY
     where cu.CASE_ID=p_case)loop
    RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,o.OWNER_ID,1);
   end loop;
  end if;
 end;

 -- Canonical composition of the pallet now (the same text is hashed at opening): unit key, version, SKU, quantity, owner.
 function composition(p_uid varchar2)return clob is c clob;
 begin
  dbms_lob.createtemporary(c,true);
  for u in(select u.PHYSICAL_UNIT_KEY K,u.UNIT_VERSION V,a.SKU_ID S,u.BASE_UOM M,u.BASE_QTY Q,a.OWNER_ID O from RRL_WMS_RECEIPT_UNIT u
    left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_UID=p_uid and u.STOCK_STATUS<>'ISSUED'
    order by u.PHYSICAL_UNIT_KEY)loop
   dbms_lob.append(c,u.K||'|'||u.V||'|'||u.S||'|'||u.M||'|'||num(u.Q)||'|'||u.O||chr(10));
  end loop;
  return c;
 end;

 function composition_hash(p_uid varchar2)return varchar2 is begin return sha(composition(p_uid));end;

 -- The pallet must still be the frozen one: same quarantine cell, stock version and code composition.
 procedure assert_unchanged(v RRL_TRADE_QUALITY_CASE%rowtype)is n number;
 begin
  select count(*)into n from RRL_REMAINS where UID_POLETA=v.PALLET_UID and CELL=v.CELL and REMAIN>0 and STOCK_VERSION=v.STOCK_VERSION;
  if n<>1 or sha(composition(v.PALLET_UID))<>v.COMPOSITION_HASH then fail('QUALITY_COMPOSITION_CHANGED');end if;
 end;

 -- Composition is read from the stock owners' rows (not copied): article, owner, quantity of the frozen unit keys.
 function summary(p_case number)return json_array_t is a json_array_t:=json_array_t();j json_object_t;
 begin
  for s in(select a.SKU_ID,a.OWNER_ID,u.BASE_UOM,sum(u.BASE_QTY)QTY,count(*)UNITS from RRL_TRADE_QUALITY_CASE_UNIT cu
    join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY
    where cu.CASE_ID=p_case group by a.SKU_ID,a.OWNER_ID,u.BASE_UOM order by a.SKU_ID,a.OWNER_ID)loop
   j:=json_object_t();j.put('sku_id',s.SKU_ID);j.put('owner_id',s.OWNER_ID);j.put('base_uom',s.BASE_UOM);j.put('base_qty',num(s.QTY));j.put('units',s.UNITS);
   a.append(j);
  end loop;
  return a;
 end;

 function card(v RRL_TRADE_QUALITY_CASE%rowtype,p_op varchar2)return json_object_t is j json_object_t:=json_object_t();ext varchar2(20);
 begin
  if p_op is not null then j.put('operation_id',p_op);end if;  -- every command receipt names its own operation
  j.put('case_id',v.CASE_ID);j.put('warehouse_id',v.WARE_ID);j.put('pallet_uid',v.PALLET_UID);j.put('cell',v.CELL);j.put('state',v.STATE);
  j.put('version',v.VERSION_NO);j.put('quality_hold_id',v.QUALITY_HOLD_ID);j.put('reason',v.REASON_TEXT);j.put('decision_note',v.DECISION_TEXT);
  j.put('approval_note',v.APPROVAL_TEXT);j.put('opened_by',v.OPENED_BY);j.put('opened_at',stamp(v.OPENED_AT));
  j.put('decided_by',v.DECIDED_BY);j.put('decided_at',stamp(v.DECIDED_AT));j.put('approved_by',v.APPROVED_BY);j.put('approved_at',stamp(v.APPROVED_AT));
  -- Honest stage: an approved write-off is not a posted one until a native posting owner writes the stock off.
  j.put('posted_by',v.POSTED_BY);j.put('posted_at',stamp(v.POSTED_AT));j.put('post_operation_id',v.POST_OPERATION_ID);
  if v.STATE='WAITING_POSTING'then j.put('posting_status','WAITING_NATIVE_POSTING');elsif v.STATE='POSTED'then j.put('posting_status','POSTED');
  else j.put_null('posting_status');end if;
  -- External answer is read from the outgoing document, never assumed.
  if v.STATE='POSTED'then
   select max(case when o.ACKNOWLEDGED_AT is not null then 'ACKNOWLEDGED'else 'PENDING'end)into ext from RRL_SAP_RECEIPT_OUTBOX o
    where o.EVENT_ID='QUALITY.WRITE_OFF:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(v.POST_OPERATION_ID,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
   j.put('external_status',nvl(ext,'MISSING'));
  else j.put_null('external_status');end if;
  j.put('composition',summary(v.CASE_ID));
  return j;
 end;

 procedure log_event(v RRL_TRADE_QUALITY_CASE%rowtype,p_op varchar2,p_action varchar2,p_from varchar2,p_at timestamp with time zone,
                     p_hash varchar2,p_actor varchar2,p_result out clob)is
 begin
  p_result:=card(v,p_op).to_clob;
  insert into RRL_TRADE_QUALITY_CASE_EVENT(OPERATION_ID,WARE_ID,CASE_ID,ACTION,FROM_STATE,TO_STATE,REQUEST_HASH,ACTOR,EVENT_AT,RESULT_JSON)
   values(p_op,v.WARE_ID,v.CASE_ID,p_action,p_from,v.STATE,p_hash,p_actor,p_at,p_result);
 end;

 procedure open_case(p_ware number,d json_object_t,p_op varchar2,p_hash varchar2,p_actor varchar2,p_result out clob)is
  v RRL_TRADE_QUALITY_CASE%rowtype;uid_value varchar2(200):=d.get_string('pallet_uid');reason varchar2(1000):=d.get_string('reason');
  n number;missing number;now timestamp with time zone:=systimestamp;
 begin
  if uid_value is null or reason is null or length(trim(reason))<3 then fail('QUALITY_REQUEST_INVALID');end if;
  -- Hidden owners first: an invisible pallet is "not found", whatever else is wrong with it.
  if pallet_visible(p_actor,p_ware,uid_value)<>1 then fail('QUALITY_PALLET_NOT_FOUND');end if;
  lock_stock(uid_value);  -- before reading stock: no move/pick can change it until this case commits
  if pallet_visible(p_actor,p_ware,uid_value)<>1 then fail('QUALITY_PALLET_NOT_FOUND');end if;
  begin select r.CELL,r.STOCK_VERSION into v.CELL,v.STOCK_VERSION from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL
    where r.UID_POLETA=uid_value and r.REMAIN>0 and c.WARE_ID=p_ware;
  exception when no_data_found then fail('QUALITY_PALLET_NOT_FOUND');
   when too_many_rows then fail('QUALITY_PALLET_SPLIT');end;
  select count(*)into n from RRL_CELLS where CELL=v.CELL and nvl(BLOCKED_FOR_REMAINS,0)=1;
  if n<>1 then fail('QUALITY_QUARANTINE_REQUIRED');end if;  -- the existing quarantine move comes first
  select count(*),count(*)-count(a.OWNER_ID)into n,missing from RRL_WMS_RECEIPT_UNIT u
   left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where u.CURRENT_UID=uid_value and u.STOCK_STATUS<>'ISSUED';
  if n=0 or missing>0 then fail('QUALITY_CODE_COMPOSITION_REQUIRED');end if;  -- fail closed: every code with its owner
  for o in(select distinct a.OWNER_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    where u.CURRENT_UID=uid_value and u.STOCK_STATUS<>'ISSUED')loop
   RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,p_ware,o.OWNER_ID,1);
  end loop;
  v.CASE_ID:=RRL_TRADE_QUALITY_CASE_SQ.nextval;v.WARE_ID:=p_ware;v.PALLET_UID:=uid_value;v.STATE:='OPEN';v.VERSION_NO:=1;
  v.COMPOSITION_HASH:=sha(composition(uid_value));v.REASON_TEXT:=substr(trim(reason),1,1000);v.OPENED_BY:=p_actor;v.OPENED_AT:=now;
  -- The hold is the existing quality entity, so traceability and any guard reading RRL_QUALITY_HOLD see the same fact.
  v.QUALITY_HOLD_ID:=RRL_TRACEABILITY_API.create_quality_hold('PALLET',uid_value,'TRADE_QUALITY_CASE',v.REASON_TEXT,p_actor);
  insert into RRL_TRADE_QUALITY_CASE values v;
  insert into RRL_TRADE_QUALITY_CASE_UNIT(CASE_ID,PHYSICAL_UNIT_KEY,UNIT_VERSION)
   select v.CASE_ID,u.PHYSICAL_UNIT_KEY,u.UNIT_VERSION from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=uid_value and u.STOCK_STATUS<>'ISSUED';
  log_event(v,p_op,'OPEN',null,now,p_hash,p_actor,p_result);
 exception when dup_val_on_index then fail('QUALITY_CASE_ACTIVE');
 end;

 procedure change_case(p_ware number,d json_object_t,p_op varchar2,p_hash varchar2,p_actor varchar2,p_result out clob)is
  v RRL_TRADE_QUALITY_CASE%rowtype;action varchar2(12):=d.get_string('action');id_value number:=d.get_number('case_id');
  expected number:=d.get_number('expected_version');decision varchar2(12):=d.get_string('decision');note varchar2(1000):=d.get_string('note');
  from_state varchar2(16);now timestamp with time zone:=systimestamp;
 begin
  begin select*into v from RRL_TRADE_QUALITY_CASE where CASE_ID=id_value and WARE_ID=p_ware for update;
  exception when no_data_found then fail('QUALITY_CASE_NOT_FOUND');end;
  lock_stock(v.PALLET_UID);
  require_case_owners(p_actor,p_ware,v.CASE_ID,1);
  if expected is null or expected<>v.VERSION_NO then fail('VERSION_CONFLICT');end if;
  if note is null or length(trim(note))<3 then fail('QUALITY_NOTE_REQUIRED');end if;
  from_state:=v.STATE;
  if action='DECIDE'and v.STATE='OPEN'and decision in('DEFECT','RELEASED')then
   assert_unchanged(v);v.STATE:=decision;v.DECISION_TEXT:=substr(trim(note),1,1000);v.DECIDED_BY:=p_actor;v.DECIDED_AT:=now;
   if decision='RELEASED'then RRL_TRACEABILITY_API.release_quality_hold(v.QUALITY_HOLD_ID,p_actor,v.DECISION_TEXT);end if;
  elsif action='APPROVE'and v.STATE='DEFECT'then
   -- Management approves the write-off of exactly the frozen composition; the stock stays held until a native posting owner exists.
   assert_unchanged(v);v.STATE:='WAITING_POSTING';v.APPROVAL_TEXT:=substr(trim(note),1,1000);v.APPROVED_BY:=p_actor;v.APPROVED_AT:=now;
  else fail('QUALITY_STATE_CONFLICT');end if;
  v.VERSION_NO:=v.VERSION_NO+1;
  update RRL_TRADE_QUALITY_CASE set row=v where CASE_ID=v.CASE_ID;
  log_event(v,p_op,action,from_state,now,p_hash,p_actor,p_result);
 end;

 procedure command(p_ware number,p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');act varchar2(12):=d.get_string('action');
  permission varchar2(40);hash_value varchar2(64):=sha(p_request);e RRL_TRADE_QUALITY_CASE_EVENT%rowtype;j json_object_t;
 begin
  if op is null or lengthb(op)>100 or not regexp_like(op,'^[A-Za-z0-9_.:-]+$')then fail('QUALITY_REQUEST_INVALID');end if;
  -- The controller determines the state; management approves the write-off document.
  permission:=case act when 'OPEN'then 'tradecase_quality_control' when 'DECIDE'then 'tradecase_quality_control' when 'APPROVE'then 'tradecase_quality_approve'end;
  if permission is null then fail('QUALITY_REQUEST_INVALID');end if;
  -- Scope first: without the warehouse right nobody learns whether the site exists. Checked again under the locks.
  require(p_actor,permission,p_ware);
  lock_site(p_ware);
  require(p_actor,permission,p_ware);
  begin
   select*into e from RRL_TRADE_QUALITY_CASE_EVENT where OPERATION_ID=op;
   if e.WARE_ID<>p_ware then fail('QUALITY_OPERATION_CONFLICT');end if;
   -- Owner rights of today, before anything about the stored operation is revealed; a receipt belongs to its own actor and body.
   require_case_owners(p_actor,p_ware,e.CASE_ID,1);
   if e.ACTOR<>p_actor or e.REQUEST_HASH<>hash_value then fail('QUALITY_OPERATION_CONFLICT');end if;
   j:=json_object_t.parse(e.RESULT_JSON);j.put('replayed',true);p_result:=j.to_clob;return;
  exception when no_data_found then null;end;
  if act='OPEN'then open_case(p_ware,d,op,hash_value,p_actor,p_result);
  else change_case(p_ware,d,op,hash_value,p_actor,p_result);end if;
  j:=json_object_t.parse(p_result);j.put('replayed',false);p_result:=j.to_clob;
 end;

 procedure assert_release(p_ware number,p_actor varchar2,p_uid varchar2)is n number;
 begin
  require(p_actor,'tradecase_view',p_ware);
  select count(*)into n from RRL_TRADE_QUALITY_CASE where WARE_ID=p_ware and PALLET_UID=p_uid and STATE in('OPEN','DEFECT','WAITING_POSTING');
  if n>0 then fail('QUALITY_CASE_BLOCKS_RELEASE');end if;
 end;

 function quarantine(p_ware number,p_actor varchar2)return json_array_t is a json_array_t:=json_array_t();j json_object_t;
 begin
  -- Pallets in quarantine cells of the site (natively excluded from allocation/picking/shipping); hidden owners filtered first.
  for x in(select r.UID_POLETA,r.CELL,r.REMAIN,r.BASE_UOM,r.STOCK_VERSION,p.ARTICUL,
     (select max(q.CASE_ID)from RRL_TRADE_QUALITY_CASE q where q.PALLET_UID=r.UID_POLETA and q.WARE_ID=p_ware)CASE_ID
    from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
    where c.WARE_ID=p_ware and nvl(c.BLOCKED_FOR_REMAINS,0)=1 and r.REMAIN>0 and pallet_visible(p_actor,p_ware,r.UID_POLETA)=1
    order by r.CELL,r.UID_POLETA fetch first 200 rows only)loop
   j:=json_object_t();j.put('pallet_uid',x.UID_POLETA);j.put('cell',x.CELL);j.put('article',x.ARTICUL);j.put('base_qty',num(x.REMAIN));
   j.put('base_uom',x.BASE_UOM);j.put('stock_version',x.STOCK_VERSION);j.put('case_id',x.CASE_ID);a.append(j);
  end loop;
  return a;
 end;

 function discrepancies(p_ware number,p_actor varchar2)return json_array_t is a json_array_t:=json_array_t();j json_object_t;
 begin
  for x in(select INVENTORY_TASK_ID,STATUS,CELL_CODE,ARTICUL,PLANNED_QTY,FACT_QTY,REVISION_ID,ASSIGNED_TO,UPDATED_AT from RRL_INVENTORY_TASK
    where WARE_ID=p_ware and(STATUS not in('DONE','CANCELLED','CLOSED')or(FACT_QTY is not null and FACT_QTY<>nvl(PLANNED_QTY,-1)))
    and cell_visible(p_actor,p_ware,CELL_CODE)=1 order by INVENTORY_TASK_ID desc fetch first 100 rows only)loop
   j:=json_object_t();j.put('inventory_task_id',x.INVENTORY_TASK_ID);j.put('status',x.STATUS);j.put('cell',x.CELL_CODE);j.put('article',x.ARTICUL);
   j.put('planned_qty',num(x.PLANNED_QTY));j.put('fact_qty',num(x.FACT_QTY));j.put('revision_id',x.REVISION_ID);j.put('assigned_to',x.ASSIGNED_TO);
   j.put('updated_at',stamp(cast(x.UPDATED_AT as timestamp with time zone)));a.append(j);
  end loop;
  return a;
 end;

 function overview(p_ware number,p_actor varchar2)return clob is r json_object_t:=json_object_t();a json_array_t:=json_array_t();n number;
  v RRL_TRADE_QUALITY_CASE%rowtype;
 begin
  require(p_actor,'tradecase_view',p_ware);
  r.put('observed_at',stamp(systimestamp));r.put('quarantine',quarantine(p_ware,p_actor));
  for x in(select CASE_ID from RRL_TRADE_QUALITY_CASE where WARE_ID=p_ware and case_visible(p_actor,p_ware,CASE_ID)=1
    order by case when STATE in('OPEN','DEFECT')then 0 when STATE='WAITING_POSTING'then 1 else 2 end,CASE_ID desc fetch first 100 rows only)loop
   select*into v from RRL_TRADE_QUALITY_CASE where CASE_ID=x.CASE_ID;a.append(card(v,null));
  end loop;
  r.put('cases',a);
  -- Count discrepancies are shown only with the existing inventory right; otherwise the section is closed, not empty.
  select RRL_ACCESS_API.allowed(p_actor,'stock_inventory_count','WAREHOUSE',to_char(p_ware))into n from dual;
  if n=1 then r.put('discrepancies',discrepancies(p_ware,p_actor));else r.put_null('discrepancies');end if;
  return r.to_clob;
 end;

 function case_detail(p_ware number,p_actor varchar2,p_case number)return clob is v RRL_TRADE_QUALITY_CASE%rowtype;j json_object_t;
  units json_array_t:=json_array_t();u json_object_t;events json_array_t:=json_array_t();
 begin
  require(p_actor,'tradecase_view',p_ware);
  begin select*into v from RRL_TRADE_QUALITY_CASE where CASE_ID=p_case and WARE_ID=p_ware;
  exception when no_data_found then fail('QUALITY_CASE_NOT_FOUND');end;
  require_case_owners(p_actor,p_ware,p_case,0);
  j:=card(v,null);
  for x in(select cu.PHYSICAL_UNIT_KEY,cu.UNIT_VERSION FROZEN,u.UNIT_VERSION NOW_VERSION,a.SKU_ID,u.BASE_UOM,u.BASE_QTY,a.OWNER_ID,u.CURRENT_UID,u.STOCK_STATUS
    from RRL_TRADE_QUALITY_CASE_UNIT cu join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY
    join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=cu.PHYSICAL_UNIT_KEY where cu.CASE_ID=p_case
    order by a.SKU_ID,cu.PHYSICAL_UNIT_KEY fetch first 2000 rows only)loop
   u:=json_object_t();u.put('unit_key',x.PHYSICAL_UNIT_KEY);u.put('sku_id',x.SKU_ID);u.put('base_uom',x.BASE_UOM);
   u.put('base_qty',num(x.BASE_QTY));u.put('owner_id',x.OWNER_ID);
   u.put('unchanged',x.FROZEN=x.NOW_VERSION and x.CURRENT_UID=v.PALLET_UID and x.STOCK_STATUS<>'ISSUED');units.append(u);
  end loop;
  j.put('units',units);
  for x in(select ACTION,FROM_STATE,TO_STATE,ACTOR,EVENT_AT from RRL_TRADE_QUALITY_CASE_EVENT where CASE_ID=p_case order by EVENT_AT)loop
   u:=json_object_t();u.put('action',x.ACTION);u.put('from_state',x.FROM_STATE);u.put('to_state',x.TO_STATE);u.put('actor',x.ACTOR);
   u.put('at',stamp(x.EVENT_AT));events.append(u);
  end loop;
  -- The posting itself is journaled by the stock posting runner (RRL_STOCK_OPERATION); shown here from the case's own facts.
  if v.STATE='POSTED'then
   u:=json_object_t();u.put('action','POST');u.put('from_state','WAITING_POSTING');u.put('to_state','POSTED');u.put('actor',v.POSTED_BY);
   u.put('at',stamp(v.POSTED_AT));u.put('operation_id',v.POST_OPERATION_ID);events.append(u);
  end if;
  j.put('events',events);
  return j.to_clob;
 end;
end;
/
