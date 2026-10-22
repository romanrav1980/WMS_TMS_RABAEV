"""Synthetic logical demand only; physical receipt/move/bind use their real APIs."""
from tools.mcp.tms_mcp_server import oracle_connection


def prepare_shipment(state):
    f=state['fixture'];w=f['warehouse_id'];uid=state.get('shipment_identifier','FP21.ST.'+str(w))
    quantity=int(state.get('shipment_quantity',10));assert quantity>0
    assert f['article'].startswith('TC03') and state['native_order']>0
    with oracle_connection()as c:
        q=c.cursor();q.execute('select NAME from RRL_WARES where ID=:w',w=w);assert q.fetchone()==('TRADECASE QA '+f['tag'],)
        q.execute("select WARE_ID,SOURCE_SYSTEM from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=:o",o=state['native_order']);assert q.fetchone()==(w,'QA_TRADECASE_ONLY')
        q.execute('select s.ID,f.CUSTOMER_ORDER_ID from RRL_SBORKA_PALLETS s left join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.LEGACY_SBORKA_PALLET_ID=s.ID where s.PALLET_UID=:u',u=uid);old=q.fetchall()
        if old:
            assert len(old)==1 and old[0][1]==state['native_order'],'Do not claim another fixture shipment'
            return dict(shipment_id=old[0][0],shipment_identifier=uid)
        q.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
        try:
            q.execute('select trunc(sysdate)+1 from dual');day=q.fetchone()[0]
            st=q.callfunc('RRL_SBORKA_PALLETS_ADD2',int,['FP.'+str(w),'FP21.QA.ADDRESS',1,uid,'1',day,'','admin',w]);assert st>0
            q.execute('update RRL_SBORKA_PALLETS set CONDITION=0 where ID=:s',s=st)
            row=q.callfunc('RRL_SBORKA_PALLET_ROWS_ADD4',int,[uid,f['article'],'Owned physical shipment QA','','EA',0,'',quantity,'',quantity,0,None,'FP.'+str(w),w,1]);assert row>0
            q.execute("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,ADDRESS_TEXT,STATUS,FACT_QTY,FACT_WEIGHT,SOURCE_SYSTEM,CREATED_AT,CREATED_BY)values(RRL_CUSTOMER_ORDER_FULF_SQ.nextval,:o,:s,:u,'FP21.QA.ADDRESS','PLANNED',0,0,'QA_TRADECASE_ONLY',sysdate,'admin')",o=state['native_order'],s=st,u=uid);c.commit()
        finally:q.callproc('RRL_STOCK_METADATA_TX.end_change')
    return dict(shipment_id=st,shipment_identifier=uid)
