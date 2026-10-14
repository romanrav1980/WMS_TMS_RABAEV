"""ERP item lines share the unchanged legacy document/SKU planning row."""
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
