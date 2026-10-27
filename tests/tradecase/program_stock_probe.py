"""Read-only balance, eligible-place window and SQL measurements for the owned program fixture."""
from datetime import date
import json
from pathlib import Path
import re
import sys
import time

sys.path.insert(0, str(Path(__file__).parent))
import live_program_orders as p


def run():
    label = sys.argv[1]
    assert re.fullmatch('[a-z0-9-]+', label)
    output = p.q.OUT/('stock-'+label+'.json')
    assert not output.exists(), 'Preserve previous evidence'
    report = dict(scope='Owned program stock, one READ ONLY snapshot', timings={})
    with p.q.oracle_connection() as conn:
        cur = conn.cursor(); cur.execute('set transaction read only')
        cur.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
        assert cur.fetchone() == ('RABAEV', 'orcl')
        cur.execute('select p.ARTICUL,count(*),sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where c.WARE_ID=:w group by p.ARTICUL order by p.ARTICUL', w=p.s['fixture']['warehouse_id'])
        report['stock'] = cur.fetchall()
        for name, sku in p.s['skus'].items():
            started = time.perf_counter()
            cur.execute('select RRL_TRADE_TOPUP_READ.eligible_units(:w,:a,:s,\'SNS\',:m,:d,10) from dual', w=p.s['fixture']['warehouse_id'], a=sku['article'], s=name, m=int(sku['mrc']), d=date.today())
            report[name] = cur.fetchone()[0]
            report['timings'][name] = round((time.perf_counter()-started)*1000, 2)
        cur.execute("select count(*) from USER_OBJECTS where STATUS='INVALID'")
        report['invalid'] = cur.fetchone()[0]
        cur.execute('select LOG_ID,ELAPSED_MS,OPERATION_KIND,substr(SQL_TEXT,1,300) from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 10 rows only', m=p.s['fixture']['slow_marker'])
        report['slow_sql'] = cur.fetchall()
        conn.rollback()
    output.write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')
    print(json.dumps(report, default=str))


if __name__ == '__main__':
    run()
