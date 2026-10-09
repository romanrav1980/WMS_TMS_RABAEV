"""Physical code capture. Does not claim external regulatory approval."""
from hashlib import sha256
from decimal import Decimal
import json

import oracledb
from ..domain.mark_identity import canonical_mark
from ..domain.unit_quantity import unit_quantity, PIECE_UNITS


class ReceivingMarks:
    def __init__(self, cursor: oracledb.Cursor) -> None:
        self.cur = cursor

    def resolve(self, order_id: str, articul: str, line_number: str, quantity: Decimal, payload: dict, base_uom: str, *, lock_policy: bool = True) -> dict:
        cur = self.cur
        cur.execute("select POLICY_VERSION,MARKING_REQUIRED from RRL_SKU_RECEIPT_POLICY where ARTICUL=:a" + (" for update" if lock_policy else ""), {"a": articul})
        policy = cur.fetchone()
        if not policy:
            raise ValueError("Configure WMS receiving/marking policy before receipt")
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
        units, quantities, scanned = {}, {}, []
        fallback = None
        if base_uom.upper() not in PIECE_UNITS:
            cur.execute('select UNITS_JSON from RRL_SAP_ARTICLE_META where ARTICUL=:a', {'a': articul})
            meta = cur.fetchone()
            if meta:
                document = meta[0].read() if hasattr(meta[0], 'read') else meta[0]
                factors = {Decimal(u['ratio']) for u in json.loads(document) if u['uom'].upper() in PIECE_UNITS}
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
            digest = sha256(code.encode()).hexdigest()
            cur.execute("select UNITS_JSON from RRL_SAP_TRACE_AGG where ORDER_ID=:o and LINE_NUMBER=:l and SYSTEM_CODE=:s and PROFILE_CODE=:p and CODE_HASH=:h and AGG_LEVEL=:level",
                        {"o": order_id, "l": line_number, "s": profile[0], "p": profile[1], "h": digest, "level": level})
            known = cur.fetchone()
            if not known:
                raise ValueError("Unknown aggregation composition: import sender manifest; quantity cannot substitute unit codes")
            raw = known[0].read() if hasattr(known[0], "read") else known[0]
            for member in json.loads(raw):
                self._quantity(quantities, member['unit_id'], unit_quantity(member.get('quantity'), base_uom, fallback))
                self._add(units, member["unit_id"], profile, member["code"])
            scanned.append({"system": profile[0], "profile": profile[1], "version": profiles[profile]["version"], "level": level, "code": code})
        if len(units)>10000 or sum(quantities.values(), Decimal(0)) != quantity:
            raise ValueError("Sum of physical unit quantities must equal pallet quantity; maximum 10000 units")
        for unit_codes in units.values():
            if set(unit_codes) != set(profiles):
                raise ValueError("Every physical unit must cover every applicable WMS marking profile")
        return {"policy_version": policy[0], "profiles": profiles, "units": units, "unit_quantities": quantities, "scanned": scanned}

    def persist(self, pallet: str, marks: dict, actor: str, *, bindings: list | None = None, base_uom: str | None = None, cell: str | None = None, source_kind: str = 'PHYSICAL_RECEIPT') -> None:
        cur = self.cur
        binding_map = {b["unit_id"]: b for b in bindings or []}
        # Receiving caller holds global receipt identity lock; database PK rejects cross-pallet duplicates.
        identities = {}
        expected_gtin = None
        if any(profile[0]=='CRPT' for codes in marks['units'].values() for profile in codes):
            cur.execute('select nvl(f.GTIN,a.BARCODE_SHT) from RRL_ARTICULS a join RRL_PALLETS p on p.ARTICUL=a.ACTICUL left join RRL_FINISHED_GOODS_SKU f on f.ARTICUL=a.ACTICUL where p.UID_PALLET=:p', {'p': pallet})
            expected_gtin = str(cur.fetchone()[0]).zfill(14)
        for unit_id, codes in marks["units"].items():
            if bindings is None:
                cur.execute("insert into RRL_WMS_RECEIPT_UNIT(UID_PALLET,UNIT_ID,POLICY_VERSION,BASE_QTY) values(:p,:u,:v,:q)",
                            {"p": pallet, "u": unit_id, "v": marks["policy_version"], "q": marks['unit_quantities'][unit_id]})
            else:
                binding = binding_map[unit_id]
                cur.execute("""insert into RRL_WMS_RECEIPT_UNIT(UID_PALLET,UNIT_ID,POLICY_VERSION,BASE_QTY,
                    PHYSICAL_UNIT_KEY,CURRENT_UID,CURRENT_CELL,BASE_UOM,STOCK_STATUS,UNIT_VERSION)
                    values(:p,:u,:v,:q,:k,:p,:c,:base,'CAPTURED',0)""",
                    p=pallet,u=unit_id,v=marks["policy_version"],q=marks['unit_quantities'][unit_id],k=binding["key"],c=cell,base=base_uom)
            for profile, code in codes.items():
                normalized = canonical_mark(profile[0], profile[1], code, expected_gtin)
                key = (profile[0], sha256(normalized["identity"].encode()).hexdigest())
                if key in identities and identities[key]["unit"] != unit_id:
                    raise ValueError("One unique code cannot identify different physical units")
                identity = identities.setdefault(key, {"unit": unit_id, "code": code, "profiles": [], **normalized})
                identity["profiles"].append({"profile": profile[1], "version": marks["profiles"][profile]["version"], "raw_code": code})
        crpt_parent = None
        if any(system == 'CRPT' for system, _ in identities):
            cur.execute('select UID_PALLET from RRL_CRPT_AGGREGATION where SSCC=:s', {'s': pallet})
            old_parent = cur.fetchone()
            if old_parent and old_parent[0]!=pallet:
                raise ValueError('CRPT aggregation identifier belongs to a different source')
            crpt_parent = cur.callfunc('RRL_PRODUCTION_API.CREATE_AGGREGATION', oracledb.DB_TYPE_NUMBER, [pallet, None, pallet, None, 'PALLET'])
        for (system, digest), identity in identities.items():
            if system == "CRPT":
                cur.execute("select count(*) from RRL_CRPT_CODES c where c.CIS=:code and nvl(c.UID_PALLET,'#')<>:p", {"code": identity["identity"], "p": pallet})
                if cur.fetchone()[0]:
                    raise ValueError("Unique code already belongs to stock in legacy CRPT registry")
            cur.execute("select UID_PALLET from RRL_WMS_RECEIPT_CODE where SYSTEM_CODE=:s and CODE_HASH=:h", {"s": system, "h": digest})
            if cur.fetchone():
                raise ValueError("Unique unit code has already been received")
            cur.setinputsizes(raw=oracledb.DB_TYPE_CLOB, profiles=oracledb.DB_TYPE_CLOB)
            cur.execute("insert into RRL_WMS_RECEIPT_CODE(SYSTEM_CODE,CODE_HASH,UID_PALLET,UNIT_ID,RAW_CODE,PROFILES_JSON,CANONICAL_CODE) values(:s,:h,:p,:u,:raw,:profiles,:canonical)",
                        {"s": system, "h": digest, "p": pallet, "u": identity["unit"], "raw": identity["code"], "profiles": json.dumps(identity["profiles"]), "canonical": identity["identity"]})
            if system == "CRPT":
                if not expected_gtin.isdigit() or expected_gtin.zfill(14) != identity['gtin']:
                    raise ValueError('Unique code GTIN does not match received article')
                cur.callfunc("RRL_PRODUCTION_API.ADD_CRPT_CODE", oracledb.DB_TYPE_NUMBER,
                             [None, pallet, identity["gtin"], identity["identity"], identity["serial"], identity["code"], pallet])
                cur.callproc('RRL_PRODUCTION_API.ADD_AGGREGATION_ITEM', [crpt_parent, 'CIS', identity['identity'], None, identity['gtin'], None])
        for system in {key[0] for key in identities}:
            journal = json.dumps({'pallet': pallet, 'units': len(marks['units']), 'physical_receipt': source_kind == 'PHYSICAL_RECEIPT', 'policy_version': marks['policy_version']})
            cur.callfunc('RRL_REGULATORY_API.WRITE_JOURNAL', oracledb.DB_TYPE_NUMBER,
                keywordParameters={'p_system_code': system, 'p_entity_type': 'PALLET', 'p_entity_id': pallet,
                    'p_uid_pallet': pallet, 'p_sscc': pallet, 'p_operation_type': source_kind,
                    'p_new_status': 'CAPTURED', 'p_payload_json': journal, 'p_created_by': actor})
        seen = set()
        for aggregation in marks["scanned"]:
            key = (aggregation["system"], sha256(aggregation["code"].encode()).hexdigest())
            if key in seen:
                continue
            seen.add(key)
            cur.setinputsizes(raw=oracledb.DB_TYPE_CLOB)
            cur.execute("insert into RRL_WMS_RECEIPT_AGG(SYSTEM_CODE,CODE_HASH,UID_PALLET,PROFILE_CODE,AGG_LEVEL,RAW_CODE) values(:s,:h,:p,:profile,:level,:raw)",
                        {"s": aggregation["system"], "h": sha256(aggregation["code"].encode()).hexdigest(), "p": pallet,
                         "profile": aggregation["profile"], "level": aggregation["level"], "raw": aggregation["code"]})

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
