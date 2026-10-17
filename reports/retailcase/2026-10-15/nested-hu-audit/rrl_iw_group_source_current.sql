package body RRL_IW_GROUP_SOURCE as
 function source_json(p_load varchar2,p_actor varchar2)return clob is
 begin RRL_INTERWARE_UNIT_SOURCE.assert_scope(p_load,p_actor);return RRL_IW_GROUP_ARCHIVE.snapshot_json(p_load);end;
end;
