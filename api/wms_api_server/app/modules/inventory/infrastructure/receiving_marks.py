"""Physical code capture. Does not claim external regulatory approval."""
from hashlib import sha256
from decimal import Decimal
from typing import Any
from ...platform.public import read_oracle_json
from .receipt_regulatory_parent import create_receipt_parent
from .trace_aggregation_source import source_header,aggregation_members,assert_sender_capture,assert_current_mark_policy,persist_scanned_aggregates
import json

import oracledb
from ..domain.mark_identity import canonical_mark
from ..domain.capture_policy import assert_capture_policy
from ..domain.unit_quantity import unit_quantity, PIECE_UNITS


class ReceivingMarks:
    def __init__(self, cursor: oracledb.Cursor) -> None:
        self.cur = cursor

    def resolve(self, order_id: str, articul: str, line_number: str, quantity: Decimal, payload: dict, base_uom: str, *, lock_policy: bool = True, birth_context: dict[str,Any]|None = None) -> dict:
        cur = self.cur
        cur.execute("select POLICY_VERSION,MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES from RRL_SKU_RECEIPT_POLICY where ARTICUL=:a" + (" for update" if lock_policy else ""), {"a": articul})
        policy = cur.fetchone()
        if not policy:
            raise ValueError("Configure WMS receiving/marking policy before receipt")
        if payload.get("weighted_boxes") or policy[2]:
            from .weighted_box_capture import resolve_weighted_boxes
            return resolve_weighted_boxes(cur, articul, quantity, payload, base_uom, policy)
        if not policy[1]:
            if payload["units"] or payload["aggregations"]:
                raise ValueError("Unmarked item must use product barcode receipt")
            cur.execute("select a.BARCODE_SHT,a.BARCODE_KOR,nvl(f.CRPT_REQUIRED,0) from RRL_ARTICULS a left join RRL_FINISHED_GOODS_SKU f on f.ARTICUL=a.ACTICUL where a.ACTICUL=:a", {"a": articul})
            rows = cur.fetchall()
            if len(rows) != 1 or rows[0][2] or not payload.get("product_barcode") or payload["product_barcode"] not in rows[0][:2]:
                raise ValueError("Product barcode/policy does not match unmarked article")
            return {"policy_version": policy[0], "units": {}, "scanned": []}
        cur.execute("select SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL=:a", {"a": articul})
        profiles = {(r[0], r[1]): {"version": r[2], "mode": r[3]} for r in cur.fetchall()}
        if not profiles:
            raise ValueError("Marked item has no WMS profiles")
        assert_capture_policy(payload,policy[0],profiles)
        manifest_id=payload.get("manifest_operation_id")
        header=None
        if manifest_id:
            if not birth_context or not payload["aggregations"]:
                raise ValueError("Non-SAP manifest requires an explicit birth source and aggregation scan")
            header=source_header(cur,manifest_id,**birth_context,policy_version=policy[0],profiles=profiles)
        units, quantities, scanned = {}, {}, []
        fallback = None
        if base_uom.upper() not in PIECE_UNITS:
            cur.execute('select UNITS_JSON from RRL_SAP_ARTICLE_META where ARTICUL=:a', {'a': articul})
            meta = cur.fetchone()
            if meta:
                document = meta[0].read() if hasattr(meta[0], 'read') else meta[0]
                factors = {Decimal(u['ratio']) for u in read_oracle_json(document) if u['uom'].upper() in PIECE_UNITS}
                fallback = next(iter(factors)) if len(factors)==1 else None
        for item in payload["units"]:
            unit_id = self._value(item, "unit_id", 100)
            self._quantity(quantities, unit_id, unit_quantity(item.get('quantity'), base_uom, fallback))
            codes = item.get("codes")
            if not isinstance(codes, list) or not codes:
                raise ValueError("Each scanned physical unit requires its unique codes")
            for code in codes:
                profile = self._profile(code, profiles)
                if profiles[profile]["mode"] not in {"UNIT", "UNIT_OR_AGGREGATION"}:
                    raise ValueError("This WMS profile requires aggregation scanning")
                self._add(units, unit_id, profile, self._value(code, "code", 4000))
        for aggregation in payload["aggregations"]:
            profile = self._profile(aggregation, profiles)
            level = self._value(aggregation, "level", 10)
            if level not in {"BOX", "PALLET"} or profiles[profile]["mode"] not in {level, "UNIT_OR_AGGREGATION"}:
                raise ValueError("Aggregation level forbidden by WMS receiving profile")
            code = self._value(aggregation, "code", 4000)
            for member in aggregation_members(cur,order_id,line_number,profile,code,level,manifest_id):
                self._quantity(quantities, member['unit_id'], unit_quantity(member.get('quantity'), base_uom, fallback))
                self._add(units, member["unit_id"], profile, member["code"])
            scanned.append({"system": profile[0], "profile": profile[1], "version": profiles[profile]["version"], "level": level, "code": code})
        if len(units)>10000 or sum(quantities.values(), Decimal(0)) != quantity:
            raise ValueError("Sum of physical unit quantities must equal pallet quantity; maximum 10000 units")
        for unit_codes in units.values():
            if set(unit_codes) != set(profiles):
                raise ValueError("Every physical unit must cover every applicable WMS marking profile")
        if header:
            assert_sender_capture(header,units,quantities,base_uom)
        return {"policy_version": policy[0], "profiles": profiles, "units": units, "unit_quantities": quantities, "scanned": scanned,"manifest_operation_id":manifest_id}

    def persist(self, pallet: str, marks: dict, actor: str, *, bindings: list | None = None, base_uom: str | None = None, cell: str | None = None, source_kind: str = 'PHYSICAL_RECEIPT') -> None:
        cur = self.cur
        if marks.get("weighted_boxes"):
            from .weighted_box_capture import assert_current_weighted_policy
            assert_current_weighted_policy(cur, pallet, marks)
        elif marks.get('units'):assert_current_mark_policy(cur,pallet,marks)
        # Receiving caller holds global receipt identity lock; database PK rejects cross-pallet duplicates.
        # Set-based: a 1000-unit pallet used to cost ~6000 round trips (C-0147); effects, order and errors are unchanged.
        expected_gtin = None
        if any(profile[0]=='CRPT' for codes in marks['units'].values() for profile in codes):
            cur.execute('select nvl(f.GTIN,a.BARCODE_SHT) from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL left join RRL_FINISHED_GOODS_SKU f on f.ARTICUL=a.ACTICUL where p.UID_PALLET=:p', {'p': pallet})
            expected_gtin = str(cur.fetchone()[0]).zfill(14)
        identities = self._identities(marks, expected_gtin)
        self._insert_units(pallet, marks, bindings, base_uom, cell)
        crpt_parent,regulatory_sscc = None,None
        if any(system == 'CRPT' for system, _ in identities):
            crpt_parent,regulatory_sscc=create_receipt_parent(cur,pallet,marks["scanned"])
        self._assert_new_codes(pallet, identities)
        crpt = [identity for (system, _), identity in identities.items() if system == "CRPT"]
        if crpt and (not expected_gtin.isdigit() or any(expected_gtin.zfill(14) != identity['gtin'] for identity in crpt)):
            raise ValueError('Unique code GTIN does not match received article')
        if identities:
            cur.setinputsizes(p_raw=oracledb.DB_TYPE_CLOB, profiles=oracledb.DB_TYPE_CLOB)
            cur.executemany("insert into RRL_WMS_RECEIPT_CODE(SYSTEM_CODE,CODE_HASH,UID_PALLET,UNIT_ID,RAW_CODE,PROFILES_JSON,CANONICAL_CODE) values(:s,:h,:p,:u,:p_raw,:profiles,:canonical)",
                            [{"s": system, "h": digest, "p": pallet, "u": identity["unit"], "p_raw": identity["code"], "profiles": json.dumps(identity["profiles"]),
                              "canonical": identity["identity"]} for (system, digest), identity in identities.items()])
        if crpt:
            self._register_crpt(pallet, crpt, regulatory_sscc, crpt_parent)
        for system in {key[0] for key in identities}:
            journal = json.dumps({'pallet': pallet, 'units': len(marks['units']), 'physical_receipt': source_kind == 'PHYSICAL_RECEIPT', 'policy_version': marks['policy_version']})
            cur.callfunc('RRL_REGULATORY_API.WRITE_JOURNAL', oracledb.DB_TYPE_NUMBER,
                keywordParameters={'p_system_code': system, 'p_entity_type': 'PALLET', 'p_entity_id': pallet,
                    'p_uid_pallet': pallet, 'p_sscc': regulatory_sscc if system=='CRPT' else None, 'p_operation_type': source_kind,
                    'p_new_status': 'CAPTURED', 'p_payload_json': journal, 'p_created_by': actor})
        persist_scanned_aggregates(cur,pallet,marks["scanned"])

    @staticmethod
    def _identities(marks: dict, expected_gtin: str | None) -> dict:
        identities = {}
        for unit_id, codes in marks["units"].items():
            for profile, code in codes.items():
                normalized = canonical_mark(profile[0], profile[1], code, expected_gtin)
                key = (profile[0], sha256(normalized["identity"].encode()).hexdigest())
                if key in identities and identities[key]["unit"] != unit_id:
                    raise ValueError("One unique code cannot identify different physical units")
                identity = identities.setdefault(key, {"unit": unit_id, "code": code, "profiles": [], **normalized})
                identity["profiles"].append({"profile": profile[1], "version": marks["profiles"][profile]["version"], "raw_code": code})
        return identities

    def _insert_units(self, pallet: str, marks: dict, bindings: list | None, base_uom: str | None, cell: str | None) -> None:
        units = list(marks["units"])
        if not units:
            return
        if bindings is None:
            self.cur.executemany("insert into RRL_WMS_RECEIPT_UNIT(UID_PALLET,UNIT_ID,POLICY_VERSION,BASE_QTY) values(:p,:u,:v,:q)",
                                 [{"p": pallet, "u": u, "v": marks["policy_version"], "q": marks['unit_quantities'][u]} for u in units])
            return
        binding_map, boxes, rows = {b["unit_id"]: b for b in bindings}, marks.get("weighted_boxes", {}), []
        for u in units:
            box = boxes.get(u, {})
            rows.append(dict(p=pallet, u=u, v=marks["policy_version"], q=marks['unit_quantities'][u], k=binding_map[u]["key"], c=cell, base=base_uom,
                             gross=Decimal(box["gross_weight_kg"]) if box.get("gross_weight_kg") else None,
                             volume=Decimal(box["volume_m3"]) if box.get("volume_m3") else None,
                             reference=box.get("measurement_reference"), label=box.get("raw_scan")))
        self.cur.executemany("""insert into RRL_WMS_RECEIPT_UNIT(UID_PALLET,UNIT_ID,POLICY_VERSION,BASE_QTY,
            PHYSICAL_UNIT_KEY,CURRENT_UID,CURRENT_CELL,BASE_UOM,STOCK_STATUS,UNIT_VERSION,
            GROSS_WEIGHT_KG,BOX_VOLUME_M3,MEASUREMENT_REFERENCE,WEIGHT_LABEL_SCAN)
            values(:p,:u,:v,:q,:k,:p,:c,:base,'CAPTURED',0,:gross,:volume,:reference,:label)""", rows)

    def _assert_new_codes(self, pallet: str, identities: dict) -> None:
        """Both uniqueness checks for the whole pallet in one query each (same predicates as the per-code checks)."""
        cis = [identity["identity"] for (system, _), identity in identities.items() if system == "CRPT"]
        if cis:
            self.cur.setinputsizes(codes=oracledb.DB_TYPE_CLOB)
            self.cur.execute("select count(*) from RRL_CRPT_CODES c join json_table(:codes,'$[*]' columns(CIS varchar2(4000) path '$')) j on j.CIS=c.CIS "
                             "where nvl(c.UID_PALLET,'#')<>:p", codes=json.dumps(cis), p=pallet)
            if self.cur.fetchone()[0]:
                raise ValueError("Unique code already belongs to stock in legacy CRPT registry")
        for system in {key[0] for key in identities}:
            self.cur.setinputsizes(hashes=oracledb.DB_TYPE_CLOB)
            self.cur.execute("select count(*) from RRL_WMS_RECEIPT_CODE r join json_table(:hashes,'$[*]' columns(H varchar2(64) path '$')) j on j.H=r.CODE_HASH "
                             "where r.SYSTEM_CODE=:s", hashes=json.dumps([digest for (s, digest) in identities if s == system]), s=system)
            if self.cur.fetchone()[0]:
                raise ValueError("Unique unit code has already been received")

    def _register_crpt(self, pallet: str, crpt: list[dict], sscc: str | None, parent: int | None) -> None:
        """The same native registration calls per code, in the same order, inside one server round trip."""
        self.cur.setinputsizes(codes=oracledb.DB_TYPE_CLOB)
        self.cur.execute("""declare v number;begin
             for r in(select GTIN,CIS,SERIAL_NO,RAW_CODE from json_table(:codes,'$[*]' columns(SEQ for ordinality,GTIN varchar2(14) path '$.gtin',
               CIS varchar2(4000) path '$.cis',SERIAL_NO varchar2(4000) path '$.serial',RAW_CODE varchar2(4000) path '$.raw')) order by SEQ)loop
              v:=RRL_PRODUCTION_API.ADD_CRPT_CODE(null,:p,r.GTIN,r.CIS,r.SERIAL_NO,r.RAW_CODE,:sscc);
              if :parent is not null then RRL_PRODUCTION_API.ADD_AGGREGATION_ITEM(:parent,'CIS',r.CIS,null,r.GTIN,null);end if;
             end loop;end;""",
                         codes=json.dumps([{"gtin": i["gtin"], "cis": i["identity"], "serial": i["serial"], "raw": i["code"]} for i in crpt]),
                         p=pallet, sscc=sscc, parent=parent)

    @staticmethod
    def _quantity(quantities: dict, unit_id: str, value: Decimal) -> None:
        if unit_id in quantities and quantities[unit_id]!=value:
            raise ValueError('Profiles disagree on the quantity of the same physical unit')
        quantities[unit_id] = value

    @staticmethod
    def _value(item: dict, name: str, maximum: int) -> str:
        if not isinstance(item, dict) or not isinstance(item.get(name), str):
            raise ValueError(f"Missing {name}")
        value = item[name]
        # Scanner payload is preserved verbatim, including GS separators.
        if not value or len(value.encode("utf-8")) > maximum:
            raise ValueError(f"Empty or oversized {name}")
        return value

    def _profile(self, item: dict, profiles: dict) -> tuple:
        key = (self._value(item, "system_code", 40), self._value(item, "profile_code", 80))
        if key not in profiles:
            raise ValueError("Scanned marking profile is not configured for this article")
        return key

    @staticmethod
    def _add(units: dict, unit_id: str, profile: tuple, code: str) -> None:
        if not isinstance(unit_id, str) or not unit_id or len(unit_id.encode()) > 100 or not isinstance(code, str) or not code or len(code.encode()) > 4000:
            raise ValueError("Invalid aggregation member")
        unit = units.setdefault(unit_id, {})
        if profile in unit:
            raise ValueError("Physical unit/profile scanned more than once")
        unit[profile] = code
