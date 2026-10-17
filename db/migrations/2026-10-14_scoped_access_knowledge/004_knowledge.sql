create or replace package RRL_KNOWLEDGE_API as
 function can_read(p_actor nvarchar2,p_payload clob) return number;
 procedure execute_command(p_actor nvarchar2,p_operation varchar2,p_hash varchar2,p_json clob,p_result out clob);
end RRL_KNOWLEDGE_API;
/
create or replace package body RRL_KNOWLEDGE_API as
 procedure fail(p_code varchar2)is begin raise_application_error(-20852,p_code);end;
 function can_read(p_actor nvarchar2,p_payload clob) return number is j json_object_t;arr json_array_t;begin
  j:=json_object_t.parse(p_payload);arr:=j.get_array('required_permissions');
  for i in 0..arr.get_size-1 loop
   if RRL_ACCESS_API.allowed(p_actor,arr.get_string(i),'PLATFORM',null)=0 then return 0;end if;
  end loop;return 1;
 end;
 procedure execute_command(p_actor nvarchar2,p_operation varchar2,p_hash varchar2,p_json clob,p_result out clob)is
  j json_object_t;b json_object_t;previous json_object_t;arr json_array_t;cmd varchar2(30);v_id varchar2(80);v_space varchar2(80);v_title nvarchar2(200);
  v_expected number;v_version number;v_pub number;v_status varchar2(15);v_actor nvarchar2(50);v_hash varchar2(64);v_body clob;old_body clob;
  v_reason nvarchar2(500);v_ref varchar2(80);n number;
 begin
  RRL_ACCESS_API.assert_allowed(p_actor,'knowledge_edit','PLATFORM',null);
  lock table RRL_KNOWLEDGE_ARTICLE in share row exclusive mode wait 5;
  begin select ACTOR,PAYLOAD_HASH,RESULT_JSON into v_actor,v_hash,v_body from RRL_PLATFORM_COMMAND where DOMAIN='KNOWLEDGE' and OPERATION_ID=p_operation;
   if v_actor!=p_actor or v_hash!=p_hash then fail('OPERATION_CONFLICT');end if;
   j:=json_object_t.parse(v_body);j.put('replayed',true);p_result:=j.to_clob;return;
  exception when no_data_found then null;end;
  j:=json_object_t.parse(p_json);cmd:=j.get_string('command_type');b:=j.get_object('payload');v_expected:=b.get_number('expected_version');
  if v_expected is null or v_expected<0 then fail('VERSION_REQUIRED');end if;
  v_id:=b.get_string('article_id');v_space:=b.get_string('space_id');v_title:=b.get_string('title');v_reason:=b.get_string('reason');
  if cmd='SPACE_SAVE' then
   RRL_ACCESS_API.assert_allowed(p_actor,'knowledge_admin','PLATFORM',null);v_id:=v_space;
   begin select VERSION_NO into v_version from RRL_KNOWLEDGE_SPACE where SPACE_ID=v_id;exception when no_data_found then v_version:=0;end;
   if v_version!=v_expected then fail('VERSION_CONFLICT');end if;
   merge into RRL_KNOWLEDGE_SPACE d using(select v_id SPACE_ID from dual)s on(d.SPACE_ID=s.SPACE_ID)
    when matched then update set TITLE=v_title,VERSION_NO=v_version+1
    when not matched then insert(SPACE_ID,TITLE,VERSION_NO)values(v_id,v_title,1);
  elsif cmd='ARTICLE_SAVE' then
   begin select CURRENT_VERSION,PUBLISHED_VERSION into v_version,v_pub from RRL_KNOWLEDGE_ARTICLE where ARTICLE_ID=v_id;
    select PAYLOAD_JSON into old_body from RRL_KNOWLEDGE_REV where ARTICLE_ID=v_id and VERSION_NO=v_version;
   exception when no_data_found then v_version:=0;end;
   if v_version!=v_expected then fail('VERSION_CONFLICT');end if;
   -- Only publishers may set/change the audience, preventing editor access expansion.
   arr:=b.get_array('required_permissions');
   if v_version=0 then
    if arr.get_size>0 then RRL_ACCESS_API.assert_allowed(p_actor,'knowledge_publish','PLATFORM',null);end if;
   else
    previous:=json_object_t.parse(old_body);
    if arr.to_string!=previous.get_array('required_permissions').to_string then RRL_ACCESS_API.assert_allowed(p_actor,'knowledge_publish','PLATFORM',null);end if;
    if can_read(p_actor,old_body)=0 then fail('ARTICLE_ACCESS_DENIED');end if;
   end if;
   if arr.get_size>30 then fail('AUDIENCE_LIMIT');end if;
   arr:=b.get_array('related');if arr.get_size>30 then fail('RELATED_LIMIT');end if;
   for i in 0..arr.get_size-1 loop v_ref:=arr.get_string(i);
    if v_ref=v_id then fail('SELF_REFERENCE');end if;
    select count(*)into n from RRL_KNOWLEDGE_ARTICLE where ARTICLE_ID=v_ref;if n=0 then fail('RELATED_NOT_FOUND');end if;
   end loop;
   v_body:=b.to_clob;v_status:='DRAFT';
   if v_version=0 then insert into RRL_KNOWLEDGE_ARTICLE(ARTICLE_ID,SPACE_ID,CURRENT_VERSION)values(v_id,v_space,1);
   else update RRL_KNOWLEDGE_ARTICLE set SPACE_ID=v_space,CURRENT_VERSION=v_version+1 where ARTICLE_ID=v_id;end if;
   insert into RRL_KNOWLEDGE_REV(ARTICLE_ID,VERSION_NO,STATE,PAYLOAD_JSON,ACTOR,REASON)values(v_id,v_version+1,v_status,v_body,p_actor,v_reason);
  elsif cmd in('PUBLISH','ARCHIVE')then
   RRL_ACCESS_API.assert_allowed(p_actor,'knowledge_publish','PLATFORM',null);
   select CURRENT_VERSION into v_version from RRL_KNOWLEDGE_ARTICLE where ARTICLE_ID=v_id;
   if v_version!=v_expected then fail('VERSION_CONFLICT');end if;
   select PAYLOAD_JSON into v_body from RRL_KNOWLEDGE_REV where ARTICLE_ID=v_id and VERSION_NO=v_version;
   if can_read(p_actor,v_body)=0 then fail('ARTICLE_ACCESS_DENIED');end if;
   v_status:=case when cmd='PUBLISH' then 'PUBLISHED' else 'ARCHIVED' end;
   insert into RRL_KNOWLEDGE_REV(ARTICLE_ID,VERSION_NO,STATE,PAYLOAD_JSON,ACTOR,REASON)values(v_id,v_version+1,v_status,v_body,p_actor,v_reason);
   update RRL_KNOWLEDGE_ARTICLE set CURRENT_VERSION=v_version+1,
    PUBLISHED_VERSION=case when cmd='PUBLISH' then v_version+1 else null end,
    ARCHIVED=case when cmd='ARCHIVE' then 1 else 0 end where ARTICLE_ID=v_id;
  else fail('UNKNOWN_COMMAND');end if;
  j:=json_object_t();j.put('operation_id',p_operation);j.put('command_type',cmd);j.put('object_id',v_id);j.put('version',v_version+1);j.put('replayed',false);p_result:=j.to_clob;
  insert into RRL_PLATFORM_COMMAND(DOMAIN,OPERATION_ID,ACTOR,PAYLOAD_HASH,RESULT_JSON)values('KNOWLEDGE',p_operation,p_actor,p_hash,p_result);
 end;
end RRL_KNOWLEDGE_API;
/
