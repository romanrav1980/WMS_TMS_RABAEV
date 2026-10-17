create or replace package body RRL_STOCK_QC_WEIGHT as
 procedure physical_mass(p_uid varchar2,p_quantity number,p_mass out number,p_lightest out number)is
  n number;bad number;qty number;
 begin
  if p_uid is null then raise_application_error(-20887,'QUALITY_WEIGHT_PHYSICAL_UID_REQUIRED');end if;
  select count(*),nvl(sum(BASE_QTY),0),nvl(sum(GROSS_WEIGHT_KG),0),min(GROSS_WEIGHT_KG),
   nvl(sum(case when BASE_QTY is null or BASE_QTY<=0 or BASE_UOM is null or BASE_UOM!='KG'
    or GROSS_WEIGHT_KG is null or GROSS_WEIGHT_KG<BASE_QTY or MEASUREMENT_REFERENCE is null or WEIGHT_LABEL_SCAN is null then 1 else 0 end),0)
   into n,qty,p_mass,p_lightest,bad from(select BASE_QTY,BASE_UOM,GROSS_WEIGHT_KG,MEASUREMENT_REFERENCE,WEIGHT_LABEL_SCAN
    from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid and STOCK_STATUS!='ISSUED'and rownum<=10001);
  if n>10000 then raise_application_error(-20881,'QUALITY_WEIGHT_PHYSICAL_UNIT_BOUND_10000');end if;
  if n=0 or bad>0 or qty!=p_quantity then raise_application_error(-20887,'QUALITY_WEIGHT_ACTUAL_BOX_MASS_COMPOSITION_REQUIRED');end if;
 end;
 procedure calculate(p_domain clob,p_expected out number,p_tolerance out number) is
  d json_object_t:=json_object_t.parse(p_domain);a json_array_t:=d.get_array('legs');l json_object_t;
  v_article varchar2(160);v_ware number:=d.get_number('warehouse');v_base_weight number;v_box_weight number;
  v_policy_uom varchar2(20);v_qty number;v_count number:=0;v_physical_mass number;v_lightest number;
 begin
  p_expected:=0;p_tolerance:=null;
  if a.get_size<1 or a.get_size>200 then raise_application_error(-20881,'QUALITY_WEIGHT_ALLOCATION_BOUND');end if;
  for i in 0..a.get_size-1 loop
   l:=treat(a.get(i) as json_object_t);v_article:=l.get_string('article');v_qty:=RRL_STOCK_MATH.quantity(l.get_string('quantity'));
   if RRL_WEIGHT_BOX_CAPACITY.enabled(v_article)=1 then
    if l.get_string('base_uom')is null or l.get_string('base_uom')!='KG'then raise_application_error(-20887,'QUALITY_WEIGHT_PHYSICAL_KG_REQUIRED');end if;
    physical_mass(l.get_string('uid'),v_qty,v_physical_mass,v_lightest);
    p_expected:=p_expected+v_physical_mass;v_count:=v_count+1;
    p_tolerance:=case when p_tolerance is null then v_lightest/2 else least(p_tolerance,v_lightest/2)end;
    continue;
   end if;
   begin
    select QC_BASE_WEIGHT_KG,QC_BOX_WEIGHT_KG,QC_WEIGHT_BASE_UOM into v_base_weight,v_box_weight,v_policy_uom from RRL_RECEIPT_SKU_RULE where WARE_ID=v_ware and ARTICUL=v_article;
   exception when no_data_found then raise_application_error(-20887,'QUALITY_SI_WEIGHT_POLICY_REQUIRED:'||v_article);end;
   if v_base_weight is null or v_base_weight<=0 or v_box_weight is null or v_box_weight<=0 then
    raise_application_error(-20887,'QUALITY_SI_WEIGHT_POLICY_REQUIRED:'||v_article);end if;
   if v_policy_uom is null or v_policy_uom!=l.get_string('base_uom') then raise_application_error(-20887,'QUALITY_MASS_BASE_UOM_CONFLICT:'||v_article);end if;
   p_expected:=p_expected+v_qty*v_base_weight;v_count:=v_count+1;
   p_tolerance:=case when p_tolerance is null then v_box_weight/2 else least(p_tolerance,v_box_weight/2) end;
  end loop;
  if v_count=0 then raise_application_error(-20887,'QUALITY_EMPTY_WEIGHT_COMPOSITION');end if;
 end;
end;
/
