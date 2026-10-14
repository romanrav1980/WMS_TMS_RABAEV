from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.js");t=p.read_text(encoding="utf-8")
a='      <td>${escapeOrder(row.status)}</td>\n    </tr>';assert a in t
b="""      <td>${escapeOrder(row.status)}${row.unit_code === "KG" && orderCan("pick_plan_create") ? '<br><button type="button" data-weight-row="' + escapeOrder(row.customer_order_row_id) + '">Целые коробки</button>' : ""}</td>
    </tr>"""
t=t.replace(a,b,1)
tick=chr(96)
a="throw new Error((payload && payload.detail) || "+tick+"HTTP ${response.status}"+tick+");"
b="throw new Error((payload && (payload.detail?.message || payload.detail?.code || payload.detail)) || "+tick+"HTTP ${response.status}"+tick+");"
assert a in t;t=t.replace(a,b)
out[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");t=p.read_text(encoding="utf-8");a='<script src="stock-pool.js"></script>';assert a in t
out[str(p)]=t.replace(a,a+'<script src="weighted-plan-choice.js"></script>')
print(json.dumps(out,ensure_ascii=True))
