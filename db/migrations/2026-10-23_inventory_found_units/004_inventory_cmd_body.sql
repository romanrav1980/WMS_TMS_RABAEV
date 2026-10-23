create or replace package body RRL_STOCK_INVENTORY_CMD as

 procedure compile_count(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is

  d json_object_t:=json_object_t.parse(p_request);a json_array_t;b json_array_t:=json_array_t();x json_object_t;y json_object_t;v json_object_t:=json_object_t();

  f json_array_t:=json_array_t();r json_array_t:=json_array_t();doc number;ware number;article varchar2(160);base varchar2(20);inputu varchar2(20);

  qty number;ver number;stockver number;signature varchar2(64);p number;h number;k varchar2(2000);

  revision_row number;row_doc number;row_cell varchar2(60);row_article varchar2(160);

  type keys is table of boolean index by varchar2(2000);seen keys;

 begin

  doc:=d.get_object('source').get_number('revision_id');select WARE_ID into ware from RRL_REVIZION where ID=doc;

  a:=d.get_object('metadata').get_array('counts');

  if a is null or a.get_size>200 or (a.get_size<1 and not d.get_object('metadata').has('inventory_task_id')) then raise_application_error(-20881,'INVENTORY_COUNT_BATCH_BOUND');end if;

  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);

  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_REVIZION',RRL_STOCK_PLAN_HELPER.decimal_text(doc));

  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));

  if d.get_object('metadata').has('revision_row_id') then

   revision_row:=d.get_object('metadata').get_number('revision_row_id');

   if a.get_size!=1 or revision_row is null then raise_application_error(-20871,'INVENTORY_REVISION_ROW_SINGLE_LOT_REQUIRED');end if;

   x:=treat(a.get(0) as json_object_t);

   select REVISION_ID,CELL,ARTICUL1 into row_doc,row_cell,row_article from RRL_REVISION_ROW where ID=revision_row;

   if row_doc is null or row_doc!=doc or row_cell is null or row_cell!=x.get_string('cell')

    or row_article is null or row_article!=x.get_string('article') then raise_application_error(-20887,'INVENTORY_REVISION_ROW_IDENTITY_CONFLICT');end if;

   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_REVISION_ROW',RRL_STOCK_PLAN_HELPER.decimal_text(revision_row));

  end if;

  for i in 0..a.get_size-1 loop

   x:=treat(a.get(i) as json_object_t);declare

 v_json_sql_1_1 varchar2(32767):=x.get_string('uid');

begin

select ARTICUL into article from RRL_PALLETS where UID_PALLET=v_json_sql_1_1;

end;

   if article is null or article!=x.get_string('article') then raise_application_error(-20887,'INVENTORY_LOT_ARTICLE_CONFLICT');end if;

   k:=rawtohex(RRL_STOCK_LOCK_API.resource_key('STOCK',x.get_string('uid'),x.get_string('cell')));if seen.exists(k) then raise_application_error(-20885,'INVENTORY_LOT_REPEATED');end if;seen(k):=true;

   inputu:=x.get_string('unit');

   RRL_STOCK_PALLET_UOM.resolve_quantity(x.get_string('uid'),inputu,

    case when regexp_like(x.get_string('quantity'),'^0([.]0{1,9})?$') then '1' else x.get_string('quantity') end,base,qty,ver,signature);

   if regexp_like(x.get_string('quantity'),'^0([.]0{1,9})?$') then qty:=0;end if;

   begin declare

 v_json_sql_2_1 varchar2(32767):=x.get_string('uid');

 v_json_sql_2_2 varchar2(32767):=x.get_string('cell');

begin

select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into p,h,stockver from RRL_REMAINS where UID_POLETA=v_json_sql_2_1 and CELL=v_json_sql_2_2;

end;

   exception when no_data_found then p:=0;h:=0;stockver:=0;end;

   if x.get_number('expected_stock_version') is null or x.get_number('expected_stock_version')!=stockver then raise_application_error(-20867,'INVENTORY_SNAPSHOT_STALE');end if;

   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,x.get_string('uid'),article,x.get_string('cell'),null);
   if x.has('found_unit_keys') then declare g json_array_t:=x.get_array('found_unit_keys');begin
    if g.get_size>10000 then raise_application_error(-20881,'INVENTORY_FOUND_UNIT_BOUND');end if;
    for q in 0..g.get_size-1 loop RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',g.get_string(q));end loop;end;end if;

   y:=json_object_t();y.put('uid',x.get_string('uid'));y.put('cell',x.get_string('cell'));y.put('article',article);

   y.put('base',base);y.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));y.put('p',RRL_STOCK_PLAN_HELPER.decimal_text(p));

   y.put('h',RRL_STOCK_PLAN_HELPER.decimal_text(h));y.put('version',stockver);y.put('uom_version',ver);y.put('signature',signature);b.append(y);

  end loop;

  v.put('document',doc);v.put('warehouse',ware);v.put('counts',b);RRL_STOCK_SHORT_RECOVERY.plan_inventory(p_request,r,f,v);p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;

 end;

 procedure execute_count(p_request clob,p_actor varchar2,p_result out clob) is

  d json_object_t:=json_object_t.parse(p_request);v json_object_t;x json_object_t;sourcex json_object_t;fact json_object_t;result json_object_t:=json_object_t();

  a json_array_t;original json_array_t;facts json_array_t:=json_array_t();plan clob;doc number;ware number;cond number;

  p number;h number;stockver number;qty number;delta number;ver number;basever number;eventid number;marking number;signature varchar2(64);base varchar2(20);units clob;found clob;lost clob;n_lost number;n_found number;revision_row number;row_doc number;row_cell varchar2(60);row_article varchar2(160);other_lots number;v_uid varchar2(200);

 begin

  RRL_INVENTORY_TASK_ACCESS.assert_count(p_request,p_actor);

  if trim(d.get_object('metadata').get_string('reason')) is null then raise_application_error(-20883,'INVENTORY_REASON_REQUIRED');end if;

  declare

 v_json_sql_3_1 varchar2(32767):=d.get_string('operation_id');

begin

select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_3_1;

end;v:=json_object_t.parse(plan).get_object('domain');

  doc:=v.get_number('document');select WARE_ID,CONDITION into ware,cond from RRL_REVIZION where ID=doc for update;

  RRL_INVENTORY_TASK_ACCESS.assert_count(p_request,p_actor);
  if ware!=v.get_number('warehouse') or cond is null or cond in(2,3) then raise_application_error(-20886,'INVENTORY_DOCUMENT_NOT_OPEN');end if;

  a:=v.get_array('counts');original:=d.get_object('metadata').get_array('counts');

  if d.get_object('metadata').has('revision_row_id') then

   revision_row:=d.get_object('metadata').get_number('revision_row_id');x:=treat(a.get(0) as json_object_t);

   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_REVISION_ROW',RRL_STOCK_PLAN_HELPER.decimal_text(revision_row)));

   select REVISION_ID,CELL,ARTICUL1 into row_doc,row_cell,row_article from RRL_REVISION_ROW where ID=revision_row for update;

   if row_doc is null or row_doc!=doc or row_cell is null or row_cell!=x.get_string('cell')

    or row_article is null or row_article!=x.get_string('article') then raise_application_error(-20890,'CLOSURE_CHANGED: revision row');end if;

   v_uid:=x.get_string('uid');

   select count(*) into other_lots from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA

    where s.CELL=row_cell and p.ARTICUL=row_article and s.REMAIN>0 and s.UID_POLETA!=v_uid;

   if other_lots>0 then raise_application_error(-20887,'LOT_SELECTION_REQUIRED: inventory-count.html');end if;

  end if;

  for i in 0..a.get_size-1 loop

   x:=treat(a.get(i) as json_object_t);sourcex:=treat(original.get(i) as json_object_t);

   RRL_STOCK_LOCATION_CORE.assert_quarantine(x.get_string('cell'),ware);

   begin declare

 v_json_sql_4_1 varchar2(32767):=x.get_string('uid');

 v_json_sql_4_2 varchar2(32767):=x.get_string('cell');

begin

select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION into p,h,stockver from RRL_REMAINS where UID_POLETA=v_json_sql_4_1 and CELL=v_json_sql_4_2;

end;

   exception when no_data_found then p:=0;h:=0;stockver:=0;end;

   if stockver!=x.get_number('version') or RRL_STOCK_PLAN_HELPER.decimal_text(p)!=x.get_string('p') or RRL_STOCK_PLAN_HELPER.decimal_text(h)!=x.get_string('h') then raise_application_error(-20890,'CLOSURE_CHANGED: inventory stock');end if;

   RRL_STOCK_PALLET_UOM.resolve_quantity(x.get_string('uid'),sourcex.get_string('unit'),

    case when regexp_like(sourcex.get_string('quantity'),'^0([.]0{1,9})?$') then '1' else sourcex.get_string('quantity') end,base,qty,ver,signature);

   if regexp_like(sourcex.get_string('quantity'),'^0([.]0{1,9})?$') then qty:=0;end if;

   if signature!=x.get_string('signature') or base!=x.get_string('base') then raise_application_error(-20890,'CLOSURE_CHANGED: inventory UOM');end if;

   if qty<h then raise_application_error(-20869,'INVENTORY_COUNT_BELOW_HARD: explicitly release conflicting reservations first');end if;

   declare

 v_json_sql_5_1 varchar2(32767):=x.get_string('article');

begin

select max(POLICY_VERSION) into basever from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_json_sql_5_1 and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1;

end;

   if basever is null then raise_application_error(-20868,'INVENTORY_BASE_POLICY_REQUIRED');end if;

   delta:=qty-p;eventid:=null;units:=null;found:=null;lost:=null;n_lost:=0;n_found:=0;
   if sourcex.has('found_unit_keys') and sourcex.get_array('found_unit_keys').get_size>0 then found:=sourcex.get_array('found_unit_keys').to_clob;end if;

   if sourcex.has('unit_keys') and sourcex.get_array('unit_keys').get_size>0 then units:=sourcex.get_array('unit_keys').to_clob;end if;

   if delta>0 then

    declare

 v_json_sql_6_1 varchar2(32767):=x.get_string('article');

 v_json_sql_6_2 varchar2(32767):=x.get_string('article');

 v_json_sql_6_3 varchar2(32767):=x.get_string('article');

begin

select greatest(nvl((select MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=v_json_sql_6_1),0),

      nvl((select CRPT_REQUIRED from RRL_FINISHED_GOODS_SKU where ARTICUL=v_json_sql_6_2),0),

      case when exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_json_sql_6_3) then 1 else 0 end) into marking from dual;

end;

    -- C-0166: a marked increase is allowed only as the restoration of the same units lost by an earlier inventory count.
    if marking!=0 and found is null then raise_application_error(-20884,'MARKED_INVENTORY_INCREASE_REQUIRES_CAPTURED_UNITS');end if;
    if found is not null then
     if units is not null then raise_application_error(-20884,'INVENTORY_FOUND_AND_LOST_SEPARATELY');end if;
     -- Current owner operate right for every found unit, also when the lot remain is 0 (the trade guard walks only live units).
     -- Fail closed: a found unit without trade attributes or in another warehouse is not restored.
     declare v_cw number;v_cell4 varchar2(60):=x.get_string('cell');begin
      select WARE_ID into v_cw from RRL_CELLS where CELL=v_cell4;
      if v_cw!=ware then raise_application_error(-20887,'INVENTORY_FOUND_WAREHOUSE_CONFLICT');end if;
      for o in(select j.K,a.OWNER_ID from json_table(found,'$[*]'columns(K varchar2(64)path '$'))j
        left join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=j.K)loop
       if o.OWNER_ID is null then raise_application_error(-20882,'INVENTORY_FOUND_OWNER_REQUIRED');end if;
       RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,o.OWNER_ID,1);
      end loop;end;
     RRL_STOCK_UNIT_CORE.restore_inventory_loss(x.get_string('uid'),x.get_string('cell'),delta,found);
     declare v_op varchar2(100):=d.get_string('operation_id');v_uid2 varchar2(200):=x.get_string('uid');v_cell2 varchar2(60):=x.get_string('cell');begin
      insert into RRL_INVENTORY_FOUND_UNIT(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID,FOUND_OPERATION_ID,REVISION_ID,UID_PALLET,CELL,ACTOR)
       select l.PHYSICAL_UNIT_KEY,max(l.LOSS_OPERATION_ID)keep(dense_rank last order by l.CREATED_AT),v_op,doc,v_uid2,v_cell2,p_actor
        from RRL_INVENTORY_LOSS_UNIT l join json_table(found,'$[*]'columns(K varchar2(64)path '$'))j on j.K=l.PHYSICAL_UNIT_KEY
        where l.UID_PALLET=v_uid2 and l.CELL=v_cell2 and not exists(select 1 from RRL_INVENTORY_FOUND_UNIT f
         where f.PHYSICAL_UNIT_KEY=l.PHYSICAL_UNIT_KEY and f.LOSS_OPERATION_ID=l.LOSS_OPERATION_ID)group by l.PHYSICAL_UNIT_KEY;
      n_found:=sql%rowcount;end;
    end if;

    RRL_STOCK_BALANCE_CORE.apply_delta(x.get_string('uid'),x.get_string('cell'),delta,0,base,basever,stockver);

    RRL_STOCK_BALANCE_CORE.write_leg(x.get_string('uid'),null,x.get_string('cell'),delta,base,basever,i+1,1,1,p_actor,eventid);

   elsif delta<0 then

    if found is not null then raise_application_error(-20884,'INVENTORY_FOUND_AND_LOST_SEPARATELY');end if;
    -- C-0166: the exact units written off are journaled as an inventory loss (not a shipment), with their version after the write-off.
    declare v_uid3 varchar2(200):=x.get_string('uid');v_cell3 varchar2(60):=x.get_string('cell');begin
     select json_arrayagg(PHYSICAL_UNIT_KEY returning clob)into lost from RRL_WMS_RECEIPT_UNIT u where CURRENT_UID=v_uid3 and CURRENT_CELL=v_cell3
      and STOCK_STATUS!='ISSUED'and(units is null or exists(select 1 from json_table(units,'$[*]'columns(K varchar2(64)path '$'))j where j.K=u.PHYSICAL_UNIT_KEY));end;
    RRL_STOCK_UNIT_CORE.issue_free_units(x.get_string('uid'),x.get_string('cell'),-delta,units);
    if lost is not null then declare v_op varchar2(100):=d.get_string('operation_id');v_uid3 varchar2(200):=x.get_string('uid');v_cell3 varchar2(60):=x.get_string('cell');v_open number;begin
     -- One open loss per unit: lost, found, then lost again is a new occurrence only after the previous one was recovered.
     select count(*)into v_open from RRL_INVENTORY_LOSS_UNIT l join json_table(lost,'$[*]'columns(K varchar2(64)path '$'))j on j.K=l.PHYSICAL_UNIT_KEY
      where not exists(select 1 from RRL_INVENTORY_FOUND_UNIT f where f.PHYSICAL_UNIT_KEY=l.PHYSICAL_UNIT_KEY and f.LOSS_OPERATION_ID=l.LOSS_OPERATION_ID);
     if v_open>0 then raise_application_error(-20886,'INVENTORY_LOSS_ALREADY_OPEN');end if;
     insert into RRL_INVENTORY_LOSS_UNIT(PHYSICAL_UNIT_KEY,LOSS_OPERATION_ID,REVISION_ID,UID_PALLET,CELL,UNIT_VERSION,ACTOR)
      select u.PHYSICAL_UNIT_KEY,v_op,doc,v_uid3,v_cell3,u.UNIT_VERSION,p_actor from RRL_WMS_RECEIPT_UNIT u
       join json_table(lost,'$[*]'columns(K varchar2(64)path '$'))j on j.K=u.PHYSICAL_UNIT_KEY where u.STOCK_STATUS='ISSUED';
     n_lost:=sql%rowcount;end;end if;

    RRL_STOCK_BALANCE_CORE.apply_delta(x.get_string('uid'),x.get_string('cell'),delta,0,base,basever,stockver);

    RRL_STOCK_BALANCE_CORE.write_leg(x.get_string('uid'),x.get_string('cell'),null,delta,base,basever,i+1,1,3,p_actor,eventid);

   end if;

   fact:=json_object_t();fact.put('uid',x.get_string('uid'));fact.put('cell',x.get_string('cell'));fact.put('base_uom',base);

   fact.put('before',RRL_STOCK_PLAN_HELPER.decimal_text(p));fact.put('after',RRL_STOCK_PLAN_HELPER.decimal_text(qty));fact.put('delta',RRL_STOCK_PLAN_HELPER.decimal_text(delta));fact.put('event_id',eventid);fact.put('lost_units',n_lost);fact.put('found_units',n_found);facts.append(fact);

  end loop;

  if revision_row is not null then

   sourcex:=treat(original.get(0) as json_object_t);

   declare v_row_unit varchar2(20):=sourcex.get_string('unit');v_row_qty varchar2(30):=sourcex.get_string('quantity');v_row_op varchar2(100):=d.get_string('operation_id');begin

   update RRL_REVISION_ROW set COUNT1=qty,REV_DATE=sysdate,

    COUNT_KOR=case when v_row_unit='BOX' then to_number(v_row_qty,'999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''') else COUNT_KOR end,

    REMARK1=substr(nvl(REMARK1,'')||' POSTED:'||v_row_op,1,255)

    where ID=revision_row;end;

  end if;

  result.put('operation_id',d.get_string('operation_id'));result.put('revision_id',doc);result.put('counts',facts);RRL_STOCK_SHORT_RECOVERY.finish_inventory(p_request,p_actor,v,facts,result);p_result:=result.to_clob;

 end;

end;
/
