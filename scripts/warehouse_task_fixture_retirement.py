"""Retire only owned QA task metadata; retain task/version/access/event history."""
from typing import Any
from app.modules.platform.public import stock_configuration_transaction
from app.services.warehouse_task_service import WarehouseTaskService
from app.services.resource_management_service import ResourceManagementService
from app.schemas import WarehouseTaskStatusRequest, ResourceSessionStatusRequest


def retire_metadata(gateway: Any, context: dict[str, Any]) -> None:
    from warehouse_task_scoped_complete_smoke import access
    for role, assignment in context['grants']:
        rows = gateway.fetch_all('select VERSION_NO,REVOKED_AT from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:id', {'id': assignment})
        if rows and rows[0]['revoked_at'] is None:
            access(gateway, context, 'REVOKE', dict(assignment_id=assignment, expected_version=int(rows[0]['version_no']), reason='Retire owned QA fixture; preserve access history'))
        rows = gateway.fetch_all('select VERSION_NO,ACTIVE from RRL_ACCESS_ROLE where ROLE_ID=:id', {'id': role})
        if rows and rows[0]['active'] == 1:
            access(gateway, context, 'ROLE_SAVE', dict(role_id=role, title='Retired QA task fixture', permissions=[], active=False, expected_version=int(rows[0]['version_no'])))
    if 'task' not in context:
        return
    WarehouseTaskService(gateway).cancel_task(context['task'], WarehouseTaskStatusRequest(updated_by='admin', reason='Retire isolated QA metadata; goods commands were caller-rollback only'))
    rows = gateway.fetch_all('select STATUS from RRL_RESOURCE_SESSION where SESSION_ID=:id', {'id': context['session']})
    if rows and rows[0]['status'] in ('ACTIVE', 'PAUSED'):
        ResourceManagementService(gateway).logout_session(context['session'], ResourceSessionStatusRequest(updated_by='admin'))
    with stock_configuration_transaction(gateway, 'Retire owned QA resource metadata, retain history', 'admin', 'warehouse_settings_edit') as cursor:
        cursor.execute('update RRL_RESOURCE_TASK_QUAL set ACTIVE=0 where RESOURCE_ID=:id', id=context['resource'])
        cursor.execute('update RRL_RESOURCE set ACTIVE=0 where RESOURCE_ID=:id', id=context['resource'])
        cursor.execute('update RRL_RESOURCE_EQUIPMENT set ACTIVE=0 where EQUIPMENT_ID=:id', id=context['equipment'])
        cursor.execute("update RRL_RESOURCE_SHIFT set STATUS='CLOSED'where SHIFT_ID=:id", id=context['shift'])
        cursor.execute('update RRL_CELLS set BLOCKED_FOR_ACCEPT=1,BLOCKED_FOR_REMAINS=1,BLOCKED_FOR_POPOLNENIE=1 where CELL=:cell', cell=context['cell'])
    with gateway.transaction('Retire exact owned QA identities after closing resources') as cursor:
        cursor.execute('lock table RRL_ACCESS_REV in exclusive mode wait 2')
        cursor.execute('update RUSERS set DELETED=1 where ID in(:actor,:other)', actor=context['actor'], other=context['other'])
