package RRL_STOCK_POOL_READ authid definer as
 function snapshot_json(p_ware number,p_article varchar2) return clob;
 function line_snapshot_json(p_line number) return clob;
end;