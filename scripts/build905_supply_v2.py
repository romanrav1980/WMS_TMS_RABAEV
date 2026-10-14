from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8")
base="api/wms_api_server/app/modules/integrations/"
files={}
p=base+"domain/supply_order.py";t=read(p).replace('"""Assumed gateway contract v1. This is not a claimed SAP standard IDoc type."""','"""Versioned warehouse gateway contract; not a claimed SAP standard IDoc type."""')
t=t.replace('root.get("version") != "1"','root.get("version") not in {"1","2"}').replace('Expected WarehouseSupplyOrder version=1','Expected WarehouseSupplyOrder version=1 or version=2')
t=t.replace('if material in materials:','if root.get("version")=="1" and material in materials:')
t=t.replace('return {"sender": sender,','return {"gateway_contract_version": int(root.get("version")), "sender": sender,')
files[p]=t
p=base+"infrastructure/supply_orders.py";t=read(p)
start=t.index('        for line in lines:',t.index('    def _lines('));end=t.index('    @staticmethod',start)
t=t[:start]+'''        from .supply_line_writer import SupplyLineWriter
        SupplyLineWriter(cur).write(order_id,naklad_id,lines,previous,sender)

'''+t[end:]
t=t.replace('UPDATED_AT=systimestamp','UPDATED_AT=systimestamp,GATEWAY_CONTRACT_VERSION=:cv')
t=t.replace('WARE_ID,RECEIVE_CELL)\n                values','WARE_ID,RECEIVE_CELL,GATEWAY_CONTRACT_VERSION)\n                values')
t=t.replace(':legacy,:r,:h,:w,:c)',':legacy,:r,:h,:w,:c,:cv)')
t=t.replace('"r": order["revision"], "h": order["payload_hash"],','"r": order["revision"], "h": order["payload_hash"], "cv": order["gateway_contract_version"],')
t=t.replace('"revision": order["revision"], "warehouse_id": order["warehouse_id"],','"revision": order["revision"], "warehouse_id": order["warehouse_id"], "gateway_contract_version": order["gateway_contract_version"],')
files[p]=t
files[base+"infrastructure/supply_line_writer.py"]='''"""ERP item lines share the unchanged legacy document/SKU planning row."""
from decimal import Decimal
from typing import Any
from ..application.ingestion import IdocConflict
from ...platform.public import read_oracle_json
from ...inventory.public import convert_sap_source_quantity
from .supply_amendments import SupplyAmendments


class SupplyLineWriter:
    def __init__(self, cursor: Any) -> None:
        self.cur = cursor

    def normalize(self, order: str, lines: list[dict], previous: dict, sender: str) -> list[dict]:
        normalized = []
        for line in lines:
            self.cur.execute("select BASE_UOM,UNITS_JSON,SENDER from RRL_SAP_ARTICLE_META where ARTICUL=:a", a=line["material"])
            master = self.cur.fetchone()
            if not master:
                raise ValueError("Import article via ARTMAS first: "+line["material"])
            if master[2] != sender:
                raise ValueError("Supply article belongs to another SAP sender")
            self.cur.execute("select ACTICUL from RRL_ARTICULS where ACTICUL=:a", a=line["material"])
            if len(self.cur.fetchall()) != 1:
                raise ValueError("Article missing or ambiguous in legacy master")
            old = previous.get(line["line_number"])
            if old and old[2] != master[0]:
                raise IdocConflict("Base unit of an existing line is immutable")
            quantity = convert_sap_source_quantity(self.cur,line["material"],line["unit"],line["quantity"],master[0],read_oracle_json(master[1]))
            SupplyAmendments(self.cur).validate_quantity(order,line["line_number"],master[0],quantity)
            normalized.append({**line,"planned":quantity,"base_uom":master[0]})
        return normalized

    def write(self, order: str, document: int, lines: list[dict], previous: dict, sender: str) -> None:
        normalized = self.normalize(order,lines,previous,sender)
        grouped: dict[str,dict] = {}
        for line in normalized:
            group = grouped.setdefault(line["material"],{"quantity":Decimal(0),"base":line["base_uom"]})
            if group["base"] != line["base_uom"]:
                raise IdocConflict("One legacy article row requires one base unit")
            group["quantity"] += line["planned"]
            if group["quantity"] > Decimal("999999999999"):
                raise ValueError("Combined article planned quantity exceeds supported bound")
        for article,group in grouped.items():
            self.cur.execute("select ID from RRL_PRIHOD_NAKLAD_ROWS where ORDID=:d and ARTICUL=:a",d=document,a=article)
            known = self.cur.fetchall()
            if len(known)>1:
                raise IdocConflict("Legacy document article row is ambiguous")
            if known:
                row = known[0][0]
                self.cur.execute("update RRL_PRIHOD_NAKLAD_ROWS set COUNT1=:q where ID=:r",q=group["quantity"],r=row)
            else:
                self.cur.execute("select RRL_PRIHOD_NAKLAD_ROWS_SQ.nextval from dual")
                row = self.cur.fetchone()[0]
                self.cur.execute("insert into RRL_PRIHOD_NAKLAD_ROWS(ID,ORDID,ARTICUL,COUNT1)values(:r,:d,:a,:q)",r=row,d=document,a=article,q=group["quantity"])
            group["row"] = row
        for line in normalized:
            row = grouped[line["material"]]["row"]
            old = previous.get(line["line_number"])
            if old and old[1] != row:
                raise IdocConflict("Existing ERP line legacy row mapping is immutable")
            values = dict(o=order,l=line["line_number"],r=row,a=line["material"],q=line["planned"],u=line["base_uom"],sq=Decimal(line["quantity"]),su=line["unit"])
            if old:
                self.cur.execute("update RRL_SAP_SUPPLY_LINE set PLANNED_QTY=:q,SOURCE_QTY=:sq,SOURCE_UOM=:su where ORDER_ID=:o and LINE_NUMBER=:l",{k:values[k]for k in("q","sq","su","o","l")})
            else:
                self.cur.execute("insert into RRL_SAP_SUPPLY_LINE(ORDER_ID,LINE_NUMBER,ROW_ID,ARTICUL,PLANNED_QTY,BASE_UOM,SOURCE_QTY,SOURCE_UOM)values(:o,:l,:r,:a,:q,:u,:sq,:su)",values)
'''
p=base+"infrastructure/supply_amendments.py";t=read(p)
t=t.replace("cur.execute('delete from RRL_PRIHOD_NAKLAD_ROWS where ID=:r', {'r': row[1]})","cur.execute('delete from RRL_PRIHOD_NAKLAD_ROWS where ID=:r and not exists(select 1 from RRL_SAP_SUPPLY_LINE where ROW_ID=:r)', {'r': row[1]})")
start=t.index('    def validate_quantity(')
t=t[:start]+"""    def validate_quantity(self, order_id: str, line_number: str, base: str, quantity: Decimal) -> None:
        self.cur.execute(\"\"\"select to_char(nvl(sum(POSTED_BASE_QTY),0),'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),
          count(case when POSTED_BASE_QTY is null or STOCK_BASE_UOM is null or STOCK_BASE_UOM!=:u then 1 end)
          from RRL_SAP_PALLET_RECEIPT where ORDER_ID=:i and LINE_NUMBER=:l\"\"\", i=order_id,l=line_number,u=base)
        accepted,invalid = self.cur.fetchone()
        if invalid:
            raise IdocConflict("Received line requires posted base-unit reconciliation")
        if quantity < Decimal(accepted):
            raise IdocConflict('SAP planned quantity cannot be less than already received quantity')

    def refresh_header(self, order_id: str, naklad_id: int) -> None:
        self.cur.execute(\"\"\"select count(*)from RRL_SAP_SUPPLY_LINE l where l.ORDER_ID=:i and
          (l.PLANNED_QTY>(select nvl(sum(r.POSTED_BASE_QTY),0)from RRL_SAP_PALLET_RECEIPT r
             where r.ORDER_ID=l.ORDER_ID and r.LINE_NUMBER=l.LINE_NUMBER)
           or exists(select 1 from RRL_SAP_PALLET_RECEIPT r where r.ORDER_ID=l.ORDER_ID and r.LINE_NUMBER=l.LINE_NUMBER
             and(r.POSTED_BASE_QTY is null or r.STOCK_BASE_UOM is null or r.STOCK_BASE_UOM!=l.BASE_UOM)))\"\"\", i=order_id)
        complete = self.cur.fetchone()[0] == 0
        self.cur.execute('update RRL_PRIHOD_NAKLAD set CONDITION=:c,DATE_OF_ACCEPT=case when :c=1 then nvl(DATE_OF_ACCEPT,sysdate) else null end where ID=:i', {'c': int(complete), 'i': naklad_id})
"""
files[p]=t
mid="2026-10-13-905-ni011-supply-line-v2";d="db/migrations/2026-10-13_ni011_supply_line_v2/"
files[d+"000_before_table.sql"]=read("tmp/904_supply_line_before.sql")
files[d+"001_lines.sql"]="""declare
 n number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20801,'RABAEV/orcl only');end if;
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_SAP_SUPPLY_ORDER'and COLUMN_NAME='GATEWAY_CONTRACT_VERSION';
 if n=0 then execute immediate 'alter table RRL_SAP_SUPPLY_ORDER add(GATEWAY_CONTRACT_VERSION number default 1 not null constraint RRL_SAP_SUP_CONTRACT_CK check(GATEWAY_CONTRACT_VERSION in(1,2)))';end if;
 for x in(select CONSTRAINT_NAME from USER_CONSTRAINTS where TABLE_NAME='RRL_SAP_SUPPLY_LINE'and CONSTRAINT_NAME in('RRL_SAP_SUP_ROW_UK','RRL_SAP_SUP_ART_UK'))loop
  execute immediate 'alter table RRL_SAP_SUPPLY_LINE drop constraint '||x.CONSTRAINT_NAME;
 end loop;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_SAP_SUP_ROW_IX';
 if n=0 then execute immediate 'create index RRL_SAP_SUP_ROW_IX on RRL_SAP_SUPPLY_LINE(ROW_ID)';end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_SAP_SUP_ART_IX';
 if n=0 then execute immediate 'create index RRL_SAP_SUP_ART_IX on RRL_SAP_SUPPLY_LINE(ORDER_ID,ARTICUL)';end if;
end;
/
"""
files[d+"apply.sql"]="@@001_lines.sql\n@@002_ledger.sql\n"
files[d+"002_ledger.sql"]=f"""merge into RRL_SCHEMA_MIGRATIONS t using(select '{mid}'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit gateway v2 item lines with shared unchanged legacy article row; v1 parser unchanged',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
files[d+"rollback.sql"]=f"""declare n number;begin
 select count(*)into n from(select ROW_ID from RRL_SAP_SUPPLY_LINE group by ROW_ID having count(*)>1);
 if n>0 then raise_application_error(-20801,'V2 shared rows exist; reconcile source mapping before rollback, no automatic deletion');end if;
 select count(*)into n from(select ORDER_ID,ARTICUL from RRL_SAP_SUPPLY_LINE group by ORDER_ID,ARTICUL having count(*)>1);
 if n>0 then raise_application_error(-20801,'V2 item lines exist; no destructive rollback');end if;
 execute immediate 'drop index RRL_SAP_SUP_ROW_IX';
 execute immediate 'drop index RRL_SAP_SUP_ART_IX';
 execute immediate 'alter table RRL_SAP_SUPPLY_LINE add constraint RRL_SAP_SUP_ROW_UK unique(ROW_ID)';
 execute immediate 'alter table RRL_SAP_SUPPLY_LINE add constraint RRL_SAP_SUP_ART_UK unique(ORDER_ID,ARTICUL)';
 execute immediate 'alter table RRL_SAP_SUPPLY_ORDER drop column GATEWAY_CONTRACT_VERSION';
end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='{mid}';
/
"""
files[d+"verify.sql"]="select COLUMN_NAME,DATA_DEFAULT,NULLABLE from USER_TAB_COLUMNS where TABLE_NAME='RRL_SAP_SUPPLY_ORDER'and COLUMN_NAME='GATEWAY_CONTRACT_VERSION';\nselect INDEX_NAME,UNIQUENESS,STATUS from USER_INDEXES where TABLE_NAME='RRL_SAP_SUPPLY_LINE';\nselect NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%';\n"
files[d+"checkpoint.json"]=json.dumps({"migration_id":mid,"state":"PREPARED","target":"RABAEV/orcl","before_table_sha256":hashlib.sha256(files[d+"000_before_table.sql"].encode()).hexdigest(),"after_files_sha256":{p:hashlib.sha256(t.encode()).hexdigest()for p,t in files.items()}},indent=2)
files["wiki/database/nicora_ni011_supply_lines_20261013.md"]="""# NI01.1: отдельные строки заказа SAP

905 PREPARED: явный WarehouseSupplyOrder version=2, не стандартный SAP IDoc. ARTMAS10 не меняется. Версия1 сохраняет запрет повторного артикула; версия2 допускает несколько разных LineNumber для одного артикула. Source PK(ORDER_ID,LINE_NUMBER) сохраняется; прежние unique ROW_ID и ORDER_ID/ARTICUL заменяются неуникальными индексами. Зависимых FK на них нет (live904). Старые RRL_PRIHOD_NAKLAD_ROWS UNIQUE(ORDID,ARTICUL) сохраняются: одна строка COUNT1=sum exact base quantities всех source lines, несколько source lines ссылаются на неё. Receipt native CORE/PLAN уже используют order/line; новые пакеты/stock writers не создаются.

Integrations SupplyLineWriter отвечает только за исходный план в существующей supply_transaction/current scope/resource fence. Inventory RRL_STOCK_RECEIPT_CORE остаётся authoritative физической проводкой. Полученное количество/перепланирование/полнота header используют RRL_SAP_PALLET_RECEIPT.POSTED_BASE_QTY по order/line, а не общий document/SKU. Несогласованная base-unit история отклоняется. Принятую строку нельзя удалить/уменьшить ниже её собственного факта; shared legacy row удаляется только без source references.

Capture904 DDL/SHA + [apply/rollback](../../db/migrations/2026-10-13_ni011_supply_line_v2/apply.sql). Rollback отказывается при уже существующих v2 shared rows; их не удаляет. Полного копирования базы нет. Обновление версии контрактов и приложение требуют совместного отката; rollback пока не испытан. Native compile/live fresh business case ожидают.

Противоречие уточнено: case900 version1 отклонён422 до создания документа/остатка. В старом v1 фактического случая дублей SKU не было; нельзя заявлять найденное искажение текущих остатков. Новая возможность позволяет принимать разные позиции одного SKU, учитывая партии паллет как прежде.
"""
files["wiki/index.md"]="- [NI01.1 строки SAP905](database/nicora_ni011_supply_lines_20261013.md): explicit v2/shared canonical legacy SKU row; prepared, live pending.\n"+read("wiki/index.md")
files["wiki/log.md"]=read("wiki/log.md")+"\n- 2026-10-13 prepared905 NI01.1 explicit supply v2 after live constraints904 capture/no referencing FK. Source PK unchanged, legacy document/SKU uniqueness retained, per-line posted receipt ledger, rollback refuses destructive reconciliation. Version1 negative900 correctly rejected before Oracle writes; not an observed inventory distortion. Apply/business proof pending.\n"
print(json.dumps(files,ensure_ascii=True))
