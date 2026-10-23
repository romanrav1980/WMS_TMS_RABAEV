"""C-0157: the NOT_APPLIED candidate functions executed unchanged as READ ONLY anonymous blocks on the live DB and compared with the
live (before) text on the same inputs: pool snapshot of real pool SKUs / the top-up warehouse, compile_wave_pool and topup compile_wave
on real waves. Only calls to the package's own functions are qualified so the text can run outside the package. No writes."""
import hashlib, json, pathlib, sys, time
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
M = pathlib.Path("C:/projects/TMS/db/migrations/2026-10-23_trade_topup_common_pool")
NL = "\n"


def part(file, start, end):
    s = (M / file).read_text(encoding="utf-8")
    return s[s.index(start):s.index(end)]


def snap_fn(file):
    return part(file, " function snapshot_json", NL + "end;").replace(
        "x:=json_object_t.parse(line_snapshot_json(", "x:=json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(")


def pool_fn(file):
    return part(file, " procedure compile_wave_pool", " procedure consume_wave_pool")


def adopt_fn(file):
    return (" procedure fail(p_code varchar2)is begin raise_application_error(-20911,p_code);end;" + NL
            + part(file, " procedure compile_wave(", " function split_units").replace("v:=line_proposal(", "v:=RRL_TRADE_TOPUP_ADOPT.line_proposal("))


def run(cur, block, **binds):
    t = time.perf_counter()
    try:
        cur.execute(block, **binds)
        err = None
    except oracledb.DatabaseError as e:
        err = str(e.args[0]).split(NL)[0]
    return err, round((time.perf_counter() - t) * 1000, 1)


def text(var):
    v = var.getvalue()
    return v.read() if hasattr(v, "read") else v


out = {"snapshot": {}, "line_proposal": {}, "waves": {}}
with OracleGateway().transaction("C-0157 candidate logic READ ONLY") as cur:
    cur.execute("set transaction read only")
    cur.execute("select WARE_ID,ARTICUL from RRL_RECEIPT_SKU_RULE where nvl(SHIP_FROM_STOCK,case STOCK_ALLOC_CLASS when 'DRY_RACK' then 1 else 0 end)=1")
    cases = cur.fetchall()
    cur.execute("select distinct ARTICUL from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=2200")
    cases += [(210564699, a) for (a,) in cur.fetchall()]
    for ware, art in cases:
        res, bodies = {}, {}
        for name, file in (("before", "before_rrl_stock_pool_read.sql"), ("after", "001_pool_read.sql")):
            v = cur.var(oracledb.DB_TYPE_CLOB)
            err, ms = run(cur, "declare" + NL + snap_fn(file) + NL + "begin :o:=snapshot_json(:w,:a);end;", o=v, w=ware, a=art)
            bodies[name] = None if err else text(v)
            res[name] = {"error": err, "ms": ms, "sha": bodies[name] and hashlib.sha256(bodies[name].encode()).hexdigest()}
        live = cur.var(oracledb.DB_TYPE_CLOB)
        cur.execute("begin :o:=RRL_STOCK_POOL_READ.snapshot_json(:w,:a);end;", o=live, w=ware, a=art)
        res["before_equals_live"] = res["before"]["sha"] == hashlib.sha256(text(live).encode()).hexdigest()
        res["after_equals_before"] = res["after"]["sha"] == res["before"]["sha"]
        if bodies["before"] and bodies["after"] and not res["after_equals_before"]:
            b, a = json.loads(bodies["before"]), json.loads(bodies["after"])
            res["changed_orders"] = [{"line_id": x["line_id"], "before": x["quantity"], "after": y["quantity"]} for x, y in zip(b["orders"], a["orders"]) if x != y]
            res["other_fields_equal"] = {k: v for k, v in b.items() if k != "orders"} == {k: v for k, v in a.items() if k != "orders"}
        out["snapshot"][f"{ware}:{art}"] = res
        print("snapshot", ware, art, res)
    cur.execute("select CUSTOMER_ORDER_ROW_ID from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=2200")
    for (row,) in cur.fetchall():
        v = cur.var(oracledb.DB_TYPE_NUMBER)
        cur.execute("begin :v:=RRL_TRADE_TOPUP_ADOPT.line_proposal(:r);end;", v=v, r=row)
        out["line_proposal"][row] = v.getvalue()
    print("line_proposal of order 2200 rows (proposal 10 CANCELLED):", out["line_proposal"])
    cur.execute("select PICK_WAVE_ID,WARE_ID from RRL_PICK_WAVE order by PICK_WAVE_ID desc fetch first 12 rows only")
    for wave, ware in cur.fetchall():
        w = {}
        for name, file in (("before", "before_rrl_stock_pool_cmd.sql"), ("after", "002_pool_cmd.sql")):
            r_, p_ = cur.var(oracledb.DB_TYPE_CLOB), cur.var(oracledb.DB_TYPE_CLOB)
            err, ms = run(cur, "declare" + NL + "rr json_array_t:=json_array_t();pp json_array_t;" + NL + pool_fn(file) + NL
                          + "begin compile_wave_pool(:w,:v,rr,pp);:r:=rr.to_clob;:p:=pp.to_clob;end;", w=ware, v=wave, r=r_, p=p_)
            w["pool_" + name] = [err, None if err else text(r_), None if err else text(p_), ms]
        for name, file in (("before", "before_rrl_trade_topup_adopt.sql"), ("after", "003_topup_adopt.sql")):
            r_ = cur.var(oracledb.DB_TYPE_CLOB)
            err, ms = run(cur, "declare" + NL + "rr json_array_t:=json_array_t();" + NL + adopt_fn(file) + NL
                          + "begin compile_wave(:v,rr);:r:=rr.to_clob;end;", v=wave, r=r_)
            w["adopt_" + name] = [err, None if err else text(r_), ms]
        out["waves"][wave] = {"pool_same": w["pool_before"][:3] == w["pool_after"][:3], "pool_error": w["pool_after"][0], "pool_ms": w["pool_after"][3],
                              "adopt_same": w["adopt_before"][:2] == w["adopt_after"][:2], "adopt_error": w["adopt_after"][0], "adopt_ms": w["adopt_after"][2]}
        print("wave", wave, out["waves"][wave])
pathlib.Path(__file__).parent.parent.joinpath("candidate-logic-live.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
