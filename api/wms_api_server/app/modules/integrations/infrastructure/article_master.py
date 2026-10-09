import json
from datetime import datetime

import oracledb

from ....oracle_gateway import OracleGateway
from ..domain.article_mapping import map_articles
from fractions import Fraction
from decimal import Decimal


class ArticleMasterApply:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def apply(self, inbox_id: str, actor: str) -> dict:
        try:
            return self._apply(inbox_id, actor)
        except (ValueError, oracledb.DatabaseError) as exc:
            self.gateway.execute("update RRL_SAP_IDOC_INBOX set STATUS='ERROR',LAST_ERROR=:e where INBOX_ID=:i and STATUS<>'APPLIED'",
                                 {"i": inbox_id, "e": str(exc)[:2000]})
            raise

    def _apply(self, inbox_id: str, actor: str) -> dict:
        from ...inventory.public import inventory_configuration_transaction as configuration_transaction
        with configuration_transaction(self.gateway, "NI01 apply SAP article master", actor, "sap_article_import") as cur:
            cur.execute("select STATUS,PARSED_JSON,RESULT_JSON from RRL_SAP_IDOC_INBOX where INBOX_ID=:i for update", {"i": inbox_id})
            row = cur.fetchone()
            if not row:
                raise LookupError("IDoc not found")
            if row[0] == "APPLIED":
                return json.loads(row[2].read() if hasattr(row[2], "read") else row[2])
            envelope = json.loads(row[1].read() if hasattr(row[1], "read") else row[1])
            articles = map_articles(envelope)
            # Serialize new material identity creation, absent legacy unique key.
            cur.execute("lock table RRL_SAP_ARTICLE_META in share row exclusive mode")
            control = envelope["control"]
            stamp = control.get("CREDAT", "") + control.get("CRETIM", "")
            if len(stamp) != 14 or not stamp.isdigit():
                raise ValueError("Working ARTMAS contract requires CREDAT/CRETIM")
            datetime.strptime(stamp, "%Y%m%d%H%M%S")
            applied, older = [], []
            for item in articles:
                cur.execute("select SOURCE_STAMP,SOURCE_DOCNUM,BASE_UOM,SENDER from RRL_SAP_ARTICLE_META where ARTICUL=:a", {"a": item["material"]})
                previous = cur.fetchone()
                if previous and previous[3] != envelope["sender"]:
                    raise ValueError("Article is owned by a different SAP sender")
                if previous and (stamp, envelope["docnum"].zfill(16)) < (previous[0], previous[1].zfill(16)):
                    older.append(item["material"])
                    continue
                self._article(cur, item, previous, envelope, stamp)
                applied.append(item["material"])
            result = {"inbox_id": inbox_id, "status": "APPLIED", "articles_applied": True,
                      "materials": applied, "older_skipped": older}
            cur.setinputsizes(result=oracledb.DB_TYPE_CLOB)
            cur.execute("update RRL_SAP_IDOC_INBOX set STATUS='APPLIED',RESULT_JSON=:result,LAST_ERROR=null where INBOX_ID=:i",
                        {"i": inbox_id, "result": json.dumps(result)})
        return result

    def _article(self, cur: oracledb.Cursor, item: dict, previous: tuple | None, envelope: dict, stamp: str) -> None:
        key = item["material"]
        cur.execute("select ACTICUL from RRL_ARTICULS where ACTICUL=:a for update", {"a": key})
        rows = cur.fetchall()
        if len(rows) > 1:
            raise ValueError("Ambiguous existing article key")
        if previous and item["base_uom"] and previous[2] != item["base_uom"]:
            raise ValueError("Base UoM change requires explicit stock conversion")
        if not rows:
            if not item["name"] or not item["base_uom"] or not item["ean"]:
                raise ValueError("New article requires description, base UoM and item EAN")
            cur.execute("insert into RRL_ARTICULS (ACTICUL,NAME,UNIT_TYPE,BARCODE_SHT,NORMA_UKLADKI) values (:a,:n,:u,:e,0)",
                        {"a": key, "n": item["name"], "u": item["base_uom"], "e": item["ean"]})
        columns = {"NAME": item["name"], "BARCODE_SHT": item["ean"], "BARCODE_KOR": item["box_ean"],
                   "COUNT_SHT_IN_KOR": item["box_qty"], "NORMA_UKLADKI": item["pallet_qty"]}
        changes = {k: v for k, v in columns.items() if v is not None}
        if changes:
            assignments = ",".join(f"{k}=:{k}" for k in changes)
            cur.execute(f"update RRL_ARTICULS set {assignments} where ACTICUL=:a", {"a": key, **changes})
        cur.execute("merge into RRL_FINISHED_GOODS_SKU d using(select :a ARTICUL from dual)s on(d.ARTICUL=s.ARTICUL) when matched then update set ACTIVE=nvl(:active,d.ACTIVE) when not matched then insert(ARTICUL,ACTIVE,CREATED_BY) values(:a,nvl(:active,1),'SAP_ARTMAS')",
                    {"a": key, "active": item["active"]})
        unit = item["base_uom"] or (previous[2] if previous else None)
        if not unit:
            raise ValueError("Base UoM missing for new SAP mapping")
        cur.setinputsizes(units=oracledb.DB_TYPE_CLOB)
        cur.execute("""merge into RRL_SAP_ARTICLE_META d using(select :a ARTICUL from dual)s on(d.ARTICUL=s.ARTICUL)
          when matched then update set BASE_UOM=:u,SENDER=:sender,SOURCE_STAMP=:stamp,SOURCE_DOCNUM=:doc,
            UNITS_JSON=case when :has_units=1 then :units else d.UNITS_JSON end
          when not matched then insert(ARTICUL,BASE_UOM,SENDER,SOURCE_STAMP,SOURCE_DOCNUM,UNITS_JSON)
            values(:a,:u,:sender,:stamp,:doc,:units)""",
                    {"a": key, "u": unit, "sender": envelope["sender"], "stamp": stamp,
                     "doc": envelope["docnum"], "units": json.dumps(item["units"]), "has_units": int(bool(item["units"]))})

        # Publish exact factors under the configuration X fence before any stock command.
        canonical_base = "EA" if unit.upper() in {"EA", "PCS", "ST", "\u0428\u0422"} else unit.upper()
        scale = 0 if canonical_base == "EA" else (3 if canonical_base == "KG" else 9)
        provenance = "SAP_ARTMAS:" + envelope["docnum"]
        conversion_units = [{"uom": canonical_base, "numerator": 1, "denominator": 1},
                            {"uom": unit, "numerator": 1, "denominator": 1}, *item["units"]]
        for conversion in conversion_units:
            if "numerator" in conversion:
                ratio = Fraction(int(conversion["numerator"]), int(conversion["denominator"]))
            else:
                ratio = Fraction(Decimal(conversion["ratio"]))
            cur.execute("begin RRL_STOCK_UOM_CONFIG.publish(:article,:input,:base,:num,:den,:scale,:provenance);end;",
                        article=key, input=conversion["uom"], base=canonical_base,
                        num=ratio.numerator, den=ratio.denominator, scale=scale, provenance=provenance)
