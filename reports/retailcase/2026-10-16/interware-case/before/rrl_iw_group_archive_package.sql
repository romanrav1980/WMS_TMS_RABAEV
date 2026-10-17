create or replace package RRL_IW_GROUP_ARCHIVE authid definer accessible by(package RRL_IW_GROUP_SOURCE,package RRL_IW_GROUP_REC)as
 function snapshot_json(p_load varchar2)return clob;
end;
/
