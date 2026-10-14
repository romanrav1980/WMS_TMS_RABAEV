from pathlib import Path
p=Path('api/wms_api_server/app/modules/master_data/infrastructure/store_profile.py')
s=p.read_text(encoding='utf-8-sig').replace('fetch first 50 rows only','fetch first 57 rows only')
s=s.replace('windows = [{"weekday": d, "from_minute": f, "to_minute": t} for d, f, t in cur.fetchall()]','rows = cur.fetchall()\n    if len(rows) > 56:\n        raise StoreProfileError("STORE_PROFILE_WINDOW_BOUND_EXCEEDED", 409)\n    windows = [{"weekday": d, "from_minute": f, "to_minute": t} for d, f, t in rows]')
s=s.replace('where STORE_ADDR=:a for update",','where STORE_ADDR=:a for update wait 5",')
old='''            for window in windows:
                cur.execute("insert into RRL_STORE_RECEIVING_WINDOW(STORE_ADDR,WEEKDAY,FROM_MINUTE,TO_MINUTE) values(:a,:d,:f,:t)",
                            a=address, d=window["weekday"], f=window["from_minute"], t=window["to_minute"])'''
new='''            if windows:
                cur.executemany("insert into RRL_STORE_RECEIVING_WINDOW(STORE_ADDR,WEEKDAY,FROM_MINUTE,TO_MINUTE) values(:a,:d,:f,:t)",
                                [{"a": address, "d": w["weekday"], "f": w["from_minute"], "t": w["to_minute"]} for w in windows])'''
assert old in s
p.write_text(s.replace(old,new),encoding='utf-8')
