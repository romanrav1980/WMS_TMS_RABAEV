package body RRL_TRADE_TOPUP_READ as
 function sha(p_text varchar2)return varchar2 is
 begin return lower(rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_text,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));end;

 function trip_basis(p_ware number,p_trip varchar2,p_exclude number default null)return varchar2 is
  body clob;ver number;vehicle number;profile clob;acc varchar2(32767);
 begin
  select BODY_JSON,VERSION_NO into body,ver from RRL_TRADE_DOCUMENT where WARE_ID=p_ware and ENTITY_TYPE='TRIP'and EXTERNAL_ID=p_trip and STATUS='ACCEPTED';
  acc:='TRIP:'||ver;
  begin select ID into vehicle from RRL_TR_VEHICLE where NUM=json_value(body,'$.vehicle_id')and nvl(DELETED,0)=0;
  exception when no_data_found or too_many_rows then raise_application_error(-20911,'TRADE_TOPUP_VEHICLE_MAPPING_REQUIRED');end;
  profile:=RRL_VEHICLE_PROFILE_API.describe_profile(vehicle);
  if json_value(profile,'$.state')<>'READY'then raise_application_error(-20911,'TRADE_TOPUP_VEHICLE_PROFILE_STALE');end if;
  acc:=acc||'|V:'||vehicle||':'||json_value(profile,'$.version')||':'||json_value(profile,'$.base_hash');
  for o in(select x.ORDER_ID,max(d.VERSION_NO)VERSION_NO from json_table(body,'$.orders[*]'columns(ORDER_ID varchar2(100)path'$.order_id'))x
    left join RRL_TRADE_DOCUMENT d on d.WARE_ID=p_ware and d.ENTITY_TYPE='ORDER'and d.EXTERNAL_ID=x.ORDER_ID and d.STATUS='ACCEPTED'
    group by x.ORDER_ID order by x.ORDER_ID)loop
   acc:=acc||'|O:'||o.ORDER_ID||':'||nvl(to_char(o.VERSION_NO),'-');
  end loop;
  for p in(select PROPOSAL_ID,VERSION_NO,APPROVED_BOXES from RRL_TRADE_TOPUP_PROPOSAL where WARE_ID=p_ware and TRIP_ID=p_trip
    and STATUS in('CONFIRMED','SAP_ACCEPTED')and PROPOSAL_ID<>nvl(p_exclude,-1)order by PROPOSAL_ID)loop
   acc:=acc||'|P:'||p.PROPOSAL_ID||':'||p.VERSION_NO||':'||p.APPROVED_BOXES;
  end loop;
  return sha(acc);
 exception when no_data_found then raise_application_error(-20911,'TRADE_TOPUP_TRIP_REQUIRED');
 end;

 function loading_started(p_ware number,p_trip varchar2)return number is n number;
 begin
  select count(*)into n from RRL_TRADE_TRIP_LINK l join RRL_TT_HU_LOAD_FACT f on f.TT_ID=l.NATIVE_TASK_ID
   where l.WARE_ID=p_ware and l.TRIP_ID=p_trip and f.STATUS in('LOADED','DEPARTED');
  return least(n,1);
 end;

 function need_confirmed_boxes(p_ware number,p_need varchar2,p_exclude number default null)return number is n number;
 begin
  select nvl(sum(APPROVED_BOXES),0)into n from RRL_TRADE_TOPUP_PROPOSAL where WARE_ID=p_ware and NEED_ID=p_need
   and STATUS in('CONFIRMED','SAP_ACCEPTED')and PROPOSAL_ID<>nvl(p_exclude,-1);
  return n;
 end;

 function protected_units(p_ware number,p_sku varchar2,p_owner varchar2,p_mrc number)return number is
  total number:=0;n number:=0;x json_object_t;units_per_box number;
 begin
  select json_value(BODY_JSON,'$.units_per_box'returning number)into units_per_box from RRL_TRADE_DOCUMENT
   where WARE_ID=p_ware and ENTITY_TYPE='SKU'and EXTERNAL_ID=p_sku and STATUS='ACCEPTED';
  for l in(select d.EXTERNAL_ID,ln.LINE_ID,ln.QTY,ln.UOM,ol.CUSTOMER_ORDER_ROW_ID
    from RRL_TRADE_DOCUMENT d cross apply json_table(d.BODY_JSON,'$.lines[*]'columns(
     LINE_ID varchar2(100)path'$.line_id',SKU_ID varchar2(100)path'$.sku_id',
     OWNER_ID varchar2(100)path'$.source_owner_id',MRC number path'$.mrc',QTY number path'$.quantity',UOM varchar2(10)path'$.uom'))ln
    left join RRL_TRADE_ORDER_LINK tl on tl.WARE_ID=d.WARE_ID and tl.EXTERNAL_ID=d.EXTERNAL_ID and tl.DOCUMENT_VERSION=d.VERSION_NO
    left join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=tl.CUSTOMER_ORDER_ID and ol.EXTERNAL_LINE_ID=ln.LINE_ID
    where d.WARE_ID=p_ware and d.ENTITY_TYPE='ORDER'and d.STATUS='ACCEPTED'
     and nvl(json_value(d.BODY_JSON,'$.cancelled'),'false')<>'true'
     and nvl(json_value(d.BODY_JSON,'$.order_kind'),'OUTBOUND')<>'BUYOUT'
     and ln.SKU_ID=p_sku and ln.OWNER_ID=p_owner and ln.MRC=p_mrc
     and not exists(select 1 from RRL_TRADE_TOPUP_PROPOSAL p where p.WARE_ID=d.WARE_ID and p.SAP_ORDER_ID=d.EXTERNAL_ID
       and p.STATUS in('CONFIRMED','SAP_ACCEPTED'))
    order by d.EXTERNAL_ID,ln.LINE_ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20911,'TRADE_TOPUP_PROTECTED_DEMAND_BOUND_200');end if;
   if l.CUSTOMER_ORDER_ROW_ID is not null then
    x:=json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(l.CUSTOMER_ORDER_ROW_ID));
    if x.get_boolean('open')then total:=total+RRL_STOCK_MATH.quantity(x.get_string('quantity'));end if;
   else
    total:=total+l.QTY*case when l.UOM='BOX'then units_per_box else 1 end;
   end if;
  end loop;
  return total;
 end;

 function candidates(p_ware number,p_article varchar2,p_sku varchar2,p_owner varchar2,p_mrc number,p_min_expiry date,p_limit number,p_step number)return clob is
  out_json json_array_t:=json_array_t();item json_object_t;keys json_array_t;left_units number:=p_limit;taken number;
 begin
  if p_step is null or p_step<1 or p_step<>trunc(p_step)or mod(p_limit,p_step)<>0 then raise_application_error(-20911,'TRADE_TOPUP_WHOLE_BOXES_REQUIRED');end if;
  for s in(select u.CURRENT_UID UID_VALUE,u.CURRENT_CELL CELL,count(*)N,min(a.EXPIRY_DATE)EXPIRY
    from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    join RRL_CELLS c on c.CELL=u.CURRENT_CELL join RRL_TRADE_CELL_POLICY cp on cp.CELL=u.CURRENT_CELL
    join RRL_PALLETS pl on pl.UID_PALLET=u.CURRENT_UID
    where c.WARE_ID=p_ware and cp.ZONE_KIND in('STORAGE','PICK')and pl.ARTICUL=p_article
     and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null and u.BASE_QTY=1 and u.BASE_UOM='EA'
     and a.SKU_ID=p_sku and a.OWNER_ID=p_owner and a.MRC=p_mrc and a.MARK_STATE='VALID'and a.EXPIRY_DATE>=p_min_expiry
     and not exists(select 1 from RRL_TRADE_BUYOUT_UNIT bu where bu.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY and bu.HOLD_ACTIVE=1)
    group by u.CURRENT_UID,u.CURRENT_CELL order by min(a.EXPIRY_DATE),u.CURRENT_UID,u.CURRENT_CELL fetch first 200 rows only)loop
   exit when left_units<=0;
   -- Quarantine, rejected/pending codes, mixed pallets, buyout/owner rules: the same reason picking uses.
   if RRL_STOCK_ELIGIBILITY.reason(s.UID_VALUE,s.CELL,p_ware,0,null,null,'REPLENISH',null,p_article)is null then
    taken:=least(trunc(s.N/p_step)*p_step,left_units);keys:=json_array_t();
    for k in(select u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
      where u.CURRENT_UID=s.UID_VALUE and u.CURRENT_CELL=s.CELL and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null
       and a.SKU_ID=p_sku and a.OWNER_ID=p_owner and a.MRC=p_mrc and a.MARK_STATE='VALID'and a.EXPIRY_DATE>=p_min_expiry
       and not exists(select 1 from RRL_TRADE_BUYOUT_UNIT bu where bu.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY and bu.HOLD_ACTIVE=1)
      order by a.EXPIRY_DATE,u.PHYSICAL_UNIT_KEY fetch first taken rows only)loop keys.append(k.PHYSICAL_UNIT_KEY);end loop;
    if taken>0 then
     item:=json_object_t();item.put('uid',s.UID_VALUE);item.put('cell',s.CELL);item.put('units',keys);out_json.append(item);
     left_units:=left_units-keys.get_size;
    end if;
   end if;
  end loop;
  return out_json.to_clob;
 end;

 function eligible_units(p_ware number,p_article varchar2,p_sku varchar2,p_owner varchar2,p_mrc number,p_min_expiry date,p_step number)return number is total number:=0;
 begin
  for s in(select u.CURRENT_UID UID_VALUE,u.CURRENT_CELL CELL,count(*)N
    from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY
    join RRL_CELLS c on c.CELL=u.CURRENT_CELL join RRL_TRADE_CELL_POLICY cp on cp.CELL=u.CURRENT_CELL
    join RRL_PALLETS pl on pl.UID_PALLET=u.CURRENT_UID
    where c.WARE_ID=p_ware and cp.ZONE_KIND in('STORAGE','PICK')and pl.ARTICUL=p_article
     and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null and u.BASE_QTY=1 and u.BASE_UOM='EA'
     and a.SKU_ID=p_sku and a.OWNER_ID=p_owner and a.MRC=p_mrc and a.MARK_STATE='VALID'and a.EXPIRY_DATE>=p_min_expiry
     and not exists(select 1 from RRL_TRADE_BUYOUT_UNIT bu where bu.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY and bu.HOLD_ACTIVE=1)
    group by u.CURRENT_UID,u.CURRENT_CELL order by min(a.EXPIRY_DATE),u.CURRENT_UID,u.CURRENT_CELL fetch first 200 rows only)loop
   if RRL_STOCK_ELIGIBILITY.reason(s.UID_VALUE,s.CELL,p_ware,0,null,null,'REPLENISH',null,p_article)is null then total:=total+trunc(s.N/p_step)*p_step;end if;
  end loop;
  return total;
 end;

 function card(p_id number)return clob is p RRL_TRADE_TOPUP_PROPOSAL%rowtype;j json_object_t:=json_object_t();holds json_array_t:=json_array_t();h json_object_t;n number;
 begin
  select*into p from RRL_TRADE_TOPUP_PROPOSAL where PROPOSAL_ID=p_id;
  j.put('proposal_id',p.PROPOSAL_ID);j.put('warehouse_id',p.WARE_ID);j.put('trip_id',p.TRIP_ID);j.put('trip_version',p.TRIP_VERSION);
  j.put('need_id',p.NEED_ID);j.put('need_version',p.NEED_VERSION);j.put('priority',p.PRIORITY);j.put('recipient_id',p.RECIPIENT_ID);j.put('sku_id',p.SKU_ID);
  j.put('source_owner_id',p.SOURCE_OWNER_ID);j.put('target_owner_id',p.TARGET_OWNER_ID);j.put('mrc',RRL_STOCK_PLAN_HELPER.decimal_text(p.MRC));
  j.put('min_expiry_date',to_char(p.MIN_EXPIRY,'YYYY-MM-DD'));j.put('units_per_box',p.UNITS_PER_BOX);
  j.put('need_boxes',RRL_STOCK_PLAN_HELPER.decimal_text(p.NEED_BOXES));j.put('proposed_boxes',p.PROPOSED_BOXES);j.put('approved_boxes',p.APPROVED_BOXES);
  j.put('status',p.STATUS);j.put('version',p.VERSION_NO);j.put('need_snapshot_at',to_char(p.NEED_SNAPSHOT_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"'));
  j.put('max_age_minutes',p.MAX_AGE_MINUTES);j.put('calculation_signature',p.CALC_SIGNATURE);j.put('calculation',json_object_t.parse(p.CALC_JSON));
  j.put('sap_order_id',p.SAP_ORDER_ID);j.put('sap_reason',p.SAP_REASON);j.put('request_outbox_id',p.REQUEST_OUTBOX_ID);
  select count(*)into n from RRL_TRADE_DOCUMENT where WARE_ID=p.WARE_ID and ENTITY_TYPE='ORDER'and EXTERNAL_ID=p.SAP_ORDER_ID and STATUS='ACCEPTED';
  j.put('sap_order_received',n=1);
  for x in(select RESERVATION_ID,UID_PALLET,CELL,BASE_QTY,STATUS from RRL_TRADE_TOPUP_HOLD where PROPOSAL_ID=p_id order by RESERVATION_ID)loop
   h:=json_object_t();h.put('reservation_id',x.RESERVATION_ID);h.put('pallet_identifier',x.UID_PALLET);h.put('cell',x.CELL);
   h.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(x.BASE_QTY));h.put('status',x.STATUS);holds.append(h);
  end loop;
  j.put('holds',holds);j.put('created_by',p.CREATED_BY);j.put('updated_by',p.UPDATED_BY);
  j.put('updated_at',to_char(p.UPDATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS"Z"'));
  -- Proposal and confirmation never mean the external order exists or that picking may start.
  j.put('picking_allowed',false);j.put('approval_available',false);
  return j.to_clob;
 end;
end;