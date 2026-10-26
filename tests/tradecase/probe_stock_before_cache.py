"""Compare immutable before-image lookup implementations on native Oracle."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection


def run():
    body=(ROOT/'db/migrations/2026-10-26_stock_verify_snapshot/001_body.sql').read_text(encoding='utf-8')
    declarations=body.split('  type quantity_map',1)[1].split('\n begin',1)[0]
    parse=body.split('  -- Parse the immutable',1)[1].split('\n  for r in(select distinct',1)[0]
    parse='  -- Parse the immutable'+parse
    cases=[[],[dict(uid='A',balances=[])],
           [dict(uid='A',balances=[dict(cell='X',p='1.25'),dict(cell='X',p='2.5'),dict(cell='OLD',p='-0.125')]),dict(uid='a',balances=[dict(cell='X',p='8')])],
           [dict(uid='A',balances=[dict(cell='X',p=None),dict(cell=None,p='9')]),dict(uid=None,balances=[dict(cell='X',p='5')])]]
    block='declare\n p_before clob:=:payload;v_uid varchar2(200);actual number;expected number;\n type quantity_map'+declarations+'\n begin\n'+parse+"""
      for u in(select column_value uid_value from table(sys.odcivarchar2list('A','a','MISSING')))loop
       v_uid:=u.uid_value;
       for c in(select column_value cell from table(sys.odcivarchar2list('X','OLD','NEW',null)))loop
        actual:=0;
        if c.cell is not null then
         balance_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('VERIFY_BAL',v_uid,c.cell));
         if before_qty.exists(balance_key)then actual:=before_qty(balance_key);end if;
        end if;
        select nvl(sum(to_number(j.qty,'999999999999999999999999999999D999999999','NLS_NUMERIC_CHARACTERS=''.,''')),0)
        into expected from json_table(p_before,'$[*]' columns(uid_value varchar2(200)path '$.uid',
        nested path '$.balances[*]'columns(cell varchar2(60)path '$.cell',qty varchar2(100)path '$.p')))j
        where j.uid_value=v_uid and j.cell=c.cell;
        if actual!=expected then raise_application_error(-20001,'CACHE_QUANTITY_MISMATCH');end if;
       end loop;
       uid_key:=rawtohex(RRL_STOCK_LOCK_API.resource_key('VERIFY_UID',v_uid));cell_values:=sys.odcivarchar2list();
       if before_cells.exists(uid_key)then cell_values:=before_cells(uid_key);end if;
       select count(*) into actual from(
        (select column_value from table(cell_values) minus select j.cell from json_table(p_before,'$[*]'columns(uid_value varchar2(200)path '$.uid',nested path '$.balances[*]'columns(cell varchar2(60)path '$.cell')))j where j.uid_value=v_uid and j.cell is not null)
        union all
        (select j.cell from json_table(p_before,'$[*]'columns(uid_value varchar2(200)path '$.uid',nested path '$.balances[*]'columns(cell varchar2(60)path '$.cell')))j where j.uid_value=v_uid and j.cell is not null minus select column_value from table(cell_values)));
       if actual!=0 then raise_application_error(-20002,'CACHE_CELL_MISMATCH');end if;
      end loop;
     end;"""
    with oracle_connection()as conn:
        cur=conn.cursor()
        for case in cases:cur.execute(block,payload=json.dumps(case))
        conn.rollback()
    report=dict(status='PASS',cases=len(cases),quantity_comparisons=48,scope='Anonymous native cache prototype; no business writes')
    out=ROOT/'runtime/test-evidence/tradecase/2026-10-26/T08/carton-scale/before-cache-prototype.json'
    assert not out.exists();out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))


if __name__=='__main__':run()
