create or replace package RRL_IW_AGG_SCAN authid definer accessible by(package RRL_INTERWARE_MARK_SCAN)as
 procedure expand(p_metadata clob,p_scans out clob);
end;
/
