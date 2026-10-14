from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/finance/infrastructure/shipping_register.py");s=p.read_text(encoding="utf-8").replace("from typing import Any","from typing import Any\nfrom datetime import timedelta\nimport json\nimport oracledb")
s=s.replace('cur.execute("""select p.ID,p.ST_NUMBER','cur.execute("""with candidate_ids as(\n            select ID from RRL_SBORKA_PALLETS where WARE_ID=:ware and ID>:after_id and STDATE>=:business_day and STDATE<:day_end\n            union all\n            select p.ID from RRL_SBORKA_PALLETS p join RRL_TRANSPORT_TASK t on t.ID=p.TRANSTASK_ID\n            where p.WARE_ID=:ware and p.ID>:after_id and p.STDATE is null and t.SHIPMENT_DATE>=:business_day and t.SHIPMENT_DATE<:day_end),\n            bounded as(select ID from candidate_ids order by ID fetch first :page_limit rows only)\n            select /* SHIPPING_MEMBER_BOUNDED275 */ p.ID,p.ST_NUMBER',1)
s=s.replace('from RRL_SBORKA_PALLETS p left join RRL_TRANSPORT_TASK','from bounded b join RRL_SBORKA_PALLETS p on p.ID=b.ID left join RRL_TRANSPORT_TASK',1)
s=s.replace('            where p.WARE_ID=:ware and p.ID>:after_id and trunc(coalesce(p.STDATE,t.SHIPMENT_DATE))=:business_day\n            order by p.ID fetch first :page_limit rows only','            order by p.ID',1)
s=s.replace('business_day=day,page_limit=limit+1)','business_day=day,day_end=day+timedelta(days=1),page_limit=limit+1)',1)
start=s.index('        cur.execute("""with declared')
end=s.index('        return {"warehouse_id"',start)
s=s[:start]+'''        cur.execute("""select CELL from(
            select c.CELL from RRL_CELLS c where c.WARE_ID=:ware and c.EXPEDITION_GROUP is not null
            union
            select c.CELL from RRL_TOPOLOGY_CELL tc join RRL_CELLS c on c.CELL=tc.LEGACY_CELL_CODE and c.WARE_ID=tc.WARE_ID
            where tc.WARE_ID=:ware and tc.ACTIVE=1 and tc.CELL_KIND in('TRANSPORT_STAGING','GATE')
            and tc.TOPOLOGY_ID=(select max(TOPOLOGY_ID)from RRL_WAREHOUSE_TOPOLOGY where WARE_ID=:ware and STATUS='PUBLISHED'))
            order by CELL fetch first 501 rows only""",ware=ware)
        codes=[row[0]for row in cur.fetchall()]
        if len(codes)>500:raise LogisticsCostError("SHIPPING_REGISTER_CELL_BOUND_500","Слишком много ячеек грузовой зоны.",409)
        occupancy=[]
        if codes:
            payload=cur.var(oracledb.DB_TYPE_CLOB);payload.setvalue(0,json.dumps(codes))
            # Predicate exactly matches the already installed sparse container-cell index178.
            cur.execute("""with declared as(select CELL from json_table(:cell_codes,'$[*]'columns(CELL varchar2(50)path '$'))),
                facts as(
                  select /*+ leading(d r) use_nl(r) */ d.CELL,'STOCK'kind,count(*)cnt from declared d join RRL_REMAINS r on r.CELL=d.CELL where r.REMAIN>0 group by d.CELL
                  union all
                  select /*+ leading(d p) use_nl(p) */ d.CELL,'CONTAINER',count(*)from declared d join RRL_PALLETS p
                    on case when p.HU_KIND='CONTAINER'then p.HU_CURRENT_CELL end=d.CELL where p.HU_SHIPPED_OPERATION is null group by d.CELL
                  union all
                  select d.CELL,'CASE',count(*)from declared d join RRL_CASE_PICK_TASK t on t.CURRENT_CELL=d.CELL
                    where t.WARE_ID=:ware and t.SHIPPED_OPERATION is null and t.STATUS not in('SHIPPED','CANCELLED','RETURNED')group by d.CELL)
                select /* SHIPPING_CELL_BOUNDED275 */ d.CELL,
                  nvl(sum(case when f.kind='STOCK'then f.cnt end),0),
                  nvl(sum(case when f.kind='CONTAINER'then f.cnt end),0),
                  nvl(sum(case when f.kind='CASE'then f.cnt end),0)
                from declared d left join facts f on f.CELL=d.CELL group by d.CELL order by d.CELL""",cell_codes=payload,ware=ware)
            occupancy=[{"cell":r[0],"positive_quantity_rows":r[1],"unshipped_container_rows":r[2],"unshipped_case_rows":r[3],
                "occupied":any(value>0 for value in r[1:])}for r in cur.fetchall()]
''' +s[end:]
out[str(p)]=s
out["db/migrations/2026-10-11_ni072_shipping_register/001_index.sql"]="""create index RRL_ST_WARE_DAY_ID_I on RRL_SBORKA_PALLETS(WARE_ID,STDATE,ID);
"""
out["db/migrations/2026-10-11_ni072_shipping_register/rollback.sql"]="drop index RRL_ST_WARE_DAY_ID_I;\n"
print(json.dumps(out,ensure_ascii=True))
