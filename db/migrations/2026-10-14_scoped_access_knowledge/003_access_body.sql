create or replace package body RRL_ACCESS_API as
 procedure fail(p_code varchar2) is begin raise_application_error(-20851,p_code);end;
 function is_admin(p_actor nvarchar2) return number is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and upper(trim(USER_GROUP))='GLOBAL_ADMIN';return least(n,1);end;
 function alive(p_actor nvarchar2) return number is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0;return least(n,1);end;
 function object_inside(p_scope_kind varchar2,p_scope_id varchar2,p_kind varchar2,p_id varchar2) return number is n number;begin
  if p_scope_kind=p_kind and p_scope_id=p_id then
   select count(*)into n from RRL_ACCESS_OBJECT where KIND=p_kind and OBJECT_ID=p_id and ACTIVE=1;return least(n,1);
  end if;
  select count(*)into n from(
   select KIND,OBJECT_ID from RRL_ACCESS_OBJECT where ACTIVE=1
    start with KIND=p_kind and OBJECT_ID=p_id and ACTIVE=1
    connect by nocycle prior PARENT_KIND=KIND and prior PARENT_ID=OBJECT_ID and ACTIVE=1
  )where KIND=p_scope_kind and OBJECT_ID=p_scope_id;return least(n,1);
 end;
 function covered(p_scope_kind varchar2,p_scope_id varchar2,p_mode varchar2,p_snapshot number,p_kind varchar2,p_id varchar2,p_actor nvarchar2,p_owner nvarchar2) return number is n number;begin
  if p_scope_kind='PLATFORM' then if p_kind='PLATFORM' then return 1;else return 0;end if;end if;
  if p_kind='PLATFORM' then return 0;end if;
  if p_scope_kind='NETWORK' then return 1;end if;
  if p_scope_kind='SELF' then if p_actor=p_owner then return 1;else return 0;end if;end if;
  if p_scope_kind='GROUP' then
   for r in(select m.KIND,m.OBJECT_ID from RRL_ACCESS_GROUP g join RRL_ACCESS_GROUP_MEMBER m on m.GROUP_ID=g.GROUP_ID
     and m.VERSION_NO=case when p_mode='SNAPSHOT' then p_snapshot else g.VERSION_NO end
     where g.GROUP_ID=p_scope_id and g.ACTIVE=1)loop
    if object_inside(r.KIND,r.OBJECT_ID,p_kind,p_id)=1 then return 1;end if;
   end loop;return 0;
  end if;
  if p_scope_kind='ORG_BRANCH' then
   if p_mode='SNAPSHOT' then
    select count(*)into n from RRL_ACCESS_BRANCH_MEMBER b join RRL_ACCESS_OBJECT o on o.KIND=b.KIND and o.OBJECT_ID=b.OBJECT_ID and o.ACTIVE=1
     where b.BRANCH_KEY=p_scope_id and b.SNAPSHOT_VERSION=p_snapshot and b.KIND=p_kind and b.OBJECT_ID=p_id;
    return least(n,1);
   end if;
   return object_inside(substr(p_scope_id,1,instr(p_scope_id,':')-1),substr(p_scope_id,instr(p_scope_id,':')+1),p_kind,p_id);
  end if;
  return object_inside(p_scope_kind,p_scope_id,p_kind,p_id);
 end;
 function allowed(p_actor nvarchar2,p_permission varchar2,p_kind varchar2,p_id varchar2,p_owner nvarchar2 default null) return number is n number;begin
  if alive(p_actor)=0 then return 0;end if;
  if is_admin(p_actor)=1 then return 1;end if;
  if RRL_HAS_WRIGHT(p_actor,lower(p_permission))=1 then
   if p_kind='PLATFORM' then return 1;end if;
   if p_kind='WAREHOUSE' then select count(*)into n from RUSERS where ID=p_actor and to_char(WARE_ID)=p_id;
    if n=1 then return 1;end if;
   end if;
  end if;
  for r in(select a.* from RRL_ACCESS_ASSIGNMENT a join RRL_ACCESS_ROLE ro on ro.ROLE_ID=a.ROLE_ID and ro.ACTIVE=1
   join RRL_ACCESS_ROLE_RIGHT rr on rr.ROLE_ID=a.ROLE_ID and rr.PERMISSION=lower(p_permission)
   where a.USERNAME=p_actor and a.REVOKED_AT is null and a.VALID_FROM<=systimestamp and(a.VALID_UNTIL is null or a.VALID_UNTIL>systimestamp))loop
   if covered(r.SCOPE_KIND,r.SCOPE_ID,r.MEMBERSHIP,r.SNAPSHOT_VERSION,p_kind,p_id,p_actor,p_owner)=1 then return 1;end if;
  end loop;return 0;
 end;
 function exists_user_warehouse(p_actor nvarchar2,p_id varchar2)return number is n number;begin
  select count(*)into n from RUSERS where ID=p_actor and to_char(WARE_ID)=p_id and nvl(DELETED,0)=0;return least(n,1);
 end;
 function explanation(p_actor nvarchar2,p_permission varchar2,p_kind varchar2,p_id varchar2) return clob is
  j json_object_t;reason json_object_t;reasons json_array_t;decision number;v_revision number;
 begin
  j:=json_object_t();reasons:=json_array_t();decision:=allowed(p_actor,p_permission,p_kind,p_id);select REVISION into v_revision from RRL_ACCESS_REV where ID=1;
  if is_admin(p_actor)=1 then reason:=json_object_t();reason.put('source','GLOBAL_ADMIN');reasons.append(reason);
  else
   if RRL_HAS_WRIGHT(p_actor,lower(p_permission))=1 and(p_kind='PLATFORM' or(p_kind='WAREHOUSE' and exists_user_warehouse(p_actor,p_id)=1))then
    reason:=json_object_t();reason.put('source','LEGACY_GROUP');reason.put('scope_kind',p_kind);reason.put('scope_id',p_id);reasons.append(reason);
   end if;
   for r in(select a.* from RRL_ACCESS_ASSIGNMENT a join RRL_ACCESS_ROLE ro on ro.ROLE_ID=a.ROLE_ID and ro.ACTIVE=1
    join RRL_ACCESS_ROLE_RIGHT rr on rr.ROLE_ID=a.ROLE_ID and rr.PERMISSION=lower(p_permission)
    where a.USERNAME=p_actor and a.REVOKED_AT is null and a.VALID_FROM<=systimestamp and(a.VALID_UNTIL is null or a.VALID_UNTIL>systimestamp))loop
    if covered(r.SCOPE_KIND,r.SCOPE_ID,r.MEMBERSHIP,r.SNAPSHOT_VERSION,p_kind,p_id,p_actor,null)=1 then
     reason:=json_object_t();reason.put('source','ASSIGNMENT');reason.put('assignment_id',r.ASSIGNMENT_ID);reason.put('role_id',r.ROLE_ID);
     reason.put('scope_kind',r.SCOPE_KIND);reason.put('scope_id',r.SCOPE_ID);reason.put('membership',r.MEMBERSHIP);reason.put('snapshot_version',r.SNAPSHOT_VERSION);reasons.append(reason);
    end if;
   end loop;
  end if;
  j.put('allowed',decision=1);j.put('reasons',reasons);j.put('access_revision',v_revision);return j.to_clob;
 end;
 procedure assert_allowed(p_actor nvarchar2,p_permission varchar2,p_kind varchar2,p_id varchar2,p_owner nvarchar2 default null)is begin
  lock table RRL_ACCESS_REV in share mode wait 5;
  if allowed(p_actor,p_permission,p_kind,p_id,p_owner)=0 then fail('ACCESS_DENIED');end if;
 end;
 procedure assert_independent(p_actor nvarchar2,p_author nvarchar2,p_process varchar2)is begin
  if p_author is null then fail('DECISION_AUTHOR_REQUIRED');end if;
  if lower(trim(p_actor))=lower(trim(p_author))then fail('INDEPENDENT_DECISION_REQUIRED');end if;
 end;
 procedure execute_command(p_actor nvarchar2,p_operation varchar2,p_hash varchar2,p_json clob,p_result out clob)is
  j json_object_t; b json_object_t; arr json_array_t; item json_object_t; old_hash varchar2(64);old_actor nvarchar2(50);stored clob;
  cmd varchar2(30);v_id varchar2(100);v_v number;v_expected number;n number;active_flag number;v_kind varchar2(20);v_mode_name varchar2(10);v_snap number;
  v_parent_kind varchar2(20);v_parent_id varchar2(100);begin_at timestamp with time zone;end_at timestamp with time zone;
  f_role_id varchar2(2000);f_title varchar2(2000);f_object_id varchar2(2000);f_parent_kind varchar2(2000);f_parent_id varchar2(2000);f_group_id varchar2(2000);f_member_kind varchar2(2000);f_assignment_id varchar2(2000);f_username varchar2(2000);f_scope_kind varchar2(2000);f_scope_id varchar2(2000);f_membership varchar2(2000);f_valid_from varchar2(2000);f_valid_until varchar2(2000);f_reason varchar2(2000);
  v_old_active number;member_id varchar2(100);permission_name varchar2(80);scope_revision number;branch_kind varchar2(20);branch_id varchar2(100);
  procedure check_version is begin if v_v!=v_expected then fail('VERSION_CONFLICT');end if;end;
  procedure admin_only is begin if is_admin(p_actor)=0 then fail('GLOBAL_ADMIN_REQUIRED');end if;end;
  procedure grant_permission(p_permission varchar2,p_kind varchar2,p_id varchar2) is
   found_grant boolean:=false;needed_from timestamp with time zone;
  begin
   if is_admin(p_actor)=1 then return;end if;
   if p_kind in('SELF','ORG_BRANCH')then fail('GLOBAL_ADMIN_REQUIRED');end if;
   needed_from:=coalesce(begin_at,systimestamp);
   for a in(select aa.* from RRL_ACCESS_ASSIGNMENT aa join RRL_ACCESS_ROLE ro on ro.ROLE_ID=aa.ROLE_ID and ro.ACTIVE=1
    join RRL_ACCESS_ROLE_RIGHT rr on rr.ROLE_ID=aa.ROLE_ID and rr.PERMISSION=p_permission
    where aa.USERNAME=p_actor and aa.REVOKED_AT is null and aa.VALID_FROM<=needed_from
     and(aa.VALID_UNTIL is null or(end_at is not null and aa.VALID_UNTIL>=end_at)))loop
    if covered(a.SCOPE_KIND,a.SCOPE_ID,a.MEMBERSHIP,a.SNAPSHOT_VERSION,p_kind,p_id,p_actor,null)=1 then found_grant:=true;exit;end if;
   end loop;
   if not found_grant then fail('DELEGATION_OUTSIDE_MANDATE');end if;
  end;
  procedure grant_check(p_role varchar2,p_kind varchar2,p_id varchar2) is begin
   for x in(select PERMISSION from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=p_role)loop
    grant_permission(x.PERMISSION,p_kind,p_id);
   end loop;
  end;

 begin
  if alive(p_actor)=0 then fail('ACCESS_DENIED');end if;
  lock table RRL_ACCESS_REV in exclusive mode wait 5;
  begin select ACTOR,PAYLOAD_HASH,RESULT_JSON into old_actor,old_hash,stored from RRL_PLATFORM_COMMAND where DOMAIN='ACCESS' and OPERATION_ID=p_operation;
   if old_actor!=p_actor or old_hash!=p_hash then fail('OPERATION_CONFLICT');end if;
   j:=json_object_t.parse(stored);j.put('replayed',true);p_result:=j.to_clob;return;
  exception when no_data_found then null;end;
  j:=json_object_t.parse(p_json);cmd:=j.get_string('command_type');b:=j.get_object('payload');v_expected:=b.get_number('expected_version');
  f_role_id:=b.get_string('role_id');
  f_title:=b.get_string('title');
  f_object_id:=b.get_string('object_id');
  f_parent_kind:=b.get_string('parent_kind');
  f_parent_id:=b.get_string('parent_id');
  f_group_id:=b.get_string('group_id');
  f_member_kind:=b.get_string('member_kind');
  f_assignment_id:=b.get_string('assignment_id');
  f_username:=b.get_string('username');
  f_scope_kind:=b.get_string('scope_kind');
  f_scope_id:=b.get_string('scope_id');
  f_membership:=b.get_string('membership');
  f_valid_from:=b.get_string('valid_from');
  f_valid_until:=b.get_string('valid_until');
  f_reason:=b.get_string('reason');
  if v_expected is null or v_expected<0 then fail('VERSION_REQUIRED');end if;
  if cmd='ROLE_SAVE' then
   assert_allowed(p_actor,'access_role_manage','PLATFORM',null);v_id:=f_role_id;begin select VERSION_NO into v_v from RRL_ACCESS_ROLE where ROLE_ID=v_id;exception when no_data_found then v_v:=0;end;check_version;
   active_flag:=case when b.get_boolean('active')then 1 else 0 end;
   arr:=b.get_array('permissions');if arr.get_size>200 then fail('ROLE_RIGHTS_LIMIT');end if;
   if is_admin(p_actor)=0 then
    n:=0;
    for a in(select SCOPE_KIND,SCOPE_ID,MEMBERSHIP,SNAPSHOT_VERSION,VALID_FROM,VALID_UNTIL from RRL_ACCESS_ASSIGNMENT
     where ROLE_ID=v_id and REVOKED_AT is null and(VALID_UNTIL is null or VALID_UNTIL>systimestamp))loop
     n:=n+1;if n>200 then fail('ROLE_IMPACT_BOUND_200');end if;
     begin_at:=greatest(a.VALID_FROM,systimestamp);end_at:=a.VALID_UNTIL;
     for i in 0..arr.get_size-1 loop permission_name:=lower(arr.get_string(i));
      if a.SCOPE_KIND='GROUP' then
       for member in(select m.KIND,m.OBJECT_ID from RRL_ACCESS_GROUP g join RRL_ACCESS_GROUP_MEMBER m on m.GROUP_ID=g.GROUP_ID
        and m.VERSION_NO=case when a.MEMBERSHIP='SNAPSHOT' then a.SNAPSHOT_VERSION else g.VERSION_NO end where g.GROUP_ID=a.SCOPE_ID and g.ACTIVE=1)loop
        grant_permission(permission_name,member.KIND,member.OBJECT_ID);
       end loop;
      else grant_permission(permission_name,a.SCOPE_KIND,a.SCOPE_ID);end if;
     end loop;
    end loop;
   end if;
   merge into RRL_ACCESS_ROLE d using(select v_id ROLE_ID from dual)s on(d.ROLE_ID=s.ROLE_ID)
   when matched then update set TITLE=f_title,ACTIVE=active_flag,VERSION_NO=v_v+1
   when not matched then insert(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(v_id,f_title,active_flag,1);
   delete from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=v_id;arr:=b.get_array('permissions');
   if arr.get_size>200 then fail('ROLE_RIGHTS_LIMIT');end if;
   for i in 0..arr.get_size-1 loop permission_name:=lower(arr.get_string(i));insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(v_id,permission_name);end loop;
  elsif cmd='OBJECT_SAVE' then
   admin_only;v_id:=f_object_id;v_kind:=b.get_string('kind');v_parent_kind:=f_parent_kind;v_parent_id:=f_parent_id;
   begin select VERSION_NO into v_v from RRL_ACCESS_OBJECT where KIND=v_kind and OBJECT_ID=v_id;exception when no_data_found then v_v:=0;end;check_version;
   if v_parent_kind is not null then
    if object_inside(v_kind,v_id,v_parent_kind,v_parent_id)=1 or(v_kind=v_parent_kind and v_id=v_parent_id)then fail('OBJECT_CYCLE');end if;
   end if;
   active_flag:=case when b.get_boolean('active')then 1 else 0 end;
   merge into RRL_ACCESS_OBJECT d using(select v_kind KIND,v_id OBJECT_ID from dual)s on(d.KIND=s.KIND and d.OBJECT_ID=s.OBJECT_ID)
   when matched then update set TITLE=f_title,PARENT_KIND=v_parent_kind,PARENT_ID=v_parent_id,ACTIVE=active_flag,VERSION_NO=v_v+1
   when not matched then insert(KIND,OBJECT_ID,TITLE,PARENT_KIND,PARENT_ID,ACTIVE,VERSION_NO)values(v_kind,v_id,f_title,v_parent_kind,v_parent_id,active_flag,1);
  elsif cmd='GROUP_SAVE' then
   assert_allowed(p_actor,'access_group_manage','PLATFORM',null);v_id:=f_group_id;v_kind:=f_member_kind;
   begin select VERSION_NO,ACTIVE into v_v,v_old_active from RRL_ACCESS_GROUP where GROUP_ID=v_id;exception when no_data_found then v_v:=0;v_old_active:=0;end;check_version;
   arr:=b.get_array('members');if arr.get_size>200 then fail('GROUP_MEMBER_LIMIT');end if;
   for i in 0..arr.get_size-1 loop item:=treat(arr.get(i)as json_object_t);member_id:=item.get_string('object_id');
    if item.get_string('kind')!=v_kind then fail('GROUP_KIND_MISMATCH');end if;
    select count(*)into n from RRL_ACCESS_OBJECT where KIND=v_kind and OBJECT_ID=member_id and ACTIVE=1;
    if n=0 then fail('OBJECT_NOT_FOUND');end if;
    if is_admin(p_actor)=0 then
     for a in(select ROLE_ID,VALID_FROM,VALID_UNTIL from RRL_ACCESS_ASSIGNMENT where SCOPE_KIND='GROUP' and SCOPE_ID=v_id and MEMBERSHIP='CURRENT' and REVOKED_AT is null and(VALID_UNTIL is null or VALID_UNTIL>systimestamp))loop
      begin_at:=greatest(a.VALID_FROM,systimestamp);end_at:=a.VALID_UNTIL;grant_check(a.ROLE_ID,v_kind,item.get_string('object_id'));
     end loop;
    end if;
   end loop;
   active_flag:=case when b.get_boolean('active')then 1 else 0 end;
   if active_flag=1 and v_old_active=0 and is_admin(p_actor)=0 then
    for a in(select ROLE_ID,SNAPSHOT_VERSION,VALID_FROM,VALID_UNTIL from RRL_ACCESS_ASSIGNMENT
      where SCOPE_KIND='GROUP' and SCOPE_ID=v_id and MEMBERSHIP='SNAPSHOT' and REVOKED_AT is null and(VALID_UNTIL is null or VALID_UNTIL>systimestamp))loop
     begin_at:=greatest(a.VALID_FROM,systimestamp);end_at:=a.VALID_UNTIL;
     for member in(select KIND,OBJECT_ID from RRL_ACCESS_GROUP_MEMBER where GROUP_ID=v_id and VERSION_NO=a.SNAPSHOT_VERSION)loop
      grant_check(a.ROLE_ID,member.KIND,member.OBJECT_ID);
     end loop;
    end loop;
   end if;
   merge into RRL_ACCESS_GROUP d using(select v_id GROUP_ID from dual)s on(d.GROUP_ID=s.GROUP_ID)
   when matched then update set TITLE=f_title,MEMBER_KIND=v_kind,ACTIVE=active_flag,VERSION_NO=v_v+1
   when not matched then insert(GROUP_ID,TITLE,MEMBER_KIND,ACTIVE,VERSION_NO)values(v_id,f_title,v_kind,active_flag,1);
   for i in 0..arr.get_size-1 loop item:=treat(arr.get(i)as json_object_t);member_id:=item.get_string('object_id');
    insert into RRL_ACCESS_GROUP_MEMBER(GROUP_ID,VERSION_NO,KIND,OBJECT_ID)values(v_id,v_v+1,v_kind,member_id);end loop;
  elsif cmd='ASSIGN' then
   assert_allowed(p_actor,'access_assign_manage','PLATFORM',null);v_id:=f_assignment_id;v_v:=0;check_version;
   select count(*)into n from RUSERS where lower(trim(ID))=lower(trim(f_username)) and nvl(DELETED,0)=0;if n!=1 then fail('USER_NOT_FOUND');end if;
   select ID into f_username from RUSERS where lower(trim(ID))=lower(trim(f_username)) and nvl(DELETED,0)=0;
   select count(*)into n from RRL_ACCESS_ROLE where ROLE_ID=f_role_id and ACTIVE=1;if n!=1 then fail('ROLE_NOT_FOUND');end if;
   v_kind:=f_scope_kind;v_mode_name:=f_membership;v_snap:=b.get_number('snapshot_version');
   begin_at:=to_timestamp_tz(f_valid_from,'YYYY-MM-DD"T"HH24:MI:SS.FFTZH:TZM');
   if f_valid_until is not null then end_at:=to_timestamp_tz(f_valid_until,'YYYY-MM-DD"T"HH24:MI:SS.FFTZH:TZM');end if;

   if v_kind='ORG_BRANCH' then
    admin_only;branch_kind:=substr(f_scope_id,1,instr(f_scope_id,':')-1);branch_id:=substr(f_scope_id,instr(f_scope_id,':')+1);
    select count(*)into n from RRL_ACCESS_OBJECT where KIND=branch_kind and OBJECT_ID=branch_id and ACTIVE=1;
    if n!=1 then fail('BRANCH_NOT_FOUND');end if;
    if v_mode_name='SNAPSHOT' then
     select REVISION into scope_revision from RRL_ACCESS_REV where ID=1;
     if v_snap!=scope_revision or v_snap is null then fail('SNAPSHOT_REVISION_CONFLICT');end if;
     insert into RRL_ACCESS_BRANCH_MEMBER(BRANCH_KEY,SNAPSHOT_VERSION,KIND,OBJECT_ID)
      select f_scope_id,v_snap,KIND,OBJECT_ID from RRL_ACCESS_OBJECT where ACTIVE=1
       start with KIND=branch_kind and OBJECT_ID=branch_id and ACTIVE=1
       connect by nocycle prior KIND=PARENT_KIND and prior OBJECT_ID=PARENT_ID and ACTIVE=1;
    end if;
   elsif v_kind not in('GROUP','SELF','NETWORK','PLATFORM') then
    select count(*)into n from RRL_ACCESS_OBJECT where KIND=v_kind and OBJECT_ID=f_scope_id and ACTIVE=1;
    if n!=1 then fail('OBJECT_NOT_FOUND');end if;
   end if;
   if v_kind='GROUP' then
    select count(*)into n from RRL_ACCESS_GROUP where GROUP_ID=f_scope_id and ACTIVE=1;if n!=1 then fail('GROUP_NOT_FOUND');end if;
    for r in(select m.KIND,m.OBJECT_ID from RRL_ACCESS_GROUP g join RRL_ACCESS_GROUP_MEMBER m on m.GROUP_ID=g.GROUP_ID
      and m.VERSION_NO=case when v_mode_name='SNAPSHOT' then v_snap else g.VERSION_NO end where g.GROUP_ID=f_scope_id)loop
     grant_check(f_role_id,r.KIND,r.OBJECT_ID);end loop;
    if v_mode_name='SNAPSHOT' then select count(*)into n from RRL_ACCESS_GROUP_MEMBER where GROUP_ID=f_scope_id and VERSION_NO=v_snap;if n=0 then fail('SNAPSHOT_NOT_FOUND');end if;end if;
   else grant_check(f_role_id,v_kind,f_scope_id);end if;
   insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,SNAPSHOT_VERSION,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)
    values(v_id,f_username,f_role_id,v_kind,f_scope_id,v_mode_name,v_snap,begin_at,end_at,p_actor,f_reason,1);
  elsif cmd='REVOKE' then
   assert_allowed(p_actor,'access_assign_manage','PLATFORM',null);v_id:=f_assignment_id;select VERSION_NO into v_v from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=v_id;check_version;
   if is_admin(p_actor)=0 then select count(*)into n from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=v_id and ASSIGNED_BY=p_actor;
    if n=0 then fail('REVOKE_OUTSIDE_MANDATE');end if;end if;
   update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp,REASON=f_reason,VERSION_NO=v_v+1 where ASSIGNMENT_ID=v_id;
  else fail('UNKNOWN_COMMAND');end if;
  update RRL_ACCESS_REV set REVISION=REVISION+1 where ID=1;
  j:=json_object_t();j.put('operation_id',p_operation);j.put('command_type',cmd);j.put('object_id',v_id);j.put('version',v_v+1);j.put('replayed',false);p_result:=j.to_clob;
  insert into RRL_PLATFORM_COMMAND(DOMAIN,OPERATION_ID,ACTOR,PAYLOAD_HASH,RESULT_JSON)values('ACCESS',p_operation,p_actor,p_hash,p_result);
  insert into RRL_ACCESS_AUDIT(OPERATION_ID,ACTOR,COMMAND_TYPE,OBJECT_ID,PAYLOAD_JSON)values(p_operation,p_actor,cmd,v_id,p_json);
 end;
end RRL_ACCESS_API;
/
