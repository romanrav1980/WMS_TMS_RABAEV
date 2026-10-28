"""C-0192 T06/T07: cleanup companion after the C0190 mixed tree was shipped and received through C0191 (root executes; Claude never runs it).

Runs only after complete delivery (C0191 STORE_RECEIPT done) on the C0190+C0191 Live state, and reverses only what this run created:
1. the root tare returns from the vehicle to the warehouse between two distinct actors (offer by the run's driver, accept by the
   warehouse), and the warehouse balance of that one pallet is counted to zero (unless C0190 cleanup zeroes the same pallet type);
2. the driver binding is switched off;
3. the wave is finished through /api/picking/waves/{wave}/finish-execution (preview must be ready or completed);
4. only this run's own lots remain (registered lots with the exact unpicked remainder, no active reservations, no foreign rows);
   they are counted to zero through the native INVENTORY_COUNT and the warehouse is verified empty;
5. retirement of this run's synthetic driver/receiver/rights STOPS with RETIRE_REQUIRES_DURABLE_OWNER_FINALIZER (K-0225): there is no
   durable journaled finalizer for RUSERS/RIGHTS yet, so no user or right is changed and cleanup is reported incomplete.
A departed historical tree is never detached or returned. Every mutation goes through the C0190 journal (stored before sending,
the exact body and operation id repeated on resume, an unknown outcome blocks the rest). Importing this module does no live work.
"""
from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

SYNTHETIC_USER = re.compile(r"^MT28[DR][0-9a-f]{9}$")


class CleanupStop(RuntimeError):
    """A fail-closed stop with the exact reason; nothing after it is attempted."""


# ---------------------------------------------------------------- pure, offline-tested parts

def delivery_findings(state: dict[str, Any]) -> list[str]:
    """Cleanup starts only after the complete C0191 delivery with identifiers that belong to this fixture."""
    out, t = [], state.get("transport") or {}
    done = set(t.get("stages_done", []))
    if "STORE_RECEIPT" not in done:
        out.append(f"DELIVERY_INCOMPLETE:{t.get('last_verified_stage')}")
    if t.get("stopped"):
        out.append("DELIVERY_STOPPED:" + str(t["stopped"])[:120])
    tag = state.get("tag", "")
    if not tag.startswith("MT28") or not isinstance(state.get("warehouse"), int) or not state.get("wave"):
        out.append("FIXTURE_IDENTITY_INCOMPLETE")
    for key in ("driver_user", "receiver_user"):
        if not (isinstance(t.get(key), str) and SYNTHETIC_USER.fullmatch(t[key])):
            out.append(f"FOREIGN_OR_MISSING_USER:{key}")
    results = (state.get("journal") or {}).get("results", {})
    for key, field, journal_key, value_key in (("vehicle_id", "id", "t.vehicle", "id"), ("driver_id", "id", "t.driver", "id"),
                                               ("transport_task_id", "task_id", "t.task", "task_id")):
        recorded = (results.get(journal_key) or {}).get("value") or {}
        if t.get(key) is None or recorded.get(value_key) != t.get(key):
            out.append(f"TRANSPORT_ID_NOT_FROM_THIS_RUN:{key}")
    if not t.get("expected_remainder_after_load"):
        out.append("EXPECTED_REMAINDER_AFTER_LOAD_MISSING")
    return out


def zero_root_tare_here(transport: dict[str, Any], cases: dict[str, Any]) -> bool:
    """C0190 cleanup counts the CASE pallet types; the root type is closed here only when it differs (never twice)."""
    return transport["inputs"]["pallet_type_id"] not in {c.get("pallet_type") for c in (cases or {}).values()}


def stock_findings(rows: list[tuple], reservations: int, own_uids: set[str], expected: dict[str, str]) -> list[str]:
    """Rows (uid, cell, article, unit, stock_version, remain): only own lots with the exact unpicked remainder may be counted."""
    out, totals = [], {}
    for uid, cell, article, unit, version, remain in rows:
        if uid not in own_uids:
            out.append(f"FOREIGN_UID:{uid}")
        if article not in expected:
            out.append(f"FOREIGN_ARTICLE:{article}")
        totals[article] = totals.get(article, Decimal(0)) + Decimal(str(remain))
    for article, qty in expected.items():
        if totals.get(article, Decimal(0)) != Decimal(str(qty)):
            out.append(f"REMAINDER_MISMATCH:{article}:{totals.get(article, Decimal(0))}!={qty}")
    if reservations:
        out.append(f"ACTIVE_RESERVATIONS:{reservations}")
    return out


def cleanup_plan(state: dict[str, Any]) -> list[str]:
    findings = delivery_findings(state)
    if findings:
        return ["STOP:" + ",".join(findings)]
    t, plan = state["transport"], ["TARE_RETURN_OFFER:driver", "TARE_RETURN_ACCEPT:warehouse"]
    plan.append("TARE_COUNT_ZERO:root" if zero_root_tare_here(t, state.get("cases")) else "TARE_COUNT_ZERO:by_C0190_cleanup")
    plan += ["DRIVER_BINDING_OFF", "WAVE_FINISH_EXECUTION", "VERIFY_OWN_STOCK_SCOPE", "INVENTORY_COUNT_OWN_LOTS_ZERO", "VERIFY_WAREHOUSE_EMPTY",
             "STOP:RETIRE_REQUIRES_DURABLE_OWNER_FINALIZER"]
    return plan


# ---------------------------------------------------------------- live part (root executes)

class MixedTreeCleanup:
    def __init__(self, live: Any):
        self.live, self.s = live, live.s
        self.t = self.s.get("transport") or {}
        self.c = self.s.setdefault("c0192", {"steps_done": []})

    def step(self, name: str, fn) -> None:
        if name in self.c["steps_done"]:
            return
        fn()
        self.c["steps_done"].append(name); self.live.save()

    def send_as(self, actor: str, key: str, method: str, path: str, body: Any) -> Any:
        import httpx
        if not SYNTHETIC_USER.fullmatch(actor):
            raise CleanupStop(f"FOREIGN_USER:{actor}")
        secret = self.live.one("select PASS from RUSERS where ID=:a and nvl(DELETED,0)=0", a=actor)  # in memory only
        saved, self.live.http = self.live.http, httpx.Client(auth=(actor, secret), timeout=60)
        try:
            return self.live.send(key, method, path, body)
        finally:
            self.live.http = saved

    def tare_return(self) -> None:
        i, tag, ware = self.t["inputs"], self.s["tag"], self.s["warehouse"]
        self.send_as(self.t["driver_user"], "c.tare.return.offer", "POST", "/api/inventory/tare/offer", {"operation_id": f"{tag}.C.TARE.RETURN.OFFER",
                     "task_id": self.t["transport_task_id"], "owner_ware_id": ware, "pallet_type_id": i["pallet_type_id"], "condition": "GOOD",
                     "from_kind": "VEHICLE", "from_id": str(self.t["vehicle_id"]), "to_kind": "WAREHOUSE", "to_id": str(ware), "quantity": "1",
                     "scan_vehicle": i["vehicle_number"]})
        self.live.send("c.tare.return.accept", "POST", "/api/inventory/tare/accept", {"operation_id": f"{tag}.C.TARE.RETURN.ACCEPT",
                       "offer_operation_id": f"{tag}.C.TARE.RETURN.OFFER", "accepted_quantity": "1", "scan_vehicle": i["vehicle_number"]})

    def tare_zero(self) -> None:
        if not zero_root_tare_here(self.t, self.s.get("cases")):
            self.c["root_tare_zero"] = "BY_C0190_CLEANUP"; self.live.save(); return
        ware, pallet_type = self.s["warehouse"], self.t["inputs"]["pallet_type_id"]
        rows = [r for r in self.live.get(f"/api/inventory/tare/warehouses/{ware}/balances")
                if r.get("custodian_kind") == "WAREHOUSE" and r.get("custodian_id") == str(ware) and r.get("pallet_type_id") == pallet_type and r.get("condition_code") == "GOOD"]
        if len(rows) != 1 or str(rows[0].get("quantity")) != "1":
            raise CleanupStop(f"ROOT_TARE_BALANCE_UNEXPECTED:{rows}")  # only the one pallet this run counted may be closed
        self.live.send("c.tare.zero", "POST", "/api/inventory/tare/count", {"operation_id": f"{self.s['tag']}.C.TARE.ZERO", "owner_ware_id": ware,
                       "pallet_type_id": pallet_type, "condition": "GOOD", "observed_quantity": "0", "expected_version": rows[0]["balance_version"],
                       "reason": "C0192 close synthetic root tare after native return", "decision_reference": f"SYNTHETIC_FIXTURE_NOT_PHYSICAL:TARE:{self.s['tag']}"})

    def binding_off(self) -> None:
        binding = (self.live.journal.results.get("t.driver.binding") or {}).get("value") or {}
        self.live.send("c.driver.binding.off", "PUT", f"/api/transport/driver-bindings/{self.t['driver_id']}",
                       {"user_id": self.t["driver_user"], "active": False, "expected_version": int(binding.get("version", 1))})

    def wave_finish(self) -> None:
        wave = self.s["wave"]
        preview = self.live.get(f"/api/picking/waves/{wave}/execution")
        if not (preview.get("ready") or preview.get("completed")):
            raise CleanupStop(f"WAVE_NOT_READY_TO_FINISH:{str(preview)[:200]}")
        if preview.get("completed"):
            return  # already finished natively; nothing to send
        self.live.send("c.wave.finish", "POST", f"/api/picking/waves/{wave}/finish-execution", {"operation_id": f"{self.s['tag']}.C.WAVE.FINISH"})
        self.live.replay_equal("c.wave.finish")

    def own_stock_zero(self) -> None:
        ware = self.s["warehouse"]
        rows = self.live.read("select r.UID_POLETA,r.CELL,p.ARTICUL,r.BASE_UOM,r.STOCK_VERSION,r.REMAIN from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA "
                              "join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0", w=ware)
        reservations = self.live.one("select count(*) from RRL_STOCK_RESERVATION r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w "
                                     "and r.STATUS in('ACTIVE','ALLOCATED','PICKING') and r.BASE_QTY>0", w=ware)
        own = set((self.s.get("lots") or {}).values()) | {u for uids in (self.s.get("carrier_lots") or {}).values() for u in uids}
        findings = stock_findings(rows, reservations, own, self.t["expected_remainder_after_load"])
        self.c["stock_scope"] = {"rows": rows, "findings": findings}; self.live.save()
        if findings:
            raise CleanupStop("STOCK_SCOPE_REFUSED:" + ",".join(findings))  # nothing is counted when anything else is present
        counts = [{"uid": uid, "cell": cell, "article": article, "unit": unit, "quantity": "0", "expected_stock_version": int(version), "unit_keys": [
                    r[0] for r in self.live.read("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and CURRENT_CELL=:c and STOCK_STATUS='AVAILABLE'", u=uid, c=cell)]}
                  for uid, cell, article, unit, version, _ in rows]
        if counts:
            self.live.post("c0192.count.zero", "INVENTORY_COUNT", {"reason": "C0192 end isolated mixed tree after delivery", "counts": counts}, {"revision_id": self.s["revision"]})
        left = self.live.one("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w", w=ware)
        if Decimal(str(left[0])) != 0 or Decimal(str(left[1])) != 0:
            raise CleanupStop(f"WAREHOUSE_NOT_EMPTY_AFTER_CLEANUP:{left}")
        self.c["warehouse_final"] = {"remain": "0", "hard": "0"}; self.live.save()

    def retire(self) -> None:
        """K-0225: users, groups and rights are retired only through a durable, journaled owner finalizer with read-only reconciliation.
        C0190 does not expose one, so the companion stops here before any user/right mutation; the safe stages stay completed."""
        self.c["retire_pending"] = {"users": [self.t.get("driver_user"), self.t.get("receiver_user")], "receiver_group": (self.t.get("receiver_user") or "").upper(),
                                    "right": "store_receipt_confirm", "reason": "no durable journaled finalizer for RUSERS/RIGHTS"}
        self.live.save()
        raise CleanupStop("RETIRE_REQUIRES_DURABLE_OWNER_FINALIZER: cleanup incomplete; synthetic users/rights remain until the owner finalizer exists")

    def run(self) -> dict[str, Any]:
        findings = delivery_findings(self.s)
        if findings:
            raise CleanupStop("CLEANUP_REFUSED:" + ",".join(findings))
        for name, fn in (("tare_return", self.tare_return), ("tare_zero", self.tare_zero), ("binding_off", self.binding_off),
                         ("wave_finish", self.wave_finish), ("own_stock_zero", self.own_stock_zero), ("retire", self.retire)):
            self.step(name, fn)
        return {"status": "CLEANED", "warehouse": self.s["warehouse"], "steps": list(self.c["steps_done"])}  # not reached while retire() stops


def run(live: Any) -> dict[str, Any]:
    flow = MixedTreeCleanup(live)
    try:
        return flow.run()
    except RuntimeError as stop:
        flow.c["stopped"] = str(stop); live.save()
        return {"stopped": str(stop), "steps": list(flow.c["steps_done"])}
