"""C-0160: the NOT_APPLIED candidate executed unchanged as READ ONLY anonymous blocks on the live DB.
1) snapshot_json of the candidate with the candidate pick-context functions inlined (enter_line, check_source, compatible), on the trade
   warehouse 210564699 and on the non-trade pool SKUs (must equal the live snapshot there);
2) prove_trade of the candidate pool command against synthetic plans (accepted / incompatible / overallocated / bad split / reason>0).
No writes: the transaction is READ ONLY."""
import hashlib, json, pathlib, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
K = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_pool_eligibility")
NL = "\n"


def part(file, start, end):
    s = (K / file).read_text(encoding="utf-8")
    return s[s.index(start):s.index(end)]


CTX = (part("002_ctx_body.sql", " g_line RRL_TRADE_ORDER_LINE%rowtype", " function has_line")
       + part("002_ctx_body.sql", " function check_source(", " function reason(")
       + part("002_ctx_body.sql", " function compatible(", NL + "end;"))
SNAP = part("003_pool_read.sql", " function snapshot_json", NL + "end;").replace(
    "x:=json_object_t.parse(line_snapshot_json(", "x:=json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(").replace(
    "RRL_TRADE_PICK_CONTEXT.compatible(", "compatible(")
BEFORE_SNAP = part("before_pool_read.sql", " function snapshot_json", NL + "end;").replace(
    "x:=json_object_t.parse(line_snapshot_json(", "x:=json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(")
PROVE = (" function nonnegative(p_text varchar2) return number is" + NL + " begin if p_text='0' then return 0;end if;return RRL_STOCK_MATH.quantity(p_text);end;" + NL
         + part("004_pool_cmd.sql", " procedure prove_trade(", " procedure compile_command("))


def clob(v):
    x = v.getvalue()
    return x.read() if hasattr(x, "read") else x


out = {"snapshots": {}, "prove": {}}
with OracleGateway().transaction("C-0160 candidate READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select WARE_ID,ARTICUL from RRL_RECEIPT_SKU_RULE where nvl(SHIP_FROM_STOCK,case STOCK_ALLOC_CLASS when 'DRY_RACK' then 1 else 0 end)=1")
    cases = cur.fetchall() + [(210564699, "TC03089DDB36")]
    # Harness only: the same candidate with the article's pool policy forced on (root restored SHIP_FROM_STOCK=0 after its run), to show
    # real source classes and row compatibility. Nothing is written; the forced value lives only inside this anonymous block.
    anchor = "exception when no_data_found then null;end;" + NL + "  select BASE_UOM into base"
    assert SNAP.count(anchor) == 1
    FORCED = SNAP.replace(anchor, "exception when no_data_found then null;end;enabled:=1;" + NL + "  select BASE_UOM into base")
    for ware, art in cases:
        row = {}
        for name, fn, ctx in (("after", SNAP, CTX), ("before", BEFORE_SNAP, ""), ("forced_pool", FORCED, CTX)):
            v = cur.var(oracledb.DB_TYPE_CLOB); t = time.perf_counter()
            try:
                cur.execute("declare" + NL + ctx + fn + NL + "begin :o:=snapshot_json(:w,:a);end;", o=v, w=ware, a=art)
                body = clob(v); row[name] = {"ms": round((time.perf_counter() - t) * 1000, 1), "sha": hashlib.sha256(body.encode()).hexdigest()}
                if name in ("after", "forced_pool"):
                    j, pre = json.loads(body), ("" if name == "after" else "forced_")
                    row[pre + "trade"] = j.get("trade"); row[pre + "classes"] = j.get("classes"); row[pre + "available"] = j.get("available")
                    row[pre + "stocks"] = [{k: s.get(k) for k in ("uid", "free", "reason", "class")} for s in j["stocks"]][:20]
                    row[pre + "orders"] = [{k: o.get(k) for k in ("line_id", "quantity", "classes", "pool_reason")} for o in j["orders"]][:20]
            except oracledb.DatabaseError as e:
                row[name] = {"error": str(e.args[0]).split(NL)[0], "ms": round((time.perf_counter() - t) * 1000, 1)}
        row["same_as_before"] = row["after"].get("sha") == row["before"].get("sha")
        out["snapshots"][f"{ware}:{art}"] = row
        print(ware, art, json.dumps({k: row[k] for k in ("trade", "available", "classes", "orders", "same_as_before", "forced_available", "forced_classes", "forced_orders") if k in row}, ensure_ascii=False)[:2500], row["after"].get("error"))

    snapshot = {"trade": 1, "classes": [{"key": "SNS|A|200|2027-01-01", "owner": "SNS", "free": "30"}, {"key": "BLC|A|250|2027-01-01", "owner": "BLC", "free": "10"}],
                "orders": [{"line_id": 1, "quantity": "20", "classes": ["SNS|A|200|2027-01-01"]}, {"line_id": 2, "quantity": "15", "classes": ["BLC|A|250|2027-01-01"]},
                           {"line_id": 3, "quantity": "5", "classes": [], "pool_reason": "TRADE_ORDER_BINDING_STALE"}]}
    plans = {
        "accepted": ({"1": "20", "2": "10", "3": "0"}, {"1": {"SNS|A|200|2027-01-01": "20"}, "2": {"BLC|A|250|2027-01-01": "10"}}),
        "incompatible_class": ({"1": "20", "2": "10", "3": "0"}, {"1": {"BLC|A|250|2027-01-01": "20"}, "2": {"BLC|A|250|2027-01-01": "10"}}),
        "class_overallocated": ({"1": "20", "2": "15", "3": "0"}, {"1": {"SNS|A|200|2027-01-01": "20"}, "2": {"BLC|A|250|2027-01-01": "15"}}),
        "split_mismatch": ({"1": "20", "2": "10", "3": "0"}, {"1": {"SNS|A|200|2027-01-01": "15"}, "2": {"BLC|A|250|2027-01-01": "10"}}),
        "reason_row_allocated": ({"1": "20", "2": "10", "3": "5"}, {"1": {"SNS|A|200|2027-01-01": "20"}, "2": {"BLC|A|250|2027-01-01": "10"}, "3": {"SNS|A|200|2027-01-01": "5"}}),
        "missing_sources": ({"1": "20", "2": "10", "3": "0"}, None),
    }
    for name, (alloc, sources) in plans.items():
        hints = {"allocations": alloc, **({"sources": sources} if sources is not None else {})}
        try:
            cur.execute("declare" + NL + PROVE + NL + "begin prove_trade(json_object_t.parse(:s),json_object_t.parse(:h),1);end;", s=json.dumps(snapshot), h=json.dumps(hints))
            out["prove"][name] = "ACCEPTED"
        except oracledb.DatabaseError as e:
            out["prove"][name] = str(e.args[0]).split(NL)[0]
        print("prove", name, out["prove"][name])
pathlib.Path(__file__).parent.parent.joinpath("candidate-live.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
