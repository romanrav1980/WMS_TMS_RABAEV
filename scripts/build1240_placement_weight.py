from pathlib import Path
import json
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/placement.py");s=p.read_text(encoding="utf-8")
a=s.index('        cur.execute("""select c.CELL,s.CELL_SLOT_ID,')
b=s.index('          case when :metric=',a)
s=s[:a]+'''        cur.execute("""with cell_pallets as (
          select r.CELL,r.UID_POLETA UID_PALLET from RRL_REMAINS r
            join RRL_CELLS rc on rc.CELL=r.CELL where rc.WARE_ID=:w and r.REMAIN>0
          union
          select wt.TO_CELL,wt.UID_PALLET from RRL_WAREHOUSE_TASK wt
            join RRL_CELLS tc on tc.CELL=wt.TO_CELL where tc.WARE_ID=:w and wt.STATUS not in('DONE','CANCELLED')
        ), cell_load as (
          select cp.CELL,sum(p.WEIGHT_BRUTTO) WEIGHT_KG,
            sum(case when p.WEIGHT_BRUTTO is null then 1 else 0 end) UNKNOWN_WEIGHTS
          from cell_pallets cp join RRL_PALLETS p on p.UID_PALLET=cp.UID_PALLET group by cp.CELL
        )
        select c.CELL,s.CELL_SLOT_ID,
'''+s[b:]
s=s.replace('          from RRL_CELLS c left join RRL_RECEIPT_CELL_RULE','          from RRL_CELLS c left join cell_load cload on cload.CELL=c.CELL\n          left join RRL_RECEIPT_CELL_RULE',1)
a=s.index('              and not exists(select 1 from RRL_REMAINS r join RRL_PALLETS')
b=s.index('            and (nvl(c.LIMIT_HEIGHT',a)
s=s[:a]+'''              and nvl(cload.UNKNOWN_WEIGHTS,0)=0
              and :weight+nvl(cload.WEIGHT_KG,0)<=c.LIMIT_WEIGHT))
'''+s[b:]
a=s.index('            cur.execute("""select nvl(sum(p.WEIGHT_BRUTTO),0)')
b=s.index('            load, unknown =',a)
s=s[:a]+'''            cur.execute("""select nvl(sum(p.WEIGHT_BRUTTO),0),nvl(sum(case when p.WEIGHT_BRUTTO is null then 1 else 0 end),0)
              from (
                select r.UID_POLETA UID_PALLET from RRL_REMAINS r where r.CELL=:c and r.REMAIN>0
                union
                select wt.UID_PALLET from RRL_WAREHOUSE_TASK wt where wt.TO_CELL=:c and wt.STATUS not in('DONE','CANCELLED')
              ) current_pallets join RRL_PALLETS p on p.UID_PALLET=current_pallets.UID_PALLET
              where p.UID_PALLET<>:p""", {'p': receipt['pallet_identifier'], 'c': cell})
'''+s[b:]
print(json.dumps({str(p):s},ensure_ascii=True))
