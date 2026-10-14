from pathlib import Path
p=Path('reports/nicora/2026-10-13/65-ni051-scoped-quality.md')
with p.open('a',encoding='utf-8') as f:f.write('''

## Дополнение: реальный storage-only допуск

Ведомый выполнил native сценарий f9734885e0: SAP receipt3EA → размещение1169 → fullpal pick1168 → binding → QC PLAN QCF1.PLAN:f9734885e0, ready=true, одно основание EXEMPT_FACT, точный повтор. ST641516/fulfillment188. Собственные P/H очищены прежним Root, правило выключено; исторический аудит сохранён. Native lookup4.762мс/5исполнений, INVALID[]. Evidence: codex/QC_F1/native_fixture.json. Ошибка чтения dict какLOB в сценарном скрипте исправлена; повтор подтверждён по сохранённому результату, новая проводка не создавалась.

Печать дополняется явным условием weight_exemption_recorded для текущей подписи состава. GET не создаёт факт: сначала существующее «Предъявить к контролю», затем этикетка. Без сохранённого основания409; при подтверждении200. scripts/case1473_label_audit.py проверяет ветви на stub-снимке и HTML escaping, без Oracle-записей. На этикетке показываются понятное основание и исходная приёмка. Native поле/индекс ведомый завершает отдельно.
''')
