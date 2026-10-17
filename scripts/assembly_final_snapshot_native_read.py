"""Explicit read-only native ASM_FINAL context acceptance after root applies kit."""
import argparse
import json
from pathlib import Path
import sys
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from warehouse_task_scoped_complete_smoke import OracleGateway,read_oracle_json


def read(g,actor):
    with g.transaction('Read current ASM_FINAL context only')as c:
        out=c.var(oracledb.DB_TYPE_CLOB);c.callproc('RRL_ASSEMBLY_SCALE_API.context',[1136,actor,out]);return read_oracle_json(out.getvalue())


def run():
    g=OracleGateway();marker=g.fetch_all('select nvl(max(LOG_ID),0)N from RRL_SQL_SLOW_LOG')[0]['n']
    before=g.fetch_all("select OPERATION_ID,STATE from RRL_STOCK_OPERATION where OPERATION_ID='WHREQ15.ASM.PICK1136'")
    first=read(g,'WHREQ15.OP');second=read(g,'WHREQ15.OP')
    for value in[first,second]:
        assert value['final_signature_domain']=='ASM_FINAL'and value['final_signature_version']==3
        assert len(value['final_composition_signature'])==64
    assert first['final_composition_signature']==second['final_composition_signature']
    try:read(g,'WHREQ15.GW')
    except oracledb.DatabaseError as error:foreign=str(error).splitlines()[0]
    else:raise AssertionError('Foreign sender must not read operator context')
    after=g.fetch_all("select OPERATION_ID,STATE from RRL_STOCK_OPERATION where OPERATION_ID='WHREQ15.ASM.PICK1136'");assert after==before
    report=dict(status='PASS',domain='ASM_FINAL',version=3,signature=first['final_composition_signature'],repeated_context_equal=True,foreign_refusal=foreign,stock_operations_unchanged=True,physical_hardware=False,slow_sql=g.fetch_all('select *from(select LOG_ID,ELAPSED_MS,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:marker order by ELAPSED_MS desc)where rownum<=10',{'marker':marker}))
    (ROOT/'reports/retailcase/2026-10-15/assembly-scale/final-snapshot-native-read.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');print(json.dumps(report,default=str))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute-read',action='store_true');args=parser.parse_args()
    if not args.execute_read:print('PREPARED_ONLY: wait for native kit apply');return
    run()


if __name__=='__main__':main()

