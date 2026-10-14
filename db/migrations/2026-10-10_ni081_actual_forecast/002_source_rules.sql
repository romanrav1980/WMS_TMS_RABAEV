create or replace package RRL_FORECAST_SOURCE_RULES authid definer
 accessible by(package RRL_FORECAST_PROJECTOR)as
 procedure compile_leaves(p_tree clob,p_ware number,p_leaves out clob);
end;
/
create or replace package body RRL_FORECAST_SOURCE_RULES as
 procedure compile_leaves(p_tree clob,p_ware number,p_leaves out clob)is
  d json_object_t:=json_object_t.parse(p_tree);nodes json_array_t;n json_object_t;line json_object_t;
  result json_array_t:=json_array_t();qty number;uid varchar2(200);article varchar2(160);base varchar2(20);kind varchar2(20);case_id number;origin_ware number;node_count number:=0;
  ordered json_array_t:=json_array_t();raw_leaves clob;
  type identity_map is table of boolean index by varchar2(200);seen identity_map;
 begin
  nodes:=d.get_array('nodes');
  if nodes is null or nodes.get_size<1 or nodes.get_size>200 or nvl(d.get_number('warehouse'),-1)!=p_ware
   or nvl(d.get_number('top_place_count'),-1)!=1 then raise_application_error(-20886,'FORECAST_EXACT_NATIVE_TREE_REQUIRED');end if;
  for i in 0..nodes.get_size-1 loop
   n:=treat(nodes.get(i)as json_object_t);
   if n.get_string('kind')='STOCK'then
    uid:=n.get_string('uid');article:=n.get_string('article');base:=n.get_string('base_uom');
    if uid is null or article is null or base is null or lengthb(uid)>200 or lengthb(article)>160 or lengthb(base)>20 then raise_application_error(-20886,'FORECAST_STOCK_IDENTITY_REQUIRED');end if;
    if seen.exists(uid)then raise_application_error(-20886,'FORECAST_REPEATED_STOCK_LEAF');end if;seen(uid):=true;
    qty:=RRL_STOCK_MATH.quantity(n.get_string('quantity'));case_id:=n.get_number('case_task_id');
    kind:='FULLPAL_DISPATCH';
    if case_id is not null then
     select t.WARE_ID into origin_ware from RRL_CASE_CARRIER_LOT c join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=c.CASE_PICK_TASK_ID where c.LOT_UID=uid and c.CASE_PICK_TASK_ID=case_id;
     kind:=case when origin_ware=p_ware then 'CASE_DISPATCH'else'TRANSIT_CASE'end;
    end if;
    line:=json_object_t();line.put('uid',uid);line.put('article',article);line.put('base_uom',base);
    line.put('quantity',to_char(qty,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));line.put('work_kind',kind);line.put('case_task_id',case_id);
    result.append(line);node_count:=node_count+1;
   end if;
  end loop;
  if node_count<1 or node_count!=nvl(d.get_number('leaf_count'),-1)then raise_application_error(-20886,'FORECAST_NATIVE_LEAF_COUNT_CONFLICT');end if;
  raw_leaves:=result.to_clob;
  for row_key in(select ORDINAL from json_table(raw_leaves,'$[*]'columns(ORDINAL for ordinality,CASE_ID number path '$.case_task_id',LOT_UID varchar2(200)path '$.uid'))order by nvl(CASE_ID,0),nlssort(LOT_UID,'NLS_SORT=BINARY'))loop
   ordered.append(result.get(row_key.ORDINAL-1));
  end loop;
  p_leaves:=ordered.to_clob;
 end;
end;
/
