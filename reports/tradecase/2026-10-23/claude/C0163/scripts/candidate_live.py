"""C-0163 READ ONLY proofs on the live DB with the candidate's own SQL (the new tables do not exist yet, so the parts are given as rows of a
WITH clause shaped like RRL_TRADE_SUPPLY_PART):
1) the native codes hash (json_table over each part's CODES_JSON, ordered by PART_NO then position, joined by LF, SHA-256) equals the
   sender rule in Python (contracts_supply_parts.codes_sha256) for parts that arrived in the order 2, 3, 1;
2) the missing-parts query of state() lists exactly the absent numbers.
No writes: READ ONLY transaction."""
import json, pathlib, sys
sys.path.insert(0, 'C:/projects/TMS/scripts'); sys.path.insert(0, 'C:/projects/TMS/api/wms_api_server')
from stock_posting_environment import load_local_oracle_environment; load_local_oracle_environment()
import oracledb
from app.oracle_gateway import OracleGateway
from app.modules.integrations.contracts_supply_parts import codes_sha256

codes = [f"010460000000000121{n:04d}abc" for n in range(1, 8)]
parts = {1: codes[0:3], 2: codes[3:5], 3: codes[5:7]}
arrival = [2, 3, 1]
rows = " union all ".join(f"select {p} PART_NO,'{json.dumps([{'system_code': 'CRPT', 'profile_code': 'TOBACCO', 'code': c} for c in parts[p]])}' CODES_JSON from dual" for p in arrival)
HASH = ("declare joined clob;first boolean:=true;begin dbms_lob.createtemporary(joined,true);"
        " for c in(with p as(" + rows + ") select x.CODE from p,json_table(p.CODES_JSON,'$[*]'columns(SEQ for ordinality,CODE varchar2(4000)path'$.code'))x order by p.PART_NO,x.SEQ)loop"
        " if not first then dbms_lob.writeappend(joined,1,chr(10));end if;dbms_lob.append(joined,c.CODE);first:=false;end loop;"
        " :h:=lower(rawtohex(sys.dbms_crypto.hash(joined,sys.dbms_crypto.hash_sh256)));end;")
MISSING = ("select level PART_NO from dual connect by level<=:cnt minus select PART_NO from(select 2 PART_NO from dual union all select 5 from dual) order by 1")
out = {}
with OracleGateway().transaction("C-0163 candidate READ ONLY") as cur:
    cur.execute("set transaction read only")
    h = cur.var(oracledb.DB_TYPE_VARCHAR); cur.execute(HASH, h=h)
    out["native_codes_sha256"], out["python_codes_sha256"] = h.getvalue(), codes_sha256(codes)
    out["hash_equal"] = out["native_codes_sha256"] == out["python_codes_sha256"]
    cur.execute(MISSING, cnt=6); out["missing_of_6_with_2_and_5"] = [r[0] for r in cur.fetchall()]
print(out)
pathlib.Path(__file__).parent.parent.joinpath("candidate-live.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
