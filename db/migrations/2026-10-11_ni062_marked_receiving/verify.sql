select name,type,line,text from user_errors where name not like 'BIN$%';
select current_uid,current_cell,stock_status,unit_version,uid_pallet from RRL_WMS_RECEIPT_UNIT where current_uid='RETURN233:13508027ed';
select operation_id,uid_pallet,stock_event_id from RRL_STORE_RETURN_RECEIPT where operation_id='RET234.RECEIVE:13508027ed1';
