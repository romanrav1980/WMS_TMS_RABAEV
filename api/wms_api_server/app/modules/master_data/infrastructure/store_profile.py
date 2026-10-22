"""Профиль магазина: одна CONFIG-транзакция — текущая версия, окна приёма и неизменяемая запись операции."""
import hashlib
import json
from typing import Any
import oracledb
from ...platform.public import stock_configuration_transaction, read_oracle_json
from ..contracts_store_profile import StoreProfileError
from ..domain.store_profile import FLAGS, StoreProfileInvalid, normalize_profile, normalize_windows, normalize_delivery_changes, delivery_rules_hash

COLUMNS = ("RECEIVING_WINDOW_MODE,TIMEZONE_REGION,BACKROOM_FLAG,BACKROOM_PALLETS,BACKROOM_ROLLS,UNATTENDED_DROP_FLAG,STORAGE_TEMP_CLASS,"
           "RAMP_FLAG,RAMP_HEIGHT_MM,MAX_VEHICLE_OUTER_HEIGHT_MM,MAX_VEHICLE_OUTER_LENGTH_MM,DEFAULT_UNLOAD_METHOD,LOADER_REQUIRED,ACCESS_NOTE")
NAMES = ("receiving_window_mode", "timezone_region", "backroom_flag", "backroom_pallets", "backroom_rolls", "unattended_drop_flag", "storage_temp_class",
         "ramp_flag", "ramp_height_mm", "max_vehicle_outer_height_mm", "max_vehicle_outer_length_mm", "default_unload_method", "loader_required", "access_note")


def _not_installed(error: oracledb.DatabaseError) -> bool:
    return getattr(error.args[0], "code", 0) == 942  # ORA-00942: таблицы профиля ещё не установлены


def read_delivery_rules(cur: Any, address: str, lock: bool = False) -> dict[str, Any]:
    cur.execute("select UNLOAD_NORM_MIN,TW_STRICT from RRL_ADDR where ADDR=:a and nvl(DELETED3,0)=0" + (" for update wait 5" if lock else ""), a=address)
    rows = cur.fetchall()
    if len(rows) != 1:
        return {"status": "MISSING_OR_AMBIGUOUS", "source_hash": None}
    duration, strict = rows[0]
    return {"status": "KNOWN", "unload_norm_min": duration, "window_strict": None if strict is None else bool(strict),
            "source_hash": delivery_rules_hash(address, duration, strict)}


def save_delivery_rules(cur: Any, address: str, canonical: dict[str, Any]) -> None:
    columns = {"unload_norm_min": "UNLOAD_NORM_MIN", "window_strict": "TW_STRICT"}
    changes = {key: canonical[key] for key in columns if key in canonical}
    if not changes:
        return
    current = read_delivery_rules(cur, address, lock=True)
    if current["status"] != "KNOWN" or current["source_hash"] != canonical["expected_delivery_rules_hash"]:
        raise StoreProfileError("STORE_DELIVERY_RULES_CHANGED", 409, "Правила доставки изменились. Перечитайте карточку магазина")
    params = {key: int(value) if isinstance(value, bool) else value for key, value in changes.items()}
    cur.execute("update RRL_ADDR set " + ",".join(columns[key] + "=:" + key for key in changes) + " where ADDR=:a and nvl(DELETED3,0)=0", a=address, **params)
    if cur.rowcount != 1:
        raise StoreProfileError("STORE_PROFILE_ADDRESS_MISSING_OR_AMBIGUOUS", 409)


def read_profile(cur: Any, address: str) -> dict[str, Any]:
    rules = read_delivery_rules(cur, address)
    cur.execute("select PROFILE_VERSION," + COLUMNS + ",UPDATED_BY,to_char(UPDATED_AT,'YYYY-MM-DD\"T\"HH24:MI:SS') from RRL_STORE_PROFILE where STORE_ADDR=:a", a=address)
    row = cur.fetchone()
    if row is None:
        return {"store_addr": address, "configured": False, "version": 0, "delivery_rules": rules,
                "profile": {**{name: None for name in NAMES}, "receiving_window_mode": "UNCONFIGURED"}, "windows": []}
    profile = dict(zip(NAMES, row[1:1 + len(NAMES)]))
    for name in FLAGS:
        if profile[name] is not None:
            profile[name] = bool(profile[name])
    cur.execute("select WEEKDAY,FROM_MINUTE,TO_MINUTE from RRL_STORE_RECEIVING_WINDOW where STORE_ADDR=:a order by WEEKDAY,FROM_MINUTE fetch first 57 rows only", a=address)
    rows = cur.fetchall()
    if len(rows) > 56:
        raise StoreProfileError("STORE_PROFILE_WINDOW_BOUND_EXCEEDED", 409)
    windows = [{"weekday": d, "from_minute": f, "to_minute": t} for d, f, t in rows]
    return {"store_addr": address, "configured": True, "version": row[0], "profile": profile, "windows": windows, "delivery_rules": rules,
            "updated_by": row[-2], "updated_at": row[-1]}


class StoreProfile:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def read(self, address: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Store profile read") as cur:
                cur.execute("set transaction read only")
                return {**read_profile(cur, address), "installed": True}
        except oracledb.DatabaseError as error:
            if not _not_installed(error):
                raise
            return {"store_addr": address, "installed": False, "configured": False, "version": 0, "profile": None, "windows": []}

    def save(self, actor: str, body: dict[str, Any]) -> dict[str, Any]:
        try:
            profile = normalize_profile(body)
            windows = normalize_windows(body.get("windows") or [], profile["receiving_window_mode"])
            delivery_changes = normalize_delivery_changes(body)
        except StoreProfileInvalid as invalid:
            raise StoreProfileError(invalid.code, 422, str(invalid)) from invalid
        canonical = {"store_addr": body["store_addr"], "expected_version": body["expected_version"], "reason": body["reason"],
                     **profile, "windows": windows, **delivery_changes}
        wire = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(wire.encode("utf-8")).hexdigest()
        try:
            return self._save(actor, body["operation_id"], canonical, profile, windows, wire, digest)
        except oracledb.DatabaseError as error:
            if _not_installed(error):
                raise StoreProfileError("STORE_PROFILE_NOT_INSTALLED", 503, "Профиль магазина ещё не установлен в базе") from error
            raise

    def _save(self, actor: str, op: str, canonical: dict[str, Any], profile: dict[str, Any], windows: list[dict[str, int]],
              wire: str, digest: str) -> dict[str, Any]:
        address = canonical["store_addr"]
        with stock_configuration_transaction(self.gateway, "Store profile publication", actor, "warehouse_settings_edit") as cur:
            cur.execute("select ACTOR,REQUEST_HASH,RESULT_JSON from RRL_STORE_PROFILE_CHANGE where OPERATION_ID=:op", op=op)
            saved = cur.fetchone()
            if saved:
                if saved[0] != actor or saved[1] != digest:
                    raise StoreProfileError("STORE_PROFILE_OPERATION_PAYLOAD_CONFLICT")
                return read_oracle_json(saved[2])
            if profile["timezone_region"] is not None:
                cur.execute("select count(*) from V$TIMEZONE_NAMES where TZNAME=:z", z=profile["timezone_region"])
                if cur.fetchone()[0] == 0:
                    raise StoreProfileError("STORE_PROFILE_TIMEZONE_UNKNOWN", 422, "Часовой пояс отсутствует в каталоге Oracle")
            cur.execute("select 1 from RRL_ADDR where ADDR=:a and nvl(DELETED3,0)=0 fetch first 2 rows only", a=address)
            if len(cur.fetchall()) != 1:
                raise StoreProfileError("STORE_PROFILE_ADDRESS_MISSING_OR_AMBIGUOUS", 422)
            cur.execute("select PROFILE_VERSION from RRL_STORE_PROFILE where STORE_ADDR=:a for update wait 5", a=address)
            row = cur.fetchone()
            current = row[0] if row else 0
            if current != canonical["expected_version"]:
                raise StoreProfileError("STORE_PROFILE_VERSION_CHANGED")
            save_delivery_rules(cur, address, canonical)
            values = {name: (int(profile[name]) if name in FLAGS and profile[name] is not None else profile[name]) for name in NAMES}
            params = {"a": address, "v": current + 1, "actor": actor, **values}
            assignments = ",".join(f"{column}=:{name}" for column, name in zip(COLUMNS.split(","), NAMES))
            if row:
                cur.execute(f"update RRL_STORE_PROFILE set PROFILE_VERSION=:v,{assignments},UPDATED_BY=:actor,UPDATED_AT=systimestamp where STORE_ADDR=:a", params)
            else:
                cur.execute(f"insert into RRL_STORE_PROFILE(STORE_ADDR,PROFILE_VERSION,{COLUMNS},UPDATED_BY) values(:a,:v,"
                            + ",".join(":" + name for name in NAMES) + ",:actor)", params)
            cur.execute("delete from RRL_STORE_RECEIVING_WINDOW where STORE_ADDR=:a", a=address)
            if windows:
                cur.executemany("insert into RRL_STORE_RECEIVING_WINDOW(STORE_ADDR,WEEKDAY,FROM_MINUTE,TO_MINUTE) values(:a,:d,:f,:t)",
                                [{"a": address, "d": w["weekday"], "f": w["from_minute"], "t": w["to_minute"]} for w in windows])
            result = {**read_profile(cur, address), "operation_id": op, "stock_changed": False, "installed": True}
            cur.execute("""insert into RRL_STORE_PROFILE_CHANGE(OPERATION_ID,STORE_ADDR,PROFILE_VERSION,ACTOR,REASON_TEXT,REQUEST_HASH,REQUEST_JSON,RESULT_JSON)
                values(:op,:a,:v,:actor,:reason,:hash,:request,:result)""", op=op, a=address, v=current + 1, actor=actor,
                        reason=canonical["reason"], hash=digest, request=wire, result=json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str))
            return result

