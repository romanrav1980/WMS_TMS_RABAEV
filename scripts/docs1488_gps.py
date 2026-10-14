from pathlib import Path
p=Path('wiki/components/nicora_geofences_gps_20261014.md');p.write_text('''# Геозоны и GPS: актуальный контракт

[Отчёт70](../../reports/nicora/2026-10-13/70-geofences-gps-contract.md): ADDR строка, SHIROTA/DOLGOTA, NUM, active filters; CONFIG radius edit. Один GPS transaction/history/latest, старый пакет не меняет свежую позицию. Timestamp — явно локальная Oracle DATE без offset; это не UTC conversion.

ENTER/EXIT не проводит разгрузку по первой UNLOAD. Возвращаются наблюдения по рейсу/адресу и operational_fact_applied=false. Для будущей автоматики нужна достоверная привязка к существующей операции, а не новый writer. Native TestClient/own roundtrip/rollback passed; actual tracker не отправлялся. SQL списка16мс; NOCACHE history insert/waits — transport operations перед высокочастотным пилотом.
''',encoding='utf-8')
p=Path('wiki/index.md');p.write_text('- [Геозоны и атомарный GPS](components/nicora_geofences_gps_20261014.md): report70, реальные поля/ADDR, история+позиция в одной транзакции, запоздалый пакет не откатывает позицию; наблюдение не меняет произвольную разгрузку.\n'+p.read_text(encoding='utf-8'),encoding='utf-8')
with Path('wiki/log.md').open('a',encoding='utf-8') as f:f.write('\n- 2026-10-14: geofences/GPS RELEASE ведомого; root review и дневной диапазон TS безTRUNC, report70. Claude C0029: cardinality ERP maps, лёгкий warehouse selector, подготовка расширенного профиля без дублирования источников; DDL apply остаётся у root.\n')
