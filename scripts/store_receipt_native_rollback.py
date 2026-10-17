"""Caller-owned stock entry; NativeAPI.post intentionally must not be used here."""
from uuid import uuid4
import oracledb
from app.modules.inventory.public import StockCommand
from app.modules.delivery.infrastructure.store_receipt_read import read_store_preview
from app.modules.platform.public import read_oracle_json

class RevertReceipt(Exception):pass


def verify_store_receipt_rollback(gateway,actor):
 load='FLOOR1194.LOAD:f49901f5d2';address='Own full-pallet ST';operation='STORE.SCOPED.ROLLBACK:'+uuid4().hex
 preview=read_store_preview(gateway,load,address,actor)
 assert not preview['requires_marked_recipient_flow']and not preview['already_received']
 command=StockCommand(operation_id=operation,command_type='STORE_RECEIPT',actor=actor,source={'load_operation_id':load,'store_address':address},lines=(),metadata={'scan_place':preview['root_scan_identifier'],'expected_composition_signature':preview['composition_signature'],'before_cameras':True})
 try:
  with gateway.transaction('Caller-owned scoped store receipt rollback acceptance')as c:
   out=c.var(oracledb.DB_TYPE_CLOB)
   try:
    c.callproc('RRL_STOCK_POSTING_API.prepare_command',[command.canonical_json(),actor,out])
    assert out.getvalue()is None
    c.callproc('RRL_STOCK_POSTING_API.execute_prepared',[out])
    value=read_oracle_json(out.getvalue())
    assert value['status']=='ACCEPTED'and value['warehouse_stock_consumed_again']is False
    c.execute('select count(*)from RRL_STORE_RECEIPT_FACT where OPERATION_ID=:op',op=operation);assert c.fetchone()[0]==1
   finally:c.callproc('RRL_STOCK_POSTING_API.reset_connection')
   raise RevertReceipt()
 except RevertReceipt:pass
 for table in('RRL_STORE_RECEIPT_FACT','RRL_STOCK_OPERATION'):
  assert gateway.fetch_all('select count(*) N from '+table+' where OPERATION_ID=:op',{'op':operation})[0]['n']==0
 return {'native_store_only_actor_accepted':True,'receipt_and_operation_rollback_verified':True,'warehouse_stock_consumed_again':False}
