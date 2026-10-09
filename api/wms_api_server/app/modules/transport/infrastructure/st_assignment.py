"""Existing ST assignment via RRL_TT_ADD_PALL, with one transaction and visible errors."""
import oracledb
from ....oracle_gateway import OracleGateway


def assign_sts(gateway: OracleGateway, task_id: int, st_numbers: list[str]) -> dict:
    numbers=sorted(set(st_numbers))
    if not numbers or len(numbers)>200:
        raise ValueError('Select 1..200 distinct STs')
    with gateway.transaction('Existing transport ST assignment') as cur:
        cur.execute('select CONDITION,PAY_ORDER_ID,DELETED from RRL_TRANSPORT_TASK where ID=:id for update', {'id':task_id})
        task=cur.fetchone()
        if not task or task[2] or task[0]=='Отгружен':
            raise ValueError('Existing active unshipped trip is required')
        if task[1]:
            raise ValueError('Trip included in billing cannot change its STs')
        for number in numbers:
            cur.execute('select TRANSTASK_ID from RRL_SBORKA_PALLETS where ST_NUMBER=:n and CONDITION<>2 for update', {'n':number})
            pallets=cur.fetchall()
            if not pallets:
                raise ValueError('ST not found: '+number)
            if any(p[0] not in (None,0,task_id) for p in pallets):
                raise ValueError('ST already belongs to another trip: '+number)
        for number in numbers:
            result=cur.callfunc('RRL_TT_ADD_PALL',oracledb.DB_TYPE_VARCHAR,[task_id,number])
            if str(result or '').lower().startswith('err'):
                raise ValueError('Existing ST writer failed: '+str(result))
            cur.execute('select count(*) from RRL_SBORKA_PALLETS where ST_NUMBER=:n and CONDITION<>2 and nvl(TRANSTASK_ID,0)<>:id', {'n':number,'id':task_id})
            if cur.fetchone()[0]:
                raise ValueError('ST writer did not persist its assignment')
        cur.callfunc('RRL_TT_REORDER_ADR',oracledb.DB_TYPE_NUMBER,[task_id])
    return {'assigned':len(numbers),'warnings':[]}
