"""Wait for Oracle SYS login, without printing credentials or mutating a database."""
import argparse
import os
import time
import oracledb


def wait(timeout):
    deadline = time.monotonic() + timeout
    last_code = None
    while time.monotonic() < deadline:
        try:
            with oracledb.connect(user='SYS', password=os.environ['RETAIL_ORACLE_SYS_PASSWORD'],
                                  dsn=os.environ['RETAIL_ORACLE_ADMIN_DSN'], mode=oracledb.SYSDBA,
                                  tcp_connect_timeout=5) as c:
                c.call_timeout = 5000
                q = c.cursor()
                q.execute("select sys_context('USERENV','CON_NAME') from dual")
                print('Oracle ready:', q.fetchone()[0])
                return
        except oracledb.Error as e:
            last_code = getattr(e.args[0], 'code', None)
            if last_code in (1017, 28000, 28001):
                raise RuntimeError('Oracle credentials rejected (code '+str(last_code)+')') from None
            time.sleep(5)
    raise RuntimeError('Oracle login timeout; last error code '+str(last_code))


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--timeout',type=int,default=600)
    wait(p.parse_args().timeout)
