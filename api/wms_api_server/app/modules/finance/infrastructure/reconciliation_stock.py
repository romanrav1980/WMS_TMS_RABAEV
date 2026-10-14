from typing import Any

INVALID_QUANTITY="r.REMAIN is null or r.REMAIN<0 or r.HARD_RESERVED_BASE is null or r.HARD_RESERVED_BASE<0 or r.HARD_RESERVED_BASE>r.REMAIN or r.BASE_UOM is null"
COMPOSITION_SOURCE="""from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
    where c.WARE_ID=:ware and(r.REMAIN>0 or exists(select 1 from RRL_WMS_RECEIPT_UNIT tracked where tracked.CURRENT_UID=r.UID_POLETA and tracked.CURRENT_CELL=r.CELL and(tracked.STOCK_STATUS is null or tracked.STOCK_STATUS!='ISSUED')))and(exists(select 1 from RRL_WMS_RECEIPT_UNIT tracked where tracked.CURRENT_UID=r.UID_POLETA and tracked.CURRENT_CELL=r.CELL and(tracked.STOCK_STATUS is null or tracked.STOCK_STATUS!='ISSUED'))or exists(select 1 from RRL_SKU_RECEIPT_PROFILE sp where sp.ARTICUL=p.ARTICUL)or exists(select 1 from RRL_SKU_RECEIPT_POLICY pol where pol.ARTICUL=p.ARTICUL and pol.MARKING_REQUIRED=1)or exists(select 1 from RRL_FINISHED_GOODS_SKU fg where fg.ARTICUL=p.ARTICUL and fg.CRPT_REQUIRED=1))
    and(r.REMAIN!=nvl((select sum(u.BASE_QTY)from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=r.UID_POLETA and u.CURRENT_CELL=r.CELL and(u.STOCK_STATUS is null or u.STOCK_STATUS!='ISSUED')),0)
    or exists(select 1 from RRL_WMS_RECEIPT_UNIT u where u.CURRENT_UID=r.UID_POLETA and u.CURRENT_CELL=r.CELL and(u.STOCK_STATUS is null or u.STOCK_STATUS!='ISSUED')and(u.BASE_QTY is null or u.BASE_QTY<=0 or u.BASE_UOM is null or u.BASE_UOM!=r.BASE_UOM or u.PHYSICAL_UNIT_KEY is null)))"""

def stock_snapshot(cursor: Any,ware: int) -> dict[str,Any]:
    cursor.execute(f"""select r.BASE_UOM,to_char(sum(r.REMAIN),'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
    to_char(sum(r.HARD_RESERVED_BASE),'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),count(*),
    sum(case when {INVALID_QUANTITY} then 1 else 0 end)
    from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware group by r.BASE_UOM order by r.BASE_UOM""",{"ware":ware})
    rows=[{"base_uom":unit,"physical_quantity":physical,"hard_quantity":hard,"stock_rows":count,"invalid_rows":bad}for unit,physical,hard,count,bad in cursor.fetchall()]
    cursor.execute(f"""select count(*){COMPOSITION_SOURCE}""",{"ware":ware})
    return {"scope":"CURRENT_SNAPSHOT","by_base_uom":rows,"physical_unit_composition_conflicts":cursor.fetchone()[0],"regulatory_external_ack_verified":False}
