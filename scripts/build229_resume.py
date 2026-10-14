from pathlib import Path
import json
s=Path("scripts/ni053_marked_recipient_case.py").read_text(encoding="utf-8");prefix=s[:s.index(' preview=')]
scan=s[s.index(' q.execute("select SYSTEM_CODE'):s.index(' body=')]
middle=' q.execute("select OPERATION_ID,CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID like \'STORE229.RECEIVE:%\'and STATE=\'APPLIED\'");op,raw=q.fetchone();canonical=read_oracle_json(raw);winner={"operation_id":op,**canonical["source"],**canonical["metadata"]};winner.pop("unit_scans");winner["scans"]=scans;saved=api(client,"POST",path+"/confirm",winner)\n'
tail=s[s.index(' q.execute("delete from RRL_STORE_RECEIPT_USER'):].replace(' q.execute("delete from RRL_STORE_RECEIPT_USER where USER_ID=:a and STORE_ADDR=:s",a=actor,s=addr);c.commit()', ' q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])\n try:q.execute("delete from RRL_STORE_RECEIPT_USER where USER_ID=:a and STORE_ADDR=:s",a=actor,s=addr);c.commit()\n finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")')
order=' q.execute("select CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=641362");order=q.fetchone()[0]\n'
print(json.dumps({"scripts/resume229_case.py":prefix+scan+middle+order+tail},ensure_ascii=True))
