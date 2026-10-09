"""Stock movement through the enabled legacy event trigger and existing task ledger."""
from decimal import Decimal


def apply_task_stock_move(gateway, task: dict, actor: str) -> bool:
    state = gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if not state or state[0]["state"] != "PREPARED":
        applied = gateway.fetch_all("""
            select m.STOCK_MOVE_ID from RRL_WAREHOUSE_TASK_STOCK_MOVE m
              join RRL_STOCK_OPERATION o on o.OPERATION_ID=m.OPERATION_ID
             where m.TASK_ID=:id and o.STATE='APPLIED' and o.COMMAND_TYPE='TASK_COMPLETE'
        """, {"id": int(task["task_id"])})
        if not applied:
            raise ValueError("Use TASK_COMPLETE before synchronizing physical stock")
        # Physical effect and its domain sync have already committed atomically.
        return False
    task_id = int(task["task_id"])
    previous = gateway.fetch_all("select * from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:id", {"id": task_id})
    if previous:
        # A historical ledger is authoritative; never emit a second event.
        old = previous[0]
        if (old["uid_pallet"] != (task.get("uid_pallet") or task.get("sscc"))
                or old["from_cell"] != task.get("from_cell") or old["to_cell"] != task.get("to_cell")
                or Decimal(str(old["qty"])) != Decimal(str(task.get("fact_qty") if task.get("fact_qty") is not None else task.get("qty")))):
            raise ValueError("Historical movement differs from warehouse fact; explicit reconciliation is required.")
        return False
    uid = task.get("uid_pallet") or task.get("sscc")
    source, target = task.get("from_cell"), task.get("to_cell")
    qty = Decimal(str(task.get("fact_qty") if task.get("fact_qty") is not None else task.get("qty")))
    if not uid or not source or not target or source == target or not qty.is_finite() or qty <= 0:
        raise ValueError("A positive stock movement requires pallet and distinct source/target cells.")
    pallets = gateway.fetch_all("select ARTICUL,PRIHOD_NAKLAD_ID from RRL_PALLETS where UID_PALLET=:p for update", {"p": uid})
    if len(pallets) != 1:
        raise ValueError("Stock pallet identity is missing or ambiguous.")
    expected_article = task.get("target_articul") or task.get("raw_articul")
    if expected_article and pallets[0]["articul"] != expected_article:
        raise ValueError("Stock article does not match warehouse task.")
    pending = gateway.fetch_all(
        "select TASK_ID from RRL_WAREHOUSE_TASK where TASK_SOURCE='SAP_RECEIPT' and UID_PALLET=:p and STATUS<>'DONE' and rownum=1",
        {"p": uid},
    )
    if pending:
        raise ValueError("Incoming SAP pallet has not completed its permitted placement.")
    nested = gateway.fetch_all(
        """select a.AGGREGATION_ID from RRL_CRPT_AGGREGATION a
           where (a.UID_PALLET=:p or a.SSCC=:p) and (a.PARENT_SSCC is not null or exists
             (select 1 from RRL_CRPT_AGGREGATION_ITEMS i where i.AGGREGATION_ID=a.AGGREGATION_ID and i.CHILD_TYPE='SSCC')) and rownum=1""",
        {"p": uid},
    )
    if nested:
        raise ValueError("Nested SSCC movement requires the NI04 tree composition command.")
    # Cell locks also serialize creation of a destination remainder that did not exist.
    cells = gateway.fetch_all(
        "select CELL,WARE_ID,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE from RRL_CELLS where CELL in (:f,:t) order by CELL for update",
        {"f": source, "t": target},
    )
    by_cell = {row["cell"]: row for row in cells}
    if len(by_cell) != 2:
        raise ValueError("Both movement cells must exist.")
    for cell, expected in [(source, task.get("from_ware_id")), (target, task.get("to_ware_id"))]:
        if expected is not None and by_cell[cell]["ware_id"] != expected:
            raise ValueError("Movement cell belongs to another warehouse.")
    if by_cell[source]["ware_id"] != by_cell[target]["ware_id"]:
        raise ValueError("Cross-warehouse transfer requires the interwarehouse process.")
    if any(by_cell[target].get(key) for key in ("blocked_for_accept", "blocked_for_remains", "blocked_for_popolnenie")):
        raise ValueError("Movement destination is blocked.")
    remains = gateway.fetch_all(
        "select CELL,to_char(REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') REMAIN from RRL_REMAINS where UID_POLETA=:p order by CELL for update",
        {"p": uid},
    )
    # Legacy event trigger updates every matching row: duplicates must not multiply an effect.
    if len([r for r in remains if r["cell"] == source]) != 1 or len([r for r in remains if r["cell"] == target]) > 1:
        raise ValueError("Source/destination remainder is missing or duplicated; reconcile before moving.")
    source_qty = next(Decimal(r["remain"]) for r in remains if r["cell"] == source)
    if source_qty < qty:
        raise ValueError("Insufficient source quantity for warehouse completion.")
    whole = qty == source_qty and all(Decimal(r["remain"]) == 0 for r in remains if r["cell"] != source)
    if task.get("qty_mode") == "PALLET" and not whole:
        raise ValueError("Full-pallet task must move the entire physical pallet stock.")
    if not whole:
        marked = gateway.fetch_all(
            """select (select count(*) from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:p)
                     +(select count(*) from RRL_CRPT_CODES where UID_PALLET=:p)
                     +(select count(*) from RRL_PALLETS p left join RRL_SKU_RECEIPT_POLICY s on s.ARTICUL=p.ARTICUL
                        left join RRL_FINISHED_GOODS_SKU f on f.ARTICUL=p.ARTICUL
                        where p.UID_PALLET=:p and (nvl(s.MARKING_REQUIRED,0)=1 or nvl(f.CRPT_REQUIRED,0)=1)) N from dual""",
            {"p": uid},
        )
        if marked[0]["n"]:
            raise ValueError("Partial marked movement requires explicit unit composition; complete it through the NI04 composition command.")
    gateway.execute(
        """insert into RRL_EVENTS(ID_EVENT,CELL_FROM,CELL_TO,DATE_EVENT,COUNT_EVENT,TYPE_EVENT,UID_POLETA,USER_ID,PRIHOD_NAKL_ID)
           values(RRL_EVENT_ID_SQ.nextval,:f,:t,sysdate,:q,2,:p,:a,:n)""",
        {"f": source, "t": target, "q": qty, "p": uid, "a": actor, "n": pallets[0]["prihod_naklad_id"]},
    )
    gateway.execute(
        """insert into RRL_WAREHOUSE_TASK_STOCK_MOVE(STOCK_MOVE_ID,TASK_ID,TASK_SOURCE,TASK_TYPE,SOURCE_DOC_TYPE,SOURCE_DOC_ID,SOURCE_TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY,CREATED_AT,CREATED_BY)
           values(RRL_WH_TASK_STOCK_MOVE_SQ.nextval,:id,:s,:kind,:doc,:docid,:sid,:p,:f,:t,:q,systimestamp,substr(:a,1,100))""",
        {"id": task_id, "s": task.get("task_source"), "kind": task.get("task_type"), "doc": task.get("source_doc_type"),
         "docid": task.get("source_doc_id"), "sid": task.get("source_task_id"), "p": uid, "f": source, "t": target, "q": qty, "a": actor},
    )
    return True
