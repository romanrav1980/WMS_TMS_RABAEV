"""Resolve scanned codes in bounded batches; never reserve or change stock here."""
from hashlib import sha256
from decimal import Decimal
import json
import oracledb
from ..domain.mark_identity import canonical_mark


def resolve_count_codes(gateway, lines) -> list[list[str]]:
    keys = [list(line.unit_keys) for line in lines]
    scans = []
    for index, line in enumerate(lines):
        if line.scans and line.unit_keys:
            raise ValueError("Choose scanned codes or explicit unit identities")
        for scan in line.scans:
            identity = canonical_mark(scan.system_code, scan.profile_code, scan.code)["identity"]
            scans.append({"index": len(scans), "line": index, "uid": line.uid, "cell": line.cell,
                          "article": line.article, "system": scan.system_code, "profile": scan.profile_code,
                          "hash": sha256(identity.encode()).hexdigest()})
    if scans:
        # Read-only resolution in a separate lease; the posting coordinator later verifies
        # the complete locked stock/unit closure. No domain row locks precede that command.
        with gateway.transaction("Resolve inventory scans without stock effects") as cursor:
            for start in range(0, len(scans), 500):
                batch = scans[start:start + 500]
                payload = cursor.var(oracledb.DB_TYPE_CLOB)
                payload.setvalue(0, json.dumps(batch, separators=(",", ":")))
                cursor.execute("""
                    select j.SCAN_INDEX,u.PHYSICAL_UNIT_KEY
                      from json_table(:scans,'$[*]' columns(
                        SCAN_INDEX number path '$.index', UID_VALUE varchar2(200) path '$.uid',
                        CELL_VALUE varchar2(60) path '$.cell', ARTICLE varchar2(160) path '$.article',
                        SYSTEM_CODE varchar2(40) path '$.system', PROFILE_CODE varchar2(60) path '$.profile',
                        CODE_HASH varchar2(64) path '$.hash')) j
                      join RRL_WMS_RECEIPT_CODE c on c.SYSTEM_CODE=j.SYSTEM_CODE and c.CODE_HASH=j.CODE_HASH
                      join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID
                      join RRL_PALLETS p on p.UID_PALLET=u.CURRENT_UID
                     where u.CURRENT_UID=j.UID_VALUE and u.CURRENT_CELL=j.CELL_VALUE and p.ARTICUL=j.ARTICLE
                       and exists(select 1 from RRL_SKU_RECEIPT_PROFILE profile
                         where profile.ARTICUL=j.ARTICLE and profile.SYSTEM_CODE=j.SYSTEM_CODE
                           and profile.PROFILE_CODE=j.PROFILE_CODE)
                """, {"scans": payload})
                resolved = {}
                for index, key in cursor:
                    index = int(index)
                    if index in resolved or not key:
                        raise ValueError("Scanned code has ambiguous physical identity")
                    resolved[index] = key
                if len(resolved) != len(batch):
                    raise ValueError("Scanned code does not identify a unit of this pallet and cell")
                for scan in batch:
                    keys[scan["line"]].append(resolved[scan["index"]])
    present_lines = [{"line": index, "uid": line.uid, "cell": line.cell} for index, line in enumerate(lines) if not line.unit_keys]
    if present_lines:
        with gateway.transaction("Resolve measured inventory unit composition") as cursor:
            payload = cursor.var(oracledb.DB_TYPE_CLOB)
            payload.setvalue(0, json.dumps(present_lines, separators=(",", ":")))
            cursor.execute("""
                select j.LINE_INDEX,u.PHYSICAL_UNIT_KEY,to_char(u.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''),u.BASE_UOM
                  from json_table(:lines,'$[*]' columns(LINE_INDEX number path '$.line',
                    UID_VALUE varchar2(200) path '$.uid',CELL_VALUE varchar2(60) path '$.cell'))j
                  join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=j.UID_VALUE and u.CURRENT_CELL=j.CELL_VALUE
                 where u.STOCK_STATUS!='ISSUED'
                 order by j.LINE_INDEX,u.PHYSICAL_UNIT_KEY fetch first 10001 rows only
            """, {"lines": payload})
            physical = cursor.fetchall()
            if len(physical) > 10000:
                raise ValueError("Inventory physical-unit closure exceeds 10000 units")
        by_line = {}
        for index, key, quantity, unit in physical:
            by_line.setdefault(int(index), {})[key] = (Decimal(str(quantity)), unit)
        for item in present_lines:
            index = item["line"]
            registered = by_line.get(index, {})
            if not registered:
                if keys[index]:
                    raise ValueError("Scanned units have no current physical composition")
                continue
            present = set(keys[index])
            if any(key not in registered for key in present):
                raise ValueError("Scanned unit is no longer present in the counted pallet")
            if any(unit != lines[index].unit for quantity, unit in registered.values()):
                raise ValueError("Marked inventory count must use the displayed base unit")
            measured = sum((registered[key][0] for key in present), Decimal(0))
            if measured != Decimal(lines[index].quantity):
                raise ValueError("Scanned present units do not match measured quantity")
            keys[index] = sorted(set(registered) - present)
    all_keys = [key for selected in keys for key in selected]
    if len(all_keys) != len(set(all_keys)):
        raise ValueError("Multiple scans identify the same physical unit")
    return [sorted(selected) for selected in keys]
