create or replace package RRL_STOCK_QC_WEIGHT authid definer as
 procedure calculate(p_domain clob,p_expected out number,p_tolerance out number);
end;
/
create or replace package body RRL_STOCK_QC_WEIGHT as
 procedure calculate(p_domain clob,p_expected out number,p_tolerance out number) is
  d json_object_t:=json_object_t.parse(p_domain);a json_array_t:=d.get_array('legs');l json_object_t;
  v_article varchar2(160);v_ware number:=d.get_number('warehouse');v_base_weight number;v_box_weight number;
  v_policy_uom varchar2(20);v_qty number;v_count number:=0;
 begin
  p_expected:=0;p_tolerance:=null;
  if a.get_size<1 or a.get_size>200 then raise_application_error(-20881,'QUALITY_WEIGHT_ALLOCATION_BOUND');end if;
  for i in 0..a.get_size-1 loop
   l:=treat(a.get(i) as json_object_t);v_article:=l.get_string('article');v_qty:=RRL_STOCK_MATH.quantity(l.get_string('quantity'));
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