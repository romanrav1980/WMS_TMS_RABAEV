-- Recovery: export newly authored metadata first; do not use after live adoption without reviewed export.
-- No legacy table/function changed by this migration.
drop package RRL_KNOWLEDGE_API;
drop package RRL_ACCESS_API;
drop table RRL_KNOWLEDGE_REV;
drop table RRL_KNOWLEDGE_ARTICLE;
drop table RRL_KNOWLEDGE_SPACE;
drop table RRL_ACCESS_AUDIT;
drop table RRL_PLATFORM_COMMAND;
drop table RRL_ACCESS_ASSIGNMENT;
drop table RRL_ACCESS_GROUP_MEMBER;
drop table RRL_ACCESS_GROUP;
drop table RRL_ACCESS_BRANCH_MEMBER;
drop table RRL_ACCESS_OBJECT;
drop table RRL_ACCESS_ROLE_RIGHT;
drop table RRL_ACCESS_ROLE;
drop table RRL_ACCESS_REV;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-scoped-access-knowledge';
commit;
