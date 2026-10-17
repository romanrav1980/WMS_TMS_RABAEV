"""Authorize complete selected invoices inside the workbook read snapshot."""
import json
from typing import Any
from ..contracts import LogisticsCostError
from ..contracts_billing_export import BillingExportError
from .cost_access import require_warehouse


def authorize_billing_export(cursor: Any, invoice_ids: list[int], actor: str) -> None:
    if not actor:
        raise BillingExportError("BILLING_EXPORT_ACTOR_REQUIRED", "Не указан пользователь выгрузки", 403)
    cursor.execute("""select RRL_HAS_WRIGHT(ID,'transport_dispatch_view') from RUSERS
        where ID=:actor and nvl(DELETED,0)=0""", actor=actor)
    current = cursor.fetchone()
    if current is None:
        raise BillingExportError("BILLING_EXPORT_ACTOR_REQUIRED", "Нет доступа к выгрузке", 403)
    if not invoice_ids:
        if current[0] != 1:
            raise BillingExportError("BILLING_EXPORT_EMPTY_SCOPE", "Для пустого реестра не определена область склада", 403)
        return
    selected = json.dumps(invoice_ids)
    cursor.execute("""select WARE_ID from (
        select s.WARE_ID from RRL_SBORKA_PALLETS s join RRL_TRANSPORT_TASK t on t.ID=s.TRANSTASK_ID
        join json_table(:ids,'$[*]' columns(ID number path '$')) selected on selected.ID=t.PAY_ORDER_ID
        union select l.WARE_ID from RRL_TT_HU_LOAD_FACT l join RRL_TRANSPORT_TASK t on t.ID=l.TT_ID
        join json_table(:ids,'$[*]' columns(ID number path '$')) selected on selected.ID=t.PAY_ORDER_ID
        union select r.WARE_ID from RRL_LOGISTICS_COST_RUN r join RRL_TRANSPORT_TASK t on t.ID=r.TT_ID
        join json_table(:ids,'$[*]' columns(ID number path '$')) selected on selected.ID=t.PAY_ORDER_ID)
        fetch first 201 rows only""", ids=selected)
    warehouses = cursor.fetchall()
    if len(warehouses) > 200:
        raise BillingExportError("BILLING_EXPORT_WAREHOUSE_BOUND_200", "Более200 складов; уточните фильтры")
    try:
        for (warehouse,) in warehouses:
            if warehouse is None:
                raise BillingExportError("BILLING_EXPORT_WAREHOUSE_REQUIRED", "Не определён склад документа", 403)
            require_warehouse(cursor, warehouse, actor, "transport_dispatch_view")
    except LogisticsCostError as error:
        raise BillingExportError(error.code, str(error), error.status) from error
    if current[0] != 1:
        cursor.execute("""select count(*) from json_table(:ids,'$[*]'columns(ID number path '$')) selected
            where not exists(select 1 from RRL_TRANSPORT_TASK t where t.PAY_ORDER_ID=selected.ID and(
                exists(select 1 from RRL_SBORKA_PALLETS s where s.TRANSTASK_ID=t.ID)
                or exists(select 1 from RRL_TT_HU_LOAD_FACT l where l.TT_ID=t.ID)
                or exists(select 1 from RRL_LOGISTICS_COST_RUN r where r.TT_ID=t.ID)))""", ids=selected)
        if cursor.fetchone()[0] != 0:
            raise BillingExportError("BILLING_EXPORT_UNKNOWN_DOCUMENT_SCOPE", "Не определены склады всех счетов; уточните фильтры", 403)
