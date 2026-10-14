from pathlib import Path
import json
root=Path('wiki/requirements/retailcase_delivery_v55');p=root/'implementation_plan.json';d=json.loads(p.read_text(encoding='utf-8'));d['planRevision']=68;d['currentSprint']='NI03.2';d['currentSprintMeaning']='Codex ведёт складское исполнение; первый блок цепочки заданий W1406–1408 выполнен. Claude: коррекции C0021 после C0018, затем C0020.'
d['jointExecutionPlan']='wiki/requirements/retailcase_joint_execution_20261014.md'
codex=['NI01.1','NI03.2','NI03.3','NI04.1','NI04.2','NI04.3','NI05.1','NI05.2','NI07.2'];claude=['NI02.2','NI05.3','NI06.1','NI06.2','NI06.3','NI07.1','NI08.1']
for i in d['increments']:
 if i['id']in codex:i['deliveryOwner']='Codex'
 elif i['id']in claude:i['deliveryOwner']='Claude Code';i['serverContractOwner']='Codex'
 else:i['deliveryOwner']='Reuse verified foundation'
 if i['id']=='NI03.2':
  i['latestDeliveryReport']='reports/retailcase/2026-10-13/59-ni032-task-family.md'
  i['remainingDeliveryWork']='Цепочка этапов/факт/остаток/исполнитель/следующее задание в UI реализованы report59. Далее операторские продолжения недостачи и смены исполнителя по существующим командам; не повторять готовые механизмы.'
 if i['id']=='NI02.2':i['remainingDeliveryWork']='ClaudeC0018 сдан: страницы200/серверный склад/ошибка без демо. При review найдены C0021: составной ключ строк и немедленное удаление старого выбора при смене query. Широкая история и clusters отдельно; индекс1381 готов.'
d['parallelAssignment']={'claudeActive':'C0021 corrections requested; ACK pending','claudeQueued':'C0020 after RELEASE','codexActive':'NI03.2/NI03.3 warehouse execution','channel':'coordination/retailcase-claude','noSharedFileWrites':True}
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'implementation_plan.md';s=p.read_text(encoding='utf-8').replace('Редакция 67 ·','Редакция 68 ·');anchor='## Правила исполнения';s=s.replace(anchor,'''## Распределение исполнения — 14.10.2026

[Совместный план Codex / Claude Code](../retailcase_joint_execution_20261014.md): пять этапов,9открытых спринтов ведётCodex,7—Claude. Код/Oracle/общиеAPI уCodex; текущие UI-файлыClaude закрепляются отдельнымACK.

Начато: CodexNI03.2, report59 — видимая цепочка заданий633→634 и следующий этап, без новых проводок/SQL. ClaudeC0018 сдан, до принятия осталосьC0021 (составной ключ строк/очистка выбора при новом фильтре), затем автоматическиC0020 (недостача тары). Последующий порядок: отбор/контроль + доставка → приёмка/отгрузка + возвраты → сверка/финансы → ресурсы.

'''+anchor,1);p.write_text(s,encoding='utf-8')
p=Path('wiki/requirements/retailcase_joint_execution_20261014.md');s=p.read_text(encoding='utf-8').replace('Claude: C0018 уже ACK K0019. После RESULT/RELEASE автоматически перейти к','Claude: C0018 сдан K0020; перед дальнейшей передачей исправить C0021 (составной ключ и старый выбор при смене фильтра). Затем автоматически перейти к').replace('Codex: W1406 / NI03.2 — видимая цепочка','Codex: W1406–1408 / NI03.2 выполнен, report59 — видимая цепочка');p.write_text(s,encoding='utf-8')