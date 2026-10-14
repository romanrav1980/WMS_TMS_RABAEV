from pathlib import Path
import json
p=Path('wiki/requirements/nikora_delivery_v55/implementation_plan.json');d=json.loads(p.read_text(encoding='utf-8'))
for i in d['increments']:
 if i['id']=='NI07.2':
  i['remainingDeliveryWork']='Обзор, переходы и bounded ID для16 backlog и3 внешних показателей реализованы reports56/58. Остаток: ключи строк за конфликтами stock и сквозное объяснение расхождений; ACK отдельно.'
  i['latestDeliveryReport']='reports/nicora/2026-10-13/58-ni072-external-document-links.md'
if '58-ni072-external-document-links.md' not in d['latestDelivery']['reports']:d['latestDelivery']['reports'].append('58-ni072-external-document-links.md')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('wiki/requirements/nikora_delivery_v55/implementation_plan.md');s=p.read_text(encoding='utf-8');s=s.replace('### Дополнение редакции 67\n','### Дополнение редакции 67\n\nReport58: конкретные ERP/регуляторные сообщения сверки, до20ID и прямое existing outbox-досье без всей очереди; SQL8–22мс. Неподтверждённый внешний ACK остаётся отдельным статусом.\n',1);p.write_text(s,encoding='utf-8')