-- Resume after verified ORA-02270 on missing legacy RUSERS unique key.
create table RRL_ACCESS_ASSIGNMENT(
 ASSIGNMENT_ID varchar2(80) primary key, USERNAME nvarchar2(50) not null, ROLE_ID varchar2(80) references RRL_ACCESS_ROLE(ROLE_ID), SCOPE_KIND varchar2(20) not null, SCOPE_ID varchar2(100), MEMBERSHIP varchar2(10) default 'CURRENT' not null check(MEMBERSHIP in('CURRENT','SNAPSHOT')), SNAPSHOT_VERSION number, VALID_FROM timestamp with time zone not null, VALID_UNTIL timestamp with time zone, REVOKED_AT timestamp with time zone, ASSIGNED_BY nvarchar2(50) not null, REASON nvarchar2(500) not null, VERSION_NO number not null, check(VALID_UNTIL is null or VALID_UNTIL>VALID_FROM), check(SCOPE_KIND in('WAREHOUSE','DC','STORE','CARRIER','REGION','ZONE','ORG_BRANCH','GROUP','SELF','NETWORK','PLATFORM')), check((SCOPE_KIND in('SELF','NETWORK','PLATFORM') and SCOPE_ID is null)or(SCOPE_KIND not in('SELF','NETWORK','PLATFORM') and SCOPE_ID is not null)), check((MEMBERSHIP='CURRENT' and SNAPSHOT_VERSION is null)or(MEMBERSHIP='SNAPSHOT' and SCOPE_KIND in('GROUP','ORG_BRANCH') and SNAPSHOT_VERSION>0))
);
create table RRL_PLATFORM_COMMAND(
 DOMAIN varchar2(20) not null, OPERATION_ID varchar2(100) not null, ACTOR nvarchar2(50) not null, PAYLOAD_HASH varchar2(64) not null, RESULT_JSON clob not null check(RESULT_JSON is json), CREATED_AT timestamp with time zone default systimestamp not null, primary key(DOMAIN,OPERATION_ID)
);
create table RRL_ACCESS_AUDIT(
 AUDIT_ID number generated always as identity primary key, OPERATION_ID varchar2(100) not null, ACTOR nvarchar2(50) not null, COMMAND_TYPE varchar2(30) not null, OBJECT_ID varchar2(100) not null, PAYLOAD_JSON clob not null check(PAYLOAD_JSON is json), CREATED_AT timestamp with time zone default systimestamp not null
);
create table RRL_KNOWLEDGE_SPACE(
 SPACE_ID varchar2(80) primary key, TITLE nvarchar2(200) not null, VERSION_NO number not null
);
create table RRL_KNOWLEDGE_ARTICLE(
 ARTICLE_ID varchar2(80) primary key, SPACE_ID varchar2(80) not null references RRL_KNOWLEDGE_SPACE(SPACE_ID), CURRENT_VERSION number not null, PUBLISHED_VERSION number, ARCHIVED number(1) default 0 not null check(ARCHIVED in(0,1))
);
create table RRL_KNOWLEDGE_REV(
 ARTICLE_ID varchar2(80) references RRL_KNOWLEDGE_ARTICLE(ARTICLE_ID), VERSION_NO number not null, STATE varchar2(15) not null check(STATE in('DRAFT','PUBLISHED','ARCHIVED')), PAYLOAD_JSON clob not null check(PAYLOAD_JSON is json), ACTOR nvarchar2(50) not null, REASON nvarchar2(500) not null, CREATED_AT timestamp with time zone default systimestamp not null, primary key(ARTICLE_ID,VERSION_NO)
);
create table RRL_ACCESS_BRANCH_MEMBER(
 BRANCH_KEY varchar2(120) not null,SNAPSHOT_VERSION number not null,KIND varchar2(20) not null,OBJECT_ID varchar2(100) not null,
 primary key(BRANCH_KEY,SNAPSHOT_VERSION,KIND,OBJECT_ID),foreign key(KIND,OBJECT_ID) references RRL_ACCESS_OBJECT(KIND,OBJECT_ID));
insert into RRL_ACCESS_REV(ID,REVISION)values(1,1);
create index RRL_ACCESS_ASSIGN_USER_I on RRL_ACCESS_ASSIGNMENT(USERNAME,ROLE_ID,REVOKED_AT);
create index RRL_ACCESS_ASSIGN_ROLE_I on RRL_ACCESS_ASSIGNMENT(ROLE_ID);
create index RRL_ACCESS_OBJECT_PARENT_I on RRL_ACCESS_OBJECT(PARENT_KIND,PARENT_ID);
create index RRL_ACCESS_MEMBER_OBJECT_I on RRL_ACCESS_GROUP_MEMBER(KIND,OBJECT_ID);
create index RRL_PLATFORM_COMMAND_ACTOR_I on RRL_PLATFORM_COMMAND(ACTOR,DOMAIN,CREATED_AT);
create index RRL_KNOWLEDGE_SPACE_I on RRL_KNOWLEDGE_ARTICLE(SPACE_ID);
commit;
