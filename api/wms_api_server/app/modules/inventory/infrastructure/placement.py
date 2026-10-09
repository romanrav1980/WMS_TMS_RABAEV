import oracledb
"""Placement scoring uses configured replenishment time or coordinates, with slot claims."""
from datetime import date
from decimal import Decimal


class ReceiptPlacement:
    def __init__(self, cursor: oracledb.Cursor) -> None:
        self.cur = cursor

    def choose(self, warehouse: int, receiving: str, articul: str, payload: dict) -> dict:
        cur = self.cur
        cur.execute('select p.X,p.Y,p.Z,p.CELL,r.TEMP_MIN,r.TEMP_MAX,nvl(r.MIN_SHELF_DAYS,0) from RRL_ARTICULS a left join RRL_RECEIPT_SKU_RULE r on r.ARTICUL=a.ACTICUL and r.WARE_ID=:w join RRL_CELLS p on p.CELL=nvl(r.PICK_CELL,a.CELL) where a.ACTICUL=:a and p.WARE_ID=:w and p.OTBOR=1 and p.X<>10000 and p.Y<>10000 and p.Z<>10000', {'a': articul, 'w': warehouse})
        rows = cur.fetchall()
        if len(rows) != 1:
            raise ValueError('Configure picking cell and coordinates in recipient warehouse')
        pick = rows[0]
        if (date.fromisoformat(payload['expiry_date'])-date.today()).days < pick[6]:
            raise ValueError('Insufficient remaining shelf life for warehouse SKU rule')
        cur.execute('select PLACEMENT_METRIC,COORDINATE_UNIT_M,REACHTRUCK_MPS,LIFT_MPS from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=:w', {'w': warehouse})
        settings = cur.fetchone() or ('DISTANCE', 1, 1, .5)
        cur.execute("""select c.CELL,s.CELL_SLOT_ID,
          case when :metric='TIME' then nvl(t.TRAVEL_SEC,((abs(c.X-:x)+abs(c.Y-:y))*:scale/:speed+abs(c.Z-:z)*:scale/:lift))
            else abs(c.X-:x)+abs(c.Y-:y)+abs(c.Z-:z) end SCORE,
          case when :metric='TIME' then nvl(t.BASIS,'NORMATIVE') else 'COORDINATE_DISTANCE' end BASIS
          from RRL_CELLS c left join RRL_RECEIPT_CELL_RULE cr on cr.WARE_ID=c.WARE_ID and cr.CELL=c.CELL
          left join RRL_RECEIPT_TRAVEL_TIME t on t.WARE_ID=c.WARE_ID and t.CELL=c.CELL and t.PICK_CELL=:pick
          left join RRL_TOPOLOGY_CELL tc on tc.LEGACY_CELL_CODE=c.CELL and tc.ACTIVE=1
            and tc.TOPOLOGY_ID=(select max(TOPOLOGY_ID) from RRL_WAREHOUSE_TOPOLOGY where WARE_ID=:w and STATUS='PUBLISHED')
          left join RRL_TOPOLOGY_CELL_SLOT s on s.TOPOLOGY_CELL_ID=tc.TOPOLOGY_CELL_ID and s.ACTIVE=1 and s.SLOT_KIND='STORAGE_SLOT'
          where c.WARE_ID=:w and c.CELL<>:receive and nvl(c.OTBOR,0)=0 and nvl(c.IS_SYSTEM,0)=0
            and nvl(c.BLOCKED_FOR_REMAINS,0)=0 and nvl(c.BLOCKED_FOR_POPOLNENIE,0)=0 and nvl(c.BLOCKED_FOR_ACCEPT,0)=0
            and c.X<>10000 and c.Y<>10000 and c.Z<>10000
            and (nvl(c.LIMIT_WEIGHT,0)=0 or (:weight is not null
              and not exists(select 1 from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where r.CELL=c.CELL and r.REMAIN>0 and p.WEIGHT_BRUTTO is null)
              and not exists(select 1 from RRL_WAREHOUSE_TASK wt join RRL_PALLETS p on p.UID_PALLET=wt.UID_PALLET where wt.TO_CELL=c.CELL and wt.STATUS not in('DONE','CANCELLED') and p.WEIGHT_BRUTTO is null)
              and :weight+nvl((select sum(p.WEIGHT_BRUTTO) from RRL_PALLETS p where exists(select 1 from RRL_REMAINS r where r.UID_POLETA=p.UID_PALLET and r.CELL=c.CELL and r.REMAIN>0)
                or exists(select 1 from RRL_WAREHOUSE_TASK wt where wt.UID_PALLET=p.UID_PALLET and wt.TO_CELL=c.CELL and wt.STATUS not in('DONE','CANCELLED'))),0)<=c.LIMIT_WEIGHT))
            and (nvl(c.LIMIT_HEIGHT,0)=0 or :height<=c.LIMIT_HEIGHT)
            and (nvl(s.CAPACITY_WEIGHT_KG,0)=0 or :weight<=s.CAPACITY_WEIGHT_KG)
            and (nvl(s.HEIGHT_M,0)=0 or :height_m<=s.HEIGHT_M)
            and (nvl(s.CAPACITY_VOLUME_M3,0)=0 or :volume<=s.CAPACITY_VOLUME_M3)
            and (:tmin is null or cr.TEMP_MIN>=:tmin) and (:tmax is null or cr.TEMP_MAX<=:tmax)
            and (s.CELL_SLOT_ID is not null or not exists(select 1 from RRL_REMAINS r where r.CELL=c.CELL and r.REMAIN<>0))
            and not exists(select 1 from RRL_REMAINS r where r.CELL=c.CELL and r.REMAIN<>0
              and not exists(select 1 from RRL_RECEIPT_SLOT_CLAIM cl where cl.CELL=c.CELL and cl.UID_PALLET=r.UID_POLETA and cl.STATUS='OCCUPIED'))
            and not exists(select 1 from RRL_RECEIPT_SLOT_CLAIM cl where cl.CELL_SLOT_ID=s.CELL_SLOT_ID and cl.STATUS in('RESERVED','OCCUPIED'))
            and not exists(select 1 from RRL_WAREHOUSE_TASK wt where wt.TO_CELL=c.CELL and wt.STATUS not in('DONE','CANCELLED')
              and (s.CELL_SLOT_ID is null or wt.TO_CELL_SLOT_ID is null or wt.TO_CELL_SLOT_ID=s.CELL_SLOT_ID))
          order by SCORE,c.CELL,s.CELL_SLOT_ID fetch first 1 row only""",
            {'w': warehouse, 'receive': receiving, 'x': pick[0], 'y': pick[1], 'z': pick[2], 'pick': pick[3], 'tmin': pick[4], 'tmax': pick[5],
             'metric': settings[0], 'scale': settings[1], 'speed': settings[2], 'lift': settings[3],
             'weight': Decimal(str(payload['gross_weight'])) if payload.get('gross_weight') else None,
             'height': Decimal(str(payload['pallet_height'])) if payload.get('pallet_height') else None,
             'height_m': Decimal(str(payload['pallet_height_m'])) if payload.get('pallet_height_m') else None,
             'volume': Decimal(str(payload['volume_m3'])) if payload.get('volume_m3') else None})
        selected = cur.fetchone()
        if not selected:
            raise ValueError('No storage slot satisfies occupancy, limits, temperature and warehouse rules')
        return {'cell': selected[0], 'slot_id': selected[1], 'score': str(selected[2]), 'basis': selected[3], 'metric': settings[0]}

    def validate_target(self, warehouse: int, cell: str, slot: int | None, receipt: dict) -> None:
        cur = self.cur
        measures = receipt.get('physical_measurements', {})
        cur.execute('select c.LIMIT_WEIGHT,c.LIMIT_HEIGHT,cr.TEMP_MIN,cr.TEMP_MAX,r.TEMP_MIN,r.TEMP_MAX,nvl(r.MIN_SHELF_DAYS,0) from RRL_CELLS c left join RRL_RECEIPT_CELL_RULE cr on cr.CELL=c.CELL and cr.WARE_ID=c.WARE_ID left join RRL_RECEIPT_SKU_RULE r on r.WARE_ID=c.WARE_ID and r.ARTICUL=:a where c.CELL=:c and c.WARE_ID=:w', {'c': cell, 'w': warehouse, 'a': receipt['material']})
        rows = cur.fetchall()
        if len(rows)!=1:
            raise ValueError('Storage address is missing/ambiguous')
        row = rows[0]
        self._limit(measures.get('gross_weight'), row[0], 'weight')
        if row[0]:
            cur.execute("""select nvl(sum(p.WEIGHT_BRUTTO),0),nvl(sum(case when p.WEIGHT_BRUTTO is null then 1 else 0 end),0)
              from RRL_PALLETS p where p.UID_PALLET<>:p and (exists(select 1 from RRL_REMAINS r where r.UID_POLETA=p.UID_PALLET and r.CELL=:c and r.REMAIN>0)
                or exists(select 1 from RRL_WAREHOUSE_TASK wt where wt.UID_PALLET=p.UID_PALLET and wt.TO_CELL=:c and wt.STATUS not in('DONE','CANCELLED')))""", {'p': receipt['pallet_identifier'], 'c': cell})
            load, unknown = cur.fetchone()
            if unknown or Decimal(str(load))+Decimal(str(measures['gross_weight']))>Decimal(str(row[0])):
                raise ValueError('Total cell weight including reserved pallets exceeds capacity; replan putaway')
        self._limit(measures.get('pallet_height'), row[1], 'height')
        if row[4] is not None and (row[2] is None or row[2]<row[4] or row[3] is None or row[3]>row[5]):
            raise ValueError('Storage temperature no longer meets SKU rule; replan putaway')
        if (date.fromisoformat(receipt['expiry_date'])-date.today()).days < row[6]:
            raise ValueError('Shelf life no longer meets receiving rule')
        if slot is not None:
            cur.execute('select s.CAPACITY_WEIGHT_KG,s.HEIGHT_M,s.CAPACITY_VOLUME_M3 from RRL_TOPOLOGY_CELL_SLOT s join RRL_TOPOLOGY_CELL tc on tc.TOPOLOGY_CELL_ID=s.TOPOLOGY_CELL_ID where s.CELL_SLOT_ID=:s and s.ACTIVE=1 and tc.LEGACY_CELL_CODE=:c and tc.WARE_ID=:w', {'s': slot, 'c': cell, 'w': warehouse})
            bounds = cur.fetchone()
            if not bounds:
                raise ValueError('Physical storage slot changed; replan putaway')
            for field, limit, title in zip(('gross_weight','pallet_height_m','volume_m3'), bounds, ('slot weight','slot height','slot volume')):
                self._limit(measures.get(field), limit, title)

    @staticmethod
    def _limit(value, maximum, title: str) -> None:
        if maximum and (value is None or Decimal(str(value))>Decimal(str(maximum))):
            raise ValueError('Pallet no longer satisfies ' + title + '; replan putaway')
