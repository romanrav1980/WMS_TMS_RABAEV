from decimal import Decimal
from .configuration_uow import configuration_transaction
from ....oracle_gateway import OracleGateway


class ReceiptConfiguration:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def get(self, warehouse: int) -> dict:
        rows = self.gateway.fetch_all('select * from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=:w', {'w': warehouse})
        return rows[0] if rows else {'ware_id': warehouse, 'company_prefix': None, 'extension_digit': 0, 'coordinate_unit_m': 1, 'reachtruck_mps': 1, 'lift_mps': 0.5, 'placement_metric': 'DISTANCE','outgoing_qc_mode':None,'outgoing_qc_independent':0,'outgoing_qc_sample_percent':0}

    def read_rule(self, warehouse: int, key: str, kind: str) -> dict:
        if kind == "sku":
            rows = self.gateway.fetch_all('select * from RRL_RECEIPT_SKU_RULE where WARE_ID=:w and ARTICUL=:k', {'w': warehouse, 'k': key})
        else:
            rows = self.gateway.fetch_all('select * from RRL_RECEIPT_CELL_RULE where WARE_ID=:w and CELL=:k', {'w': warehouse, 'k': key})
        return rows[0] if rows else {"configured": False}

    def save(self, warehouse: int, body: dict, actor: str) -> dict:
        with configuration_transaction(self.gateway, 'NI01 configure receiving warehouse', actor, 'warehouse_settings_edit') as cur:
            cur.execute('select count(*) from RRL_WARES where ID=:w', {'w': warehouse})
            if cur.fetchone()[0] != 1:
                raise LookupError('Warehouse not found')
            cur.execute('merge into RRL_RECEIPT_WARE_SETTINGS d using(select :w WARE_ID from dual)s on(d.WARE_ID=s.WARE_ID) when matched then update set COMPANY_PREFIX=:prefix,EXTENSION_DIGIT=:ext,COORDINATE_UNIT_M=:unit,REACHTRUCK_MPS=:speed,LIFT_MPS=:lift,PLACEMENT_METRIC=:metric,HU_CELL_HEIGHT_UNIT=case when :hu_set=1 then :hu_unit else d.HU_CELL_HEIGHT_UNIT end,UPDATED_BY=:actor,UPDATED_AT=systimestamp when not matched then insert(WARE_ID,COMPANY_PREFIX,EXTENSION_DIGIT,COORDINATE_UNIT_M,REACHTRUCK_MPS,LIFT_MPS,PLACEMENT_METRIC,HU_CELL_HEIGHT_UNIT,UPDATED_BY) values(:w,:prefix,:ext,:unit,:speed,:lift,:metric,:hu_unit,:actor)', {'w': warehouse, 'prefix': body['company_prefix'], 'ext': body['extension_digit'], 'unit': body['coordinate_unit_m'], 'speed': body['reachtruck_mps'], 'lift': body['lift_mps'], 'metric': body['placement_metric'], 'hu_set': int('hu_cell_height_unit' in body), 'hu_unit': body.get('hu_cell_height_unit'), 'actor': actor})
            if "defer_wait_cell" in body:
                cur.execute("update RRL_RECEIPT_WARE_SETTINGS set DEFER_WAIT_CELL=:cell where WARE_ID=:w", {"cell": body["defer_wait_cell"], "w": warehouse})
            if "outgoing_qc_mode" in body:
                cur.execute("update RRL_RECEIPT_WARE_SETTINGS set OUTGOING_QC_MODE=:p_qc_mode where WARE_ID=:w",{"p_qc_mode":body["outgoing_qc_mode"],"w":warehouse})
            if "outgoing_qc_independent" in body:
                cur.execute("update RRL_RECEIPT_WARE_SETTINGS set OUTGOING_QC_INDEPENDENT=:p_independent where WARE_ID=:w",{"p_independent":int(bool(body["outgoing_qc_independent"])),"w":warehouse})
            if "outgoing_qc_sample_percent" in body:
                cur.execute("update RRL_RECEIPT_WARE_SETTINGS set OUTGOING_QC_SAMPLE_PERCENT=:p_percent where WARE_ID=:w",{"p_percent":Decimal(str(body["outgoing_qc_sample_percent"] or 0)),"w":warehouse})
        return self.get(warehouse)

    def sku_rule(self, warehouse: int, articul: str, body: dict, actor: str = "API") -> dict:
        with configuration_transaction(self.gateway, 'NI01 configure warehouse SKU receiving rule', actor, 'warehouse_settings_edit') as cur:
            cur.execute('select count(*) from RRL_ARTICULS where ACTICUL=:a', {'a': articul})
            if cur.fetchone()[0] != 1:
                raise LookupError('Article missing or ambiguous')
            cur.execute('select count(*) from RRL_CELLS where WARE_ID=:w and CELL=:c and OTBOR=1', {'w': warehouse, 'c': body['pick_cell']})
            if cur.fetchone()[0] != 1:
                raise ValueError('Configure an existing picking cell of this warehouse')
            cur.execute('merge into RRL_RECEIPT_SKU_RULE d using(select :w WARE_ID,:a ARTICUL from dual)s on(d.WARE_ID=s.WARE_ID and d.ARTICUL=s.ARTICUL) when matched then update set PICK_CELL=:c,TEMP_MIN=:lo,TEMP_MAX=:hi,MIN_SHELF_DAYS=:days,SOURCE_PICK_MODE=:source_mode,ALLOW_PICK_BATCH_MIX=nvl(:mix,d.ALLOW_PICK_BATCH_MIX) when not matched then insert(WARE_ID,ARTICUL,PICK_CELL,TEMP_MIN,TEMP_MAX,MIN_SHELF_DAYS,SOURCE_PICK_MODE,ALLOW_PICK_BATCH_MIX) values(:w,:a,:c,:lo,:hi,:days,:source_mode,nvl(:mix,0))', {'w': warehouse, 'a': articul, 'c': body['pick_cell'], 'lo': body['temp_min'], 'hi': body['temp_max'], 'days': body['min_shelf_days'], 'source_mode': body.get('source_pick_mode', 'AFTER_PUTAWAY'), 'mix': None if body.get('allow_pick_batch_mix') is None else int(body['allow_pick_batch_mix'])})
        return {'warehouse_id': warehouse, 'articul': articul, **body}

    def cell_rule(self, warehouse: int, cell: str, body: dict, actor: str) -> dict:
        with configuration_transaction(self.gateway, 'NI01 configure storage temperature and replenishment time', actor, 'warehouse_settings_edit') as cur:
            cur.execute('select count(*) from RRL_CELLS where WARE_ID=:w and CELL=:c', {'w': warehouse, 'c': cell})
            if cur.fetchone()[0] != 1:
                raise LookupError('Warehouse cell not found')
            cur.execute('merge into RRL_RECEIPT_CELL_RULE d using(select :w WARE_ID,:c CELL from dual)s on(d.WARE_ID=s.WARE_ID and d.CELL=s.CELL) when matched then update set TEMP_MIN=:lo,TEMP_MAX=:hi when not matched then insert(WARE_ID,CELL,TEMP_MIN,TEMP_MAX) values(:w,:c,:lo,:hi)', {'w': warehouse, 'c': cell, 'lo': body['temp_min'], 'hi': body['temp_max']})
            if body.get('travel_sec') is not None:
                cur.execute('select count(*) from RRL_CELLS where WARE_ID=:w and CELL=:p and OTBOR=1', {'w': warehouse, 'p': body['pick_cell']})
                if cur.fetchone()[0] != 1:
                    raise ValueError('Travel-time destination must be warehouse picking cell')
                cur.execute('merge into RRL_RECEIPT_TRAVEL_TIME d using(select :w WARE_ID,:c CELL,:p PICK_CELL from dual)s on(d.WARE_ID=s.WARE_ID and d.CELL=s.CELL and d.PICK_CELL=s.PICK_CELL) when matched then update set TRAVEL_SEC=:t,BASIS=:b,UPDATED_BY=:a,UPDATED_AT=systimestamp when not matched then insert(WARE_ID,CELL,PICK_CELL,TRAVEL_SEC,BASIS,UPDATED_BY) values(:w,:c,:p,:t,:b,:a)', {'w': warehouse, 'c': cell, 'p': body['pick_cell'], 't': body['travel_sec'], 'b': body['basis'], 'a': actor})
        return {'warehouse_id': warehouse, 'cell': cell, **body}
