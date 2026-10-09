select 'REMAINS' KIND,count(*) ROWS_LEFT from RRL_REMAINS
union all select 'EVENTS',count(*) from RRL_EVENTS
union all select 'NEW_OPERATIONS',count(*) from RRL_STOCK_OPERATION;
