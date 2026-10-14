exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
from app.modules.fulfillment.public import build_customer_order_read_service
r=build_customer_order_read_service()
print(json.dumps([(x["customer_order_id"],x["order_no"]) for x in r.list("admin",before_id=1,limit=3)],ensure_ascii=True))
