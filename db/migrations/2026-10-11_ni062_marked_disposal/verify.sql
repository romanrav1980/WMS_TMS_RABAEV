select name,type,line,text from user_errors where name not like 'BIN$%';
select target_system,status from RRL_EVENT_OUTBOX where correlation_id='RET236.DISPOSE:13508027ed0'and event_type='MARKED_GOODS_DISPOSED';
select remain,hard_reserved_base from RRL_REMAINS where uid_poleta='RETURN233:13508027ed';
