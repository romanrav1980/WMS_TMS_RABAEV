select name,type,line,text from user_errors where name not like 'BIN$%';
select target_system,status from RRL_EVENT_OUTBOX where correlation_id='RET237.SUP.LOAD:13508027ed'and event_type='MARKED_SUPPLIER_RETURN_DISPATCHED';
select remain,hard_reserved_base from RRL_REMAINS where uid_poleta='RETURN237:13508027ed';
