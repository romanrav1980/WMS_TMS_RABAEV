from pathlib import Path
import json
p=Path('wiki/requirements/retailcase_delivery_v55/implementation_plan.json');d=json.loads(p.read_text(encoding='utf-8'));d['planRevision']=67;d['currentSprint']='NI08.1'
updates={
 'NI06.3':('Повреждение, двухсторонний возврат и независимое списание реализованы C0015; далее остаются варианты недостачи/спорного долга, которые нужно сопоставить с существующим UI, не писать заново. Внешняя и независимая приёмка отдельно.','reports/retailcase/2026-10-13/claude/C0015/report.md'),
 'NI07.2':('Обзор, переходы и до20 ID для16 backlog-показателей реализованы report56. Остаток: документы за производными stock/ERP/regulatory показателями и сквозное объяснение расхождений; ACK отдельно.','reports/retailcase/2026-10-13/56-ni072-documents-and-query-batching.md'),
 'NI08.1':('Интервалы нагрузки/рекомендации и scoped настройки реализованы reports54/57. Остаток: подтвердить конкретные ещё отсутствующие операторские пути слотов/ручного и автоматического допуска по действующим владельцам; каталог сотрудников пока ограничен500 на склад.','reports/retailcase/2026-10-13/57-ni081-scoped-configuration.md'),
 'NI02.2':('Тип адресата и переопределение, общая укладка и реальный выезд реализованы. Следующая доработка: ClaudeC0018 подключает серверные страницы200 в существующем диспетчере; SQL-страница и индекс1381 уже действуют. Широкая история ещё4–8с.','reports/retailcase/2026-10-13/53-ni022-st-page-index.md')}
for i in d['increments']:
 if i['id'] in updates:i['remainingDeliveryWork'],i['latestDeliveryReport']=updates[i['id']]
d['latestDelivery']={'reports':['54-ni081-workload-overview.md','55-ni051-case-next-step.md','56-ni072-documents-and-query-batching.md','57-ni081-scoped-configuration.md'],'claudeCompleted':'C0015/K0018','claudeNext':'coordination/retailcase-claude/TASK_C0018.md','note':'Не закрывает полную независимую/внешнюю приёмку; выполненные функции повторно не реализовывать.'}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=Path('wiki/requirements/retailcase_delivery_v55/implementation_plan.md');s=p.read_text(encoding='utf-8').replace('Редакция 66 ·','Редакция 67 ·');s=s.replace('Текущий блок NI06.2 — операторский путь товарного возврата.','Текущий блок NI08.1 — ограниченные настройки ресурсов; параллельно ClaudeC0018 — серверные страницы СТ.');s=s.replace('Дальше у него NI07.2. Задания: coordination/retailcase-claude/TASK_C0010.md.','NI07.2 затем сдан K-0016; C0015 повреждённой тары сдан K-0018. Текущее задание: coordination/retailcase-claude/TASK_C0018.md.');anchor='## Очерёдность сквозных блоков';extra='''### Дополнение редакции 67

Reports54–55: интервалы нагрузки и следующий шаг после закрытия CASE. Report56: документы backlog, два пакетных SQL вместо32 обращений, средние38–62мс; восстановление auth при временной ошибке и переходы с контекстом. Report57: выборка норм по группе и выходов по периоду, SQL8–34мс. Дополнительные индексы для этих быстрых запросов не нужны.

ClaudeC0015: повреждение1ед → возврат магазин–водитель–склад → независимое списание, повтор исходнымID один раз; итог склад4/магазин1GOOD, DAMAGED0. Новый C0018 подключает SQL-страницы200 к существующему диспетчеру без автоматической загрузки всей истории. Задача: [TASK_C0018](../../../coordination/retailcase-claude/TASK_C0018.md).

Эти блоки не считаются отсутствующими в remainingDeliveryWork. Полные спринты не закрываются по единичному успешному сценарию; ожидание реальных ERP/госсервисов/оборудования не является запретом продолжать код.

''';s=s.replace(anchor,extra+anchor,1);p.write_text(s,encoding='utf-8')