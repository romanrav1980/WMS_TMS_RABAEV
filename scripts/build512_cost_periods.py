import json
from pathlib import Path
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
d=Path("db/migrations/2026-10-12_ni071_cost_periods");out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_LOG_COST_LINE_GUARD'and TYPE='TRIGGER'order by LINE")
 src="create or replace "+"".join(r[0]for r in q).replace("\r","")+"\n/\n"
 out[str(d/"000_before_guard.sql")]=src
 start=src.index(" if policy_mode='LOADED_UTC'")
 end=src.index(" if :new.RATE_DATE!=expected_day",start)
 src=src[:start]+""" if :new.PERIOD_KEY!=to_char(:new.RATE_DATE,'YYYY-MM-DD')then raise_application_error(-20886,'COST_EXPLICIT_PERIOD_KEY_REQUIRED');end if;
 select count(*)into n from RRL_LOG_COST_SOURCE_CLAIM where LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID
 and COST_CODE=:new.COST_CODE and CURRENCY=:new.CURRENCY and OPERATION_ID=:new.OPERATION_ID;
 if n!=1 then raise_application_error(-20886,'COST_SINGLE_SOURCE_CLAIM_REQUIRED');end if;
 if policy_mode='LOADED_UTC'then
  expected_day:=loaded_day;
  select count(*)into n from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID;
 else
  select count(*)into n
  from RRL_TT_LOAD_BOX_WEIGHT b join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=b.CASE_BOX_TASK_ID
  and t.WARE_ID=ware and t.STARTED_AT_INSTANT is not null
  join json_table(archive_body,'$.nodes[*]'columns(UID_VALUE varchar2(160)path '$.uid',KIND_VALUE varchar2(20)path '$.kind',CASE_ID number path '$.case_task_id'))j
  on j.UID_VALUE=b.BOX_UID and j.KIND_VALUE='CASE'and j.CASE_ID=t.CASE_PICK_TASK_ID
  where b.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID;
  select count(*)into latest_version from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID;
  if n!=latest_version then raise_application_error(-20886,'COST_EACH_CASE_ACTUAL_START_REQUIRED');end if;
  select count(*)into n from RRL_TT_LOAD_BOX_WEIGHT b join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=b.CASE_BOX_TASK_ID
  and t.WARE_ID=ware and t.STARTED_AT_INSTANT is not null
  where b.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID
  and trunc(cast(t.STARTED_AT_INSTANT at time zone(policy_zone)as timestamp))=:new.RATE_DATE;
  expected_day:=case when n>0 then :new.RATE_DATE else null end;
 end if;
 if n!=:new.QUANTITY then raise_application_error(-20886,'COST_PERIOD_PHYSICAL_BOX_COUNT_REQUIRED');end if;
 select VERSION_NO into latest_version from RRL_LOG_COST_PERIOD_HEAD where WARE_ID=ware;
""" +src[end:]
 old=" and :new.QUANTITY=(select count(*)from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID)"
 assert old in src;src=src.replace(old,"")
 # Native rows must match every frozen monetary value, not merely the date.
 src=src.replace("POLICY_VERSION number path '$.period_policy_version'", "POLICY_VERSION number path '$.period_policy_version',QTY number path '$.quantity',RATE_KEY_VALUE varchar2(64)path '$.rate_key',RATE_VERSION number path '$.version',RATE_NUMBER number path '$.rate',AMOUNT_NUMBER number path '$.amount'")
 src=src.replace("and j.POLICY_VERSION=latest_version;","and j.POLICY_VERSION=latest_version and j.QTY=:new.QUANTITY and j.RATE_KEY_VALUE=:new.RATE_KEY and j.RATE_VERSION=:new.VERSION_NO and j.RATE_NUMBER=:new.RATE_VALUE and j.AMOUNT_NUMBER=:new.AMOUNT;")
 out[str(d/"003_guard.sql")]=src
out[str(d/"001_schema.sql")]="""-- Existing recognised rows, including unknown legacy dates, remain untouched.
begin execute immediate 'alter table RRL_LOGISTICS_COST_LINE add PERIOD_KEY varchar2(10) default ''LEGACY'' not null';
exception when others then if sqlcode!=-1430 then raise;end if;end;
/
begin execute immediate q'[create table RRL_LOG_COST_SOURCE_CLAIM(
 LOAD_OPERATION_ID varchar2(100)not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 COST_CODE varchar2(40)not null,CURRENCY varchar2(3)not null,
 OPERATION_ID varchar2(100)not null references RRL_LOGISTICS_COST_RUN(OPERATION_ID),
 primary key(LOAD_OPERATION_ID,COST_CODE,CURRENCY),
 unique(LOAD_OPERATION_ID,COST_CODE,CURRENCY,OPERATION_ID))]';
exception when others then if sqlcode!=-955 then raise;end if;end;
/
insert into RRL_LOG_COST_SOURCE_CLAIM(LOAD_OPERATION_ID,COST_CODE,CURRENCY,OPERATION_ID)
 select distinct l.LOAD_OPERATION_ID,l.COST_CODE,l.CURRENCY,l.OPERATION_ID from RRL_LOGISTICS_COST_LINE l
 where not exists(select 1 from RRL_LOG_COST_SOURCE_CLAIM s where s.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID and s.COST_CODE=l.COST_CODE and s.CURRENCY=l.CURRENCY);
commit;
/
declare n number;begin
 for k in(select CONSTRAINT_NAME,CONSTRAINT_TYPE from USER_CONSTRAINTS where TABLE_NAME='RRL_LOGISTICS_COST_LINE'and CONSTRAINT_TYPE in('P','U'))loop
  select count(*)into n from ALL_CONSTRAINTS where CONSTRAINT_TYPE='R'and R_OWNER=user and R_CONSTRAINT_NAME=k.CONSTRAINT_NAME;
  if n!=0 then raise_application_error(-20886,'COST_LINE_EXTERNAL_KEY_DEPENDENCY');end if;
  execute immediate 'alter table RRL_LOGISTICS_COST_LINE drop constraint '||dbms_assert.simple_sql_name(k.CONSTRAINT_NAME);
 end loop;
 execute immediate 'alter table RRL_LOGISTICS_COST_LINE add constraint RRL_LOG_COST_PERIOD_PK primary key(OPERATION_ID,LOAD_OPERATION_ID,COST_CODE,PERIOD_KEY)';
 execute immediate 'alter table RRL_LOGISTICS_COST_LINE add constraint RRL_LOG_COST_PERIOD_UQ unique(LOAD_OPERATION_ID,COST_CODE,CURRENCY,PERIOD_KEY)';
 execute immediate 'alter table RRL_LOGISTICS_COST_LINE add constraint RRL_LOG_COST_SOURCE_FK foreign key(LOAD_OPERATION_ID,COST_CODE,CURRENCY,OPERATION_ID)references RRL_LOG_COST_SOURCE_CLAIM(LOAD_OPERATION_ID,COST_CODE,CURRENCY,OPERATION_ID)';
end;
/
"""
out[str(d/"002_claim_guard.sql")]="""create or replace trigger RRL_LOG_COST_CLAIM_GUARD before insert or update or delete on RRL_LOG_COST_SOURCE_CLAIM for each row
declare body clob;n number;quantity number;physical number;distinct_days number;currency_value varchar2(3);
begin
 if not inserting then raise_application_error(-20863,'COST_SOURCE_CLAIM_IMMUTABLE');end if;
 select r.RESULT_JSON,r.CURRENCY into body,currency_value from RRL_LOGISTICS_COST_RUN r
 join RRL_TT_HU_LOAD_FACT l on l.TT_ID=r.TT_ID and l.WARE_ID=r.WARE_ID
 join RRL_STOCK_OPERATION op on op.OPERATION_ID=l.LOAD_OPERATION_ID and op.STATE='APPLIED'
 where r.OPERATION_ID=:new.OPERATION_ID and l.LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and l.STATUS='DEPARTED';
 if currency_value!=:new.CURRENCY or :new.COST_CODE!='WAREHOUSE_PICKING'then raise_application_error(-20886,'COST_SOURCE_CLAIM_SCOPE_REQUIRED');end if;
 select count(*),sum(j.QTY),count(distinct j.RATE_DAY)into n,quantity,distinct_days
 from json_table(body,'$.lines[*]'columns(LOAD_ID varchar2(100)path '$.load_operation_id',QTY number path '$.quantity',RATE_DAY varchar2(10)path '$.rate_date',CODE varchar2(40)path '$.cost_code'))j
 where j.LOAD_ID=:new.LOAD_OPERATION_ID and j.CODE=:new.COST_CODE;
 select count(*)into physical from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID;
 if n=0 or n>200 or distinct_days!=n or quantity!=physical or physical=0 then raise_application_error(-20886,'COST_COMPLETE_SOURCE_PERIOD_PARTITION_REQUIRED');end if;
exception when no_data_found then raise_application_error(-20886,'COST_SOURCE_CLAIM_FACT_REQUIRED');
end;
/
"""
out[str(d/"004_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-512-warehouse-cost-period-partition' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'BOX recognition partitioned by actual CASE date; one immutable source claim; legacy rows preserved',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
out[str(d/"apply.sql")]="@@001_schema.sql\n@@002_claim_guard.sql\n@@003_guard.sql\n@@004_ledger.sql\n"
out[str(d/"rollback.sql")]="""-- Forward repair is required after multiple-period costs. Never delete recognised history.
declare n number;begin
 select count(*)into n from(select LOAD_OPERATION_ID,COST_CODE,CURRENCY from RRL_LOGISTICS_COST_LINE group by LOAD_OPERATION_ID,COST_CODE,CURRENCY having count(*)>1);
 if n!=0 then raise_application_error(-20886,'COST_MULTIPERIOD_FORWARD_REPAIR_REQUIRED');end if;
end;
/
alter table RRL_LOGISTICS_COST_LINE drop constraint RRL_LOG_COST_SOURCE_FK;
alter table RRL_LOGISTICS_COST_LINE drop constraint RRL_LOG_COST_PERIOD_PK;
alter table RRL_LOGISTICS_COST_LINE drop constraint RRL_LOG_COST_PERIOD_UQ;
alter table RRL_LOGISTICS_COST_LINE add primary key(OPERATION_ID,LOAD_OPERATION_ID,COST_CODE);
alter table RRL_LOGISTICS_COST_LINE add unique(LOAD_OPERATION_ID,COST_CODE,CURRENCY);
drop trigger RRL_LOG_COST_CLAIM_GUARD;
drop table RRL_LOG_COST_SOURCE_CLAIM;
alter table RRL_LOGISTICS_COST_LINE drop column PERIOD_KEY;
@@000_before_guard.sql
-- Restore Python/UI/summary together; no monetary or quantity facts are removed.
"""
p=Path("api/wms_api_server/app/modules/finance/infrastructure/box_costs.py");v=p.read_text(encoding="utf-8")
v=v.replace("from .period_policy import current_policy","from .period_policy import current_policy\nfrom .cost_period_lines import load_period_lines")
a=v.index('                if policy["period_mode"]=="CASE_ASSEMBLY":');b=v.index('            result=',a)
v=v[:a]+"""                period_lines=load_period_lines(cur,tree,int(boxes),load,day,ware,currency,policy)
                lines.extend(period_lines)
                total+=sum((Decimal(line["amount"])for line in period_lines),Decimal(0))
""" +v[b:]
a=v.index("            for line in lines:")
v=v[:a]+"""            for load in sorted({line["load_operation_id"]for line in lines}):
                cur.execute("insert into RRL_LOG_COST_SOURCE_CLAIM(LOAD_OPERATION_ID,COST_CODE,CURRENCY,OPERATION_ID)values(:load_id,'WAREHOUSE_PICKING',:currency,:op)",load_id=load,currency=currency,op=op)
""" +v[a:]
v=v.replace("PERIOD_POLICY_VERSION)values(", "PERIOD_POLICY_VERSION,PERIOD_KEY)values(")
v=v.replace(":period_version)\",", ":period_version,:period_key)\",")
v=v.replace('"period_version":line["period_policy_version"]}', '"period_version":line["period_policy_version"],"period_key":line["rate_date"]}')
v=v.replace("from ..domain.amount import cost_amount\n","")
out[str(p)]=v
out["api/wms_api_server/app/modules/finance/infrastructure/cost_period_lines.py"]=r"""# Partition one physical load using existing immutable CASE start evidence.
from collections import Counter
from decimal import Decimal
from typing import Any
from ..contracts import LogisticsCostError
from ..domain.amount import cost_amount


def load_period_lines(cursor: Any, tree: dict[str,Any], boxes: int, load: str, loaded_day: str,
                      ware: int, currency: str, policy: dict[str,Any])->list[dict[str,Any]]:
    counts=Counter({loaded_day:boxes})
    if policy["period_mode"]=="CASE_ASSEMBLY":
        case_ids=sorted({int(n["case_task_id"])for n in tree.get("nodes",[])
                         if n.get("kind")=="CASE"and n.get("case_task_id")is not None})
        if len(case_ids)!=boxes or not 1<=boxes<=200:
            raise LogisticsCostError("COST_ASSEMBLY_SOURCE_REQUIRED","Каждой коробке нужен собственный источник начала CASE")
        binds={f"case{i}":value for i,value in enumerate(case_ids)}
        binds.update(region=policy["timezone_region"],ware=ware)
        cursor.execute("select CASE_PICK_TASK_ID,to_char(STARTED_AT_INSTANT at time zone(:region),'YYYY-MM-DD')from RRL_CASE_PICK_TASK where WARE_ID=:ware and CASE_PICK_TASK_ID in("+",".join(":case"+str(i)for i in range(len(case_ids)))+")",binds)
        dates=cursor.fetchall()
        if len(dates)!=boxes or any(date is None for _,date in dates):
            raise LogisticsCostError("COST_ACTUAL_ASSEMBLY_START_REQUIRED","Нет достоверного момента начала каждой коробки")
        counts=Counter(date for _,date in dates)
    # Rate revisions cannot cross a single source calculation while its history is selected.
    cursor.execute("select RATE_KEY from RRL_LOGISTICS_RATE_HEAD where WARE_ID=:ware and CURRENCY=:currency and COST_CODE='WAREHOUSE_PICKING'for update",ware=ware,currency=currency)
    if not cursor.fetchone():
        raise LogisticsCostError("COST_RATE_MISSING","На подтверждённую расчётную дату нет ставки")
    lines=[]
    for day,quantity in sorted(counts.items()):
        cursor.execute("select h.RATE_KEY,h.VERSION_NO,to_char(h.RATE_VALUE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') "
        "from RRL_LOGISTICS_RATE_HISTORY h join RRL_LOGISTICS_RATE_HEAD r on r.RATE_KEY=h.RATE_KEY "
        "        where r.WARE_ID=:ware and r.CURRENCY=:currency and r.COST_CODE='WAREHOUSE_PICKING' "
        "        and h.EFFECTIVE_FROM<=to_date(:day,'FXYYYY-MM-DD') "
        "        order by h.EFFECTIVE_FROM desc,h.VERSION_NO desc fetch first 1 row only",ware=ware,currency=currency,day=day)
        rate=cursor.fetchone()
        if not rate:
            raise LogisticsCostError("COST_RATE_MISSING","На подтверждённую расчётную дату нет ставки")
        amount=cost_amount(quantity,Decimal(str(rate[2])))
        lines.append({"load_operation_id":load,"rate_key":rate[0],"version":int(rate[1]),"quantity":quantity,
                      "rate":str(rate[2]),"amount":str(amount),"basis":"BOX","cost_code":"WAREHOUSE_PICKING",
                      "rate_date_utc":day if policy["period_mode"]=="LOADED_UTC"else None,"rate_date":day,
                      "period_mode":policy["period_mode"],"period_timezone":policy["timezone_region"],
                      "period_policy_version":policy["version"]})
    return lines
"""
p=Path("api/wms_api_server/app/modules/finance/domain/cost_summary.py");v=p.read_text(encoding="utf-8")
v=v.replace('set[tuple[str,str,str,str]]','set[tuple[str,...]]').replace('("operation_id","load_operation_id","cost_code","currency"))','("operation_id","load_operation_id","cost_code","currency","rate_date"))')
out[str(p)]=v
p=Path("admin/wms_admin_frontend/src/features/finance/BillingWarehouseCosts.tsx");v=p.read_text(encoding="utf-8")
v=v.replace('key={r.operation_id+":"+r.load_operation_id}','key={r.operation_id+":"+r.load_operation_id+":"+r.cost_code+":"+r.currency+":"+r.rate_date}')
out[str(p)]=v
p=Path("api/wms_api_server/app/modules/finance/infrastructure/logistics_costs.py");v=p.read_text(encoding="utf-8")
v=v.replace("order by l.TT_ID,c.LOAD_OPERATION_ID fetch","order by l.TT_ID,c.LOAD_OPERATION_ID,c.RATE_DATE fetch")
out[str(p)]=v
print(json.dumps(out))
