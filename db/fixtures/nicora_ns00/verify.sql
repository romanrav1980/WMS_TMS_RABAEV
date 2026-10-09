-- NS00 diagnostics only; targets current RABAEV. No business DML.
select sys_context('USERENV','SESSION_USER') USER_NAME,
       sys_context('USERENV','DB_NAME') DB_NAME,
       sys_context('USERENV','SERVICE_NAME') SERVICE_NAME from dual;
select count(*) INVALID_COUNT from user_objects where status='INVALID' and object_name not like 'BIN$%';
select count(*) ERROR_COUNT from user_errors where name not like 'BIN$%' and attribute='ERROR';
select p.UID_PALLET,p.ARTICUL,p.EXPIRY_DATE,r.CELL,r.REMAIN
  from RRL_PALLETS p join RRL_REMAINS r on r.UID_POLETA=p.UID_PALLET
 where p.UID_PALLET in ('DS-BASE-B1','DS-BASE-B2') order by p.UID_PALLET;
select o.ORDER_NO,r.ORDER_QTY,r.PACK_COUNT
  from RRL_CUSTOMER_ORDER o join RRL_CUSTOMER_ORDER_ROW r on r.CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID
 where o.CUSTOMER_ORDER_ID in (-980711,-980712,-980713) order by o.ORDER_NO;
