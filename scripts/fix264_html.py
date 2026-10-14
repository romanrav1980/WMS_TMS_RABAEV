from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html");s=p.read_text(encoding="utf-8")
a=s.index('<article class="panel" data-permission="customer_rule_edit">\n<h2>Календарь')
b=s.index("</article>",a)+len("</article>")
section=s[a:b];s=s[:a]+s[b:];s=s.replace("</main>",section+"\n</main>",1)
print(json.dumps({str(p):s},ensure_ascii=True))
