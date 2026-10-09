"""Bind DS-BASE core records to actual NS00 legacy columns; no runtime imports."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'wiki/requirements/nikora_delivery_v55/execution/fixtures/base.json'
WARE_ID = 9807
PREFIX = 'DS-BASE-'
TABLE_KEYS = {
    'RRL_WARES': ('ID',), 'RRL_CELLS': ('CELL',),
    'RRL_ARTICULS': ('ACTICUL',), 'RRL_CUSTOMER': ('CUSTOMER_ID',),
    'RRL_PRIHOD_NAKLAD': ('ID',), 'RRL_PALLETS': ('UID_PALLET',),
    'RRL_REMAINS': ('UID_POLETA', 'CELL'),
    'RRL_CUSTOMER_ORDER': ('CUSTOMER_ORDER_ID',),
    'RRL_CUSTOMER_ORDER_ROW': ('CUSTOMER_ORDER_ROW_ID',),
}


def plan() -> dict[str, list[dict]]:
    base = json.loads(BASE.read_text(encoding='utf-8'))
    start = datetime.fromisoformat(base['clock']['start']).replace(tzinfo=None)
    rows = {table: [] for table in TABLE_KEYS}
    rows['RRL_WARES'] = [dict(ID=WARE_ID, NAME='DS-BASE NS00 synthetic', PREFIX='NB0',
                             WARE_COMMENT='NS00 owned fixture; not production',
                             FLAG_FINISHED_GOODS=1, MES_ENABLED=0)]
    for index, cell in enumerate(base['locations'], 1):
        rows['RRL_CELLS'].append(dict(CELL=PREFIX+cell['id'], WARE_ID=WARE_ID,
                                    X=index, Y=1, Z=1, OTBOR=int(cell['id']=='P1'),
                                    IS_SYSTEM=int(cell.get('virtual', False)),
                                    BLOCKED_FOR_REMAINS=1, BLOCKED_FOR_POPOLNENIE=1,
                                    BLOCKED_FOR_ACCEPT=1))
    for item in base['products']:
        sku = dict(ACTICUL=PREFIX+item['sku'], NORMA_UKLADKI=1,
                   BARCODE_SHT='NS00-TEST-'+item['sku'], NAME='DS-BASE synthetic '+item['sku'],
                   UNIT_TYPE='KG' if item['sku']=='FRESH' else 'PCS', CELL=PREFIX+'P1',
                   FLOATING_WEIGHT=int(item['sku']=='FRESH'),
                   COUNT_SHT_IN_KOR=item.get('piecesPerBox', item.get('piecesPerTestBox', 1)),
                   SHIPMENT_AGING_HOURS=0, SHIPMENT_AGING_COMMENT='NS00 baseline')
        if 'grossKg' in item:
            sku.update(BRUTTO_WEIGHT_OF_KOR=Decimal(item['grossKg']),
                       WEIGHT_OF_KOR=Decimal(item['netKg']), CARTON_WEIGHT=Decimal(item['boxTareKg']))
        if 'dimensionsMm' in item:
            sku.update(zip(('DIMKOR_X','DIMKOR_Y','DIMKOR_Z'), item['dimensionsMm']))
        rows['RRL_ARTICULS'].append(sku)
    for index, store in enumerate(base['stores'], 1):
        rows['RRL_CUSTOMER'].append(dict(CUSTOMER_ID=-980700-index, CUSTOMER_CODE=PREFIX+store['id'],
                                        CUSTOMER_NAME='DS-BASE synthetic '+store['id'], CUSTOMER_TYPE='STORE',
                                        ACTIVE=0, CREATED_AT=start, CREATED_BY='DS-BASE'))
    rows['RRL_PRIHOD_NAKLAD'] = [dict(ID=-980700, NAKLAD_NUMBER=PREFIX+'IN',
                                    WARE_ID=WARE_ID, DATE_OF_NAKLAD=start, CONDITION=0, PROOVED=0)]
    for index, lot in enumerate(base['lots'], 1):
        uid = PREFIX+lot['lot']
        rows['RRL_PALLETS'].append(dict(UID_PALLET=uid, ARTICUL=PREFIX+'D10',
                                       CREATION_DATE=start, EXPIRY_DATE=datetime.fromisoformat(lot['expiry']),
                                       UNIT_COUNT=Decimal('1200'), COUNT_KOR=Decimal('50'),
                                       PRIHOD_NAKLAD_ID=-980700, PRINTED=0, KLADOVSHIK='DS-BASE',
                                       QUALITY_STATUS='RELEASED', CRPT_STATUS='NOT_REQUIRED'))
        rows['RRL_REMAINS'].append(dict(UID_POLETA=uid, CELL=PREFIX+'P1' if index==1 else PREFIX+'RES1',
                                       REMAIN=Decimal('1200'), TIME_OF_LAST_UPDATE=start))
    for index, order in enumerate(base['orders'], 1):
        order_id = -980710-index
        rows['RRL_CUSTOMER_ORDER'].append(dict(CUSTOMER_ORDER_ID=order_id, ORDER_NO=PREFIX+order['id'],
                                               CUSTOMER_ID=-980701, WARE_ID=WARE_ID, STATUS='DRAFT',
                                               SOURCE_SYSTEM='DS-BASE', CREATED_AT=start, CREATED_BY='DS-BASE'))
        rows['RRL_CUSTOMER_ORDER_ROW'].append(dict(CUSTOMER_ORDER_ROW_ID=order_id,
                                                   CUSTOMER_ORDER_ID=order_id, LINE_NO=10,
                                                   ARTICUL=PREFIX+order['sku'], UNIT_CODE='PCS',
                                                   ORDER_QTY=Decimal(order['boxes'])*24,
                                                   PACK_COUNT=Decimal(order['boxes']), STATUS='OPEN',
                                                   CREATED_AT=start, CREATED_BY='DS-BASE', WARE_ID=WARE_ID))
    return rows


def validate_plan(rows: dict[str, list[dict]]) -> None:
    if tuple(rows) != tuple(TABLE_KEYS):
        raise ValueError('Fixture table allowlist mismatch')
    for table, records in rows.items():
        keys = [tuple(row[key] for key in TABLE_KEYS[table]) for row in records]
        if len(keys)!=len(set(keys)):
            raise ValueError(f'Duplicate fixture key: {table}')
    if sum(row['REMAIN'] for row in rows['RRL_REMAINS'])!=Decimal('2400'):
        raise ValueError('Expected 100 boxes / 2400 pieces')
