from pathlib import Path
import json
files={}
report="reports/nicora/2026-10-13/45-b02-marked-picking-terminal.md"
files[report]="""# B02: маркированный отбор через существующий ТСД
14.10.2026, RABAEV/orcl. Собственная dev-фикстура, авторская адресная проверка.

## Функционал
- Поля кодов формируются для всех применимых профилей карточки SKU. Обычный CASE больше не ограничен одним переключаемым профилем. Коды и управляющие разделители сохраняются; пустой профиль, повтор внутри профиля и разное число кодов останавливают отправку.
- Весовая серийная коробка сохраняет отдельный существующий weighted-box вход. Для немаркированного товара на развес UI требует архивное NET-показание и использует существующий weigh-line; ручной накопленный факт заблокирован.
- Подсказка показывает последовательность сканов и способ отбора. Накопленный факт явно обозначен; количество отображается существующим точным formatter без Number/toFixed(3).
- Сохранённый отбор проверяет контекст пользователя/API, неизменность локального запроса, operation/task/line в ответе. Повреждённый запрос блокирует новую отправку и архивируется явно.
- Закрытие CASE использует уже существующий metadata journal с operation_id и expected_content_version. Потерянный ответ повторяется с исходным телом; закрытое место не предлагается закрывать заново. Это не новая товарная проводка.

## Реальное выполнение
Создан отдельный тестовый SKU QPB12941294AB01 с двумя искусственно совмещёнными профилями CRPT/TOBACCO и EGAIS/ALCOHOL для проверки нескольких профилей одной физической единицы. Это тест интерфейса и локального реестра, не заявление о реальной применимости двух государственных систем к одному товару.
SAP-совместимый dev-вход → приёмка12EA/12 физических единиц/24кода → DIRECT план2192/волна560 → CASE1134/строка1137, заказ2139.
ТСД430px отобрал5EA с10кодами. Без EGAIS-профиля сетевого POST не было. Реальный ответ проведённой команды был намеренно потерян на клиенте; после перезагрузки кнопка повтора отправила тот же body/operation_id. Backend вернул сохранённый результат.
Операция CASE.PICK.UI:c0ca94f9-5f11-4940-9030-1ba3c7a4e2b8 — одна APPLIED запись. Источник7EA/H0, CASE5EA/H5; суммарный запас12/H5. Физические единицы7+5; исходный реестр24кода сохранился, два профиля не удвоили товар.
Закрытие CASE.CLOSE.UI:741441c5-7700-41a9-8947-e7c6e518512c → WAIT_CONTROL/version1/physical_stock_changed=false. Следующий этап этой фикстуры — привязка к СТ/контроль и отгрузка; не объявлен выполненным.

## Проверка и ограничения
UI реальный,0page errors. Проверка ручного ввода для реальной сохранённой NET-политики CASE1064 сначала обнаружила промежуточное включение поля при повторной загрузке политики; поле теперь блокируется на всё время чтения. Отдельное чтение текущей NET-политики подтвердило disabled=true; товар CASE1064 не менялся.
Скриншоты: [профили](screenshots/82-b02-multiple-profiles.png), [отобрано5](screenshots/83-b02-picked.png), [закрытие](screenshots/84-b02-case-closed.png).
SQL resolver101nar4b5fyzn:216.927мс/389buffers за одно холодное исполнение; текущие резервные lookups24.401мс/76buffers и9.216мс/122buffers за3исполнения. Решение: сохранить batch500/existing indexed reservation scope; новую индексацию без повторного медленного плана не добавлять. Владелец inventory, повторный анализ при регулярном>500мс/пилоте.
Нет реальных государственных ACK, промышленной проверки сканера/весов, независимой приёмки. Внешние статусы остаются отдельными. Общий NI04.2/NI04.3 остаётся открыт для остальных применимых сценариев.
"""
page="wiki/components/nicora_b02_terminal_profiles_20261014.md"
files[page]="# B02: ТСД для нескольких профилей маркировки\n\n1292–1300. Существующий case-pick-tsd использует поля каждого текущего профиля SKU, отдельные weighted-box/weigh-line пути, точные количества, сохранённый повтор и existing CASE close journal. Нового реестра/товарного исполнителя нет.\n\nActual CASE1134/order2139/wave560:12EA приняты,5EA/10кодов отобраны, потерянный ответ→точный replay, одна APPLIED операция; источник7/CASE5/P12H5. WAIT_CONTROL, дальнейшая отгрузка не выполнена. [Отчёт45](../../"+report+").\n\nВнешние ACK/весы/сканер/independent acceptance не подтверждены. Прочие методы NI04.2 и регуляторные сценарии остаются открытыми; существующие native владельцы сохраняются.\n"
p=Path("wiki/index.md");files[str(p)]="- [B02: маркированный отбор1300](components/nicora_b02_terminal_profiles_20261014.md):CASE1134/5EA/10кодов/потеря ответа→replay/WAIT_CONTROL, отчёт45; NET ручной факт блокируется.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-14 ·1300: B02 multi-profile TSD/NET policy/exact quantity/durable pick+close; actual1134/5EA10codes, P12H5, replay after response loss; report45/screens82–84. No external ACK/full-sprint claim.\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");d=json.loads(p.read_text(encoding="utf-8"))
for item in d["increments"]:
 if item["id"]in["NI04.2","NI04.3"]:item.setdefault("implementedSlices",[]).append("1292–1300 existing TSD all SKU profiles/NET archive/exact quantities/current-scope durable pick and close; actual1134 five units ten codes, committed-response-loss replay, WAIT_CONTROL; report45.")
files[str(p)]=json.dumps(d,indent=2,ensure_ascii=False)+"\n"
print(json.dumps(files,ensure_ascii=True))
