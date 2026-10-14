from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_demand")
t=(f/"000_before_pool.sql").read_text(encoding="utf-8")
t=t.replace("qty number;requested number;hard_qty number;","qty number;requested number;waived_qty number;hard_qty number;",1)
a="   requested:=qty;qty:=greatest(0,qty-hard_qty-greatest(0,picked_qty-picked_hard));"
assert t.count(a)==1
t=t.replace(a,"   requested:=qty;waived_qty:=RRL_WEIGHT_DEVIATION_READ.waived_line(o.CUSTOMER_ORDER_ROW_ID);qty:=greatest(0,qty-hard_qty-greatest(0,picked_qty-picked_hard)-waived_qty);")
a="  x.put('quantity_semantics','UNALLOCATED_BASE_NOT_SHIPPED_PROOF');";assert a in t
t=t.replace(a,"  x.put('accepted_weight_deviation_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(waived_qty));\n  x.put('quantity_semantics',case when waived_qty>0 then 'UNALLOCATED_BASE_AFTER_ACCEPTED_WEIGHT_DEVIATION'else 'UNALLOCATED_BASE_NOT_SHIPPED_PROOF'end);")
out[str(f/"002_pool.sql")]=t
out[str(f/"apply.sql")]="@@001_waiver.sql\n@@002_pool.sql\n"
out[str(f/"rollback.sql")]="@@000_before_pool.sql\ndrop package RRL_WEIGHT_DEVIATION_READ;\n"
out["wiki/database/nicora_ni042_weight_demand_design_20261011.md"]="""# NI04.2: потребность после принятого отклонения массы
193 pure reader extends original pool math only: remaining = original - HARD - nonoverlapping physically picked - accepted current weight deviation. No P/H/domain writes. Immutable192 history retained; current accepted short/PT DONE/CASE notcancelled/operationAPPLIED required. Original whole order-SKU requested KG must still equal frozen approval, current actual whole SKU remains within frozen pct. Own-line waiver capped by original own requested minus current actual. Returned/cancelled CASE/PT removes waiver automatically and original demand reopens. New card policy does not retroactively rewrite accepted commercial agreement; original quantities/return source changes invalidate.
Readers bounded200 original rows/2000 PT/200 accepted decisions. Ordinary SKU fast no matching accepted decision returns0. No global full-order close/status change. Lastbox over-plan exception remains separate.
"""
for name,line in [("wiki/index.md","- [Потребность после принятого отклонения: разработка](database/nicora_ni042_weight_demand_design_20261011.md):193 pure current waiver/return-aware original pool math; no stock write."),
("wiki/log.md","2026-10-11:193 begins from fresh live pool contract/checkpoint; accepted192 deviation applies only current fulfilled source/frozen order mass window, return removes waiver; original stock owner unchanged.")]:
 p=Path(name);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
