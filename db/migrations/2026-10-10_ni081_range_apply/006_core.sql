create or replace package RRL_PICK_RANGE_APPLY_CORE authid definer
 accessible by(package RRL_PICK_RANGE_PROPOSAL_API)as
 procedure apply_change(p_operation varchar2,p_actor varchar2,p_action varchar2,p_ware number,p_article varchar2,
  p_request clob,p_source clob,p_result out clob);
end;
/
create or replace package body RRL_PICK_RANGE_APPLY_CORE as
 procedure current_actor(p_actor varchar2,p_ware number)is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0
   and(WARE_ID=p_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(ID,'pick_topology_edit')=1;
  if n!=1 then raise_application_error(-20882,'PICK_RANGE_CURRENT_WARE_ACTOR_REQUIRED');end if;
 end;
 procedure candidate(p_face number,p_ware number,p_weight number,p_row out RRL_PICK_FACE%rowtype)is n number;
 begin
  select *into p_row from RRL_PICK_FACE where PICK_FACE_ID=p_face and WARE_ID=p_ware for update;
  if p_row.ACTIVE!=1 or(p_row.PICK_FACE_TYPE!='DYNAMIC'and p_row.ALLOW_DYNAMIC_ASSIGNMENT!=1)
   or p_row.MAX_VOLUME is null or p_row.MAX_WEIGHT is null or p_row.MAX_WEIGHT<p_weight then
   raise_application_error(-20886,'PICK_RANGE_CURRENT_FACE_CAPACITY_REQUIRED');end if;
  select count(*)into n from RRL_CELLS c join RRL_PICK_ROUTE r on r.PICK_ROUTE_ID=p_row.PICK_ROUTE_ID
   and r.WARE_ID=c.WARE_ID and r.ACTIVE=1 and r.STATUS='PUBLISHED'
   join RRL_PICK_ROUTE_CELL rc on rc.PICK_ROUTE_CELL_ID=p_row.PICK_ROUTE_CELL_ID and rc.PICK_ROUTE_ID=r.PICK_ROUTE_ID
    and rc.WARE_ID=c.WARE_ID and rc.CELL_CODE=c.CELL and rc.ACTIVE=1
   where c.CELL=p_row.CELL_CODE and c.WARE_ID=p_ware and c.OTBOR=1 and nvl(c.IS_SYSTEM,0)=0
    and nvl(c.BLOCKED_FOR_REMAINS,0)=0 and nvl(c.BLOCKED_FOR_POPOLNENIE,0)=0;
  if n!=1 then raise_application_error(-20886,'PICK_RANGE_CURRENT_PUBLISHED_ROUTE_REQUIRED');end if;
  select (select count(*)from RRL_PICK_FACE_ARTICUL where PICK_FACE_ID=p_face and ACTIVE=1)
   +(select count(*)from RRL_PICK_FACE_ASSIGNMENT where CELL_CODE=p_row.CELL_CODE and STATUS='ACTIVE')
   +(select count(*)from RRL_REMAINS where CELL=p_row.CELL_CODE and(REMAIN>0 or HARD_RESERVED_BASE>0))
   +(select count(*)from RRL_WAREHOUSE_TASK where(TO_CELL=p_row.CELL_CODE or FROM_CELL=p_row.CELL_CODE)and STATUS not in('DONE','CANCELLED'))
   +(select count(*)from RRL_PICK_WAVE_REPLENISH_TASK where TARGET_CELL_CODE=p_row.CELL_CODE and STATUS not in('DONE','CANCELLED','FAILED'))
   +(select count(*)from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
      where l.CELL_CODE=p_row.CELL_CODE and t.STATUS not in('DONE','CANCELLED')and l.PLANNED_QTY>nvl(l.PICKED_QTY,0))
   into n from dual;
  if n!=0 then raise_application_error(-20886,'PICK_RANGE_CANDIDATE_NO_LONGER_EMPTY');end if;
 end;
 procedure clone_template(p_template RRL_PICK_FACE_ARTICUL%rowtype,p_face number,p_actor varchar2,p_mapping out number)is
 begin
  p_mapping:=RRL_PICK_TOPOLOGY_API.assign_articul(null,p_face,p_template.ARTICUL,p_template.PRIORITY,
   p_template.MIN_QTY,p_template.MAX_QTY,1,1,p_template.VALID_FROM,p_template.VALID_TO,p_actor);
  update RRL_PICK_FACE_ARTICUL set REPLENISHMENT_METHOD=p_template.REPLENISHMENT_METHOD,
   REPLENISHMENT_QTY_MODE=p_template.REPLENISHMENT_QTY_MODE,MIN_TRIGGER_BOX_QTY=p_template.MIN_TRIGGER_BOX_QTY,
   MIN_TRIGGER_LAYER_QTY=p_template.MIN_TRIGGER_LAYER_QTY,BOXES_PER_LAYER=p_template.BOXES_PER_LAYER,
   BOXES_PER_PALLET=p_template.BOXES_PER_PALLET,BOX_VOLUME_M3=p_template.BOX_VOLUME_M3,
   ALLOW_PARTIAL_PALLET=p_template.ALLOW_PARTIAL_PALLET,USE_ARTICUL_REPLENISH_RULE=p_template.USE_ARTICUL_REPLENISH_RULE,
   REPLENISHMENT_RELEASE_POLICY=p_template.REPLENISHMENT_RELEASE_POLICY,SAFETY_LAYER_QTY=p_template.SAFETY_LAYER_QTY,
   PREDICTIVE_BUFFER_MIN=p_template.PREDICTIVE_BUFFER_MIN,PICK_RATE_SOURCE=p_template.PICK_RATE_SOURCE,
   RECHECK_ON_PICK_EVENT=p_template.RECHECK_ON_PICK_EVENT where PICK_FACE_ARTICUL_ID=p_mapping;
 end;
 procedure approve(p_operation varchar2,p_actor varchar2,p_ware number,p_article varchar2,
  b json_object_t,s json_object_t,p_result out clob)is
  proposal RRL_PICK_RANGE_PROPOSAL%rowtype;t RRL_PICK_FACE_ARTICUL%rowtype;f RRL_PICK_FACE%rowtype;
  recommendation json_object_t;refs json_array_t;selected json_array_t;old_faces json_array_t;
  x json_object_t;j json_object_t:=json_object_t();new_ids json_array_t:=json_array_t();old_ids json_array_t:=json_array_t();
  identity varchar2(100);n number;mapping number;weight number;multiple number;num number;den number;boxes number;q number;v_proof clob;v_face number;v_cell varchar2(100);layout json_object_t;
 begin
  identity:=b.get_string('proposal_id');
  select *into proposal from RRL_PICK_RANGE_PROPOSAL where PROPOSAL_ID=identity for update;
  current_actor(p_actor,p_ware);
  if proposal.WARE_ID!=p_ware or proposal.ARTICLE!=p_article then raise_application_error(-20882,'PICK_RANGE_PROPOSAL_SCOPE_CONFLICT');end if;
  select(select count(*)from RRL_PICK_RANGE_CANCEL where PROPOSAL_ID=identity)
    +(select count(*)from RRL_PICK_RANGE_APPROVAL where PROPOSAL_ID=identity)into n from dual;
  if n!=0 then raise_application_error(-20886,'PICK_RANGE_PROPOSAL_NOT_CURRENT_DRAFT');end if;
  if s.get_string('source_signature')is null or s.get_string('source_signature')!=proposal.SOURCE_SIGNATURE
   or s.get_string('status')is null or s.get_string('status')!='SCENARIO_ONLY'
   or s.get_string('undated_unpicked_quantity')is null or not regexp_like(s.get_string('undated_unpicked_quantity'),'^0([.]0+)?$') then
   raise_application_error(-20886,'PICK_RANGE_COMPLETE_CURRENT_PERIOD_REQUIRED');end if;
  if b.get_boolean('geometry_checked')is null or not b.get_boolean('geometry_checked')
   or b.get_boolean('product_compatibility_checked')is null or not b.get_boolean('product_compatibility_checked')then
   raise_application_error(-20881,'PICK_RANGE_OPERATOR_LAYOUT_INSPECTION_REQUIRED');end if;
  recommendation:=s.get_object('range_recommendation');selected:=recommendation.get_array('selected_faces');
  refs:=recommendation.get_array('reference_templates');layout:=s.get_object('existing_range');old_faces:=layout.get_array('cells');
  if recommendation.get_string('status')!='NOMINAL_RECOMMENDATION'or selected.get_size not between 1 and 100
   or refs.get_size<1 or old_faces.get_size not between 1 and 100 then
   raise_application_error(-20886,'PICK_RANGE_COMPLETE_NOMINAL_SELECTION_REQUIRED');end if;
  x:=treat(refs.get(0)as json_object_t);v_face:=x.get_number('pick_face_id');
  select a.*into t from RRL_PICK_FACE_ARTICUL a join RRL_PICK_FACE pf on pf.PICK_FACE_ID=a.PICK_FACE_ID
   where a.PICK_FACE_ID=v_face and a.ARTICUL=p_article and a.ACTIVE=1 and pf.WARE_ID=p_ware;
  if t.VALID_FROM is null or trunc(t.VALID_FROM)>trunc(sysdate)or(t.VALID_TO is not null and trunc(t.VALID_TO)<trunc(sysdate))then
   raise_application_error(-20886,'PICK_RANGE_CURRENT_TEMPLATE_DATE_REQUIRED');end if;
  select PALLET_MULTIPLE into multiple from RRL_ARTICULS where ACTICUL=p_article;
  select NUMERATOR,DENOMINATOR into num,den from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM='BOX'
   and POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM='BOX');
  select coalesce(case when t.USE_ARTICUL_REPLENISH_RULE=1 then ar.BOXES_PER_PALLET end,t.BOXES_PER_PALLET)into boxes
   from dual left join RRL_ARTICUL_REPLENISH_RULE ar on ar.ARTICUL=p_article;
  if multiple is null or multiple<=0 or boxes is null or boxes<=0 or num<=0 or den<=0 or boxes*num/den!=multiple then
   raise_application_error(-20886,'PICK_RANGE_PALLET_BASE_NORM_NOT_COHERENT');end if;
  x:=treat(selected.get(0)as json_object_t);weight:=RRL_STOCK_MATH.quantity(x.get_string('declared_pallet_gross_weight_kg'));
  if weight<=0 then raise_application_error(-20881,'PICK_RANGE_GROSS_WEIGHT_REQUIRED');end if;
  for i in 0..selected.get_size-1 loop
   x:=treat(selected.get(i)as json_object_t);candidate(x.get_number('pick_face_id'),p_ware,weight,f);
  end loop;
  current_actor(p_actor,p_ware);
  v_proof:=s.to_clob;
  insert into RRL_PICK_RANGE_APPROVAL(PROPOSAL_ID,OPERATION_ID,WARE_ID,ARTICLE,PROOF_JSON)
   values(identity,p_operation,p_ware,p_article,v_proof);
  for i in 0..selected.get_size-1 loop
   x:=treat(selected.get(i)as json_object_t);
   if RRL_STOCK_MATH.quantity(x.get_string('nominal_pallet_base_quantity'))!=multiple then
    raise_application_error(-20886,'PICK_RANGE_NOMINAL_PALLET_CHANGED');end if;
   candidate(x.get_number('pick_face_id'),p_ware,weight,f);
   clone_template(t,f.PICK_FACE_ID,p_actor,mapping);
   q:=RRL_STOCK_REPL_CAPACITY.unit_volume(f.CELL_CODE,p_article)*multiple;
   if q is null or q>f.MAX_VOLUME then raise_application_error(-20886,'PICK_RANGE_VOLUME_NO_LONGER_FITS');end if;
   merge into RRL_PICK_RANGE_STATUS d using(select mapping ID from dual)v on(d.PICK_FACE_ARTICUL_ID=v.ID)
    when matched then update set MODE_CODE='ACTIVE',APPROVAL_OPERATION_ID=p_operation
    when not matched then insert(PICK_FACE_ARTICUL_ID,MODE_CODE,APPROVAL_OPERATION_ID)values(mapping,'ACTIVE',p_operation);
   insert into RRL_PICK_RANGE_MEMBER(PROPOSAL_ID,PICK_FACE_ARTICUL_ID,ROLE_CODE)values(identity,mapping,'NEW');new_ids.append(mapping);
  end loop;
  for i in 0..old_faces.get_size-1 loop
   x:=treat(old_faces.get(i)as json_object_t);v_face:=x.get_number('pick_face_id');v_cell:=x.get_string('cell');
   select a.PICK_FACE_ARTICUL_ID into mapping from RRL_PICK_FACE_ARTICUL a join RRL_PICK_FACE f on f.PICK_FACE_ID=a.PICK_FACE_ID
    where a.PICK_FACE_ID=v_face and a.ARTICUL=p_article and a.ACTIVE=1 and f.WARE_ID=p_ware for update of a.ACTIVE;
   merge into RRL_PICK_RANGE_STATUS d using(select mapping ID from dual)v on(d.PICK_FACE_ARTICUL_ID=v.ID)
    when matched then update set MODE_CODE='DRAINING',APPROVAL_OPERATION_ID=p_operation
    when not matched then insert(PICK_FACE_ARTICUL_ID,MODE_CODE,APPROVAL_OPERATION_ID)values(mapping,'DRAINING',p_operation);
   insert into RRL_PICK_RANGE_ALLOW_REPL(PICK_FACE_ARTICUL_ID,DRAIN_OPERATION_ID,REPLENISH_TASK_ID,MAX_ORIGINAL_QTY)
    select mapping,p_operation,PICK_WAVE_REPLENISH_TASK_ID,QTY from RRL_PICK_WAVE_REPLENISH_TASK
     where TARGET_CELL_CODE=v_cell and ARTICUL=p_article and STATUS not in('DONE','CANCELLED','FAILED');
   insert into RRL_PICK_RANGE_MEMBER(PROPOSAL_ID,PICK_FACE_ARTICUL_ID,ROLE_CODE)values(identity,mapping,'OLD');old_ids.append(mapping);
  end loop;
  j.put('proposal_id',identity);j.put('status','APPROVED');j.put('new_mapping_ids',new_ids);j.put('draining_mapping_ids',old_ids);
  j.put('stock_changed',false);j.put('existing_task_assignments_changed',false);j.put('range_applied',true);p_result:=j.to_clob;
 end;
 procedure close_drain(p_operation varchar2,p_actor varchar2,p_ware number,p_article varchar2,
  b json_object_t,p_result out clob)is
  a RRL_PICK_FACE_ARTICUL%rowtype;f RRL_PICK_FACE%rowtype;s RRL_PICK_RANGE_STATUS%rowtype;n number;v_mapping number;j json_object_t:=json_object_t();
 begin
  v_mapping:=b.get_number('pick_face_articul_id');
  select *into a from RRL_PICK_FACE_ARTICUL where PICK_FACE_ARTICUL_ID=v_mapping for update;
  select *into f from RRL_PICK_FACE where PICK_FACE_ID=a.PICK_FACE_ID;
  if a.ARTICUL!=p_article or f.WARE_ID!=p_ware then raise_application_error(-20882,'PICK_RANGE_DRAIN_SCOPE_CONFLICT');end if;
  select *into s from RRL_PICK_RANGE_STATUS where PICK_FACE_ARTICUL_ID=a.PICK_FACE_ARTICUL_ID for update;
  current_actor(p_actor,p_ware);
  if s.MODE_CODE!='DRAINING'then raise_application_error(-20886,'PICK_RANGE_NOT_DRAINING');end if;
  select(select count(*)from RRL_REMAINS where CELL=f.CELL_CODE and(REMAIN>0 or HARD_RESERVED_BASE>0))
   +(select count(*)from RRL_WAREHOUSE_TASK where(TO_CELL=f.CELL_CODE or FROM_CELL=f.CELL_CODE)and STATUS not in('DONE','CANCELLED'))
   +(select count(*)from RRL_PICK_WAVE_REPLENISH_TASK where TARGET_CELL_CODE=f.CELL_CODE and ARTICUL=p_article and STATUS not in('DONE','CANCELLED','FAILED'))
   +(select count(*)from RRL_CASE_PICK_LINE l join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID
      where l.CELL_CODE=f.CELL_CODE and t.STATUS not in('DONE','CANCELLED')and l.PLANNED_QTY>nvl(l.PICKED_QTY,0))
   +(select count(*)from RRL_PICK_FACE_ASSIGNMENT where CELL_CODE=f.CELL_CODE and STATUS='ACTIVE')into n from dual;
  if n!=0 then raise_application_error(-20886,'PICK_RANGE_OLD_STOCK_OR_COMMITMENT_REMAINS');end if;
  n:=RRL_PICK_TOPOLOGY_API.assign_articul(a.PICK_FACE_ARTICUL_ID,a.PICK_FACE_ID,a.ARTICUL,a.PRIORITY,a.MIN_QTY,a.MAX_QTY,
   0,0,a.VALID_FROM,a.VALID_TO,p_actor);
  update RRL_PICK_RANGE_STATUS set MODE_CODE='CLOSED'where PICK_FACE_ARTICUL_ID=a.PICK_FACE_ARTICUL_ID;
  insert into RRL_PICK_RANGE_DRAIN_CLOSE(OPERATION_ID,PICK_FACE_ARTICUL_ID,FROM_APPROVAL_OPERATION_ID)
   values(p_operation,a.PICK_FACE_ARTICUL_ID,s.APPROVAL_OPERATION_ID);
  j.put('status','DRAIN_CLOSED');j.put('pick_face_articul_id',a.PICK_FACE_ARTICUL_ID);j.put('stock_changed',false);p_result:=j.to_clob;
 end;
 procedure apply_change(p_operation varchar2,p_actor varchar2,p_action varchar2,p_ware number,p_article varchar2,
  p_request clob,p_source clob,p_result out clob)is b json_object_t:=json_object_t.parse(p_request);s json_object_t;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  if p_action='APPROVE'then s:=json_object_t.parse(p_source);approve(p_operation,p_actor,p_ware,p_article,b,s,p_result);
  elsif p_action='CLOSE_DRAIN'then close_drain(p_operation,p_actor,p_ware,p_article,b,p_result);
  else raise_application_error(-20881,'PICK_RANGE_APPLY_ACTION_REQUIRED');end if;
 end;
end;
/
