# Геозоны и GPS: актуальный контракт

[Отчёт70](../../reports/retailcase/2026-10-13/70-geofences-gps-contract.md): ADDR строка, SHIROTA/DOLGOTA, NUM, active filters; CONFIG radius edit. Один GPS transaction/history/latest, старый пакет не меняет свежую позицию. Timestamp — явно локальная Oracle DATE без offset; это не UTC conversion.

ENTER/EXIT не проводит разгрузку по первой UNLOAD. Возвращаются наблюдения по рейсу/адресу и operational_fact_applied=false. Для будущей автоматики нужна достоверная привязка к существующей операции, а не новый writer. Native TestClient/own roundtrip/rollback passed; actual tracker не отправлялся. SQL списка16мс; NOCACHE history insert/waits — transport operations перед высокочастотным пилотом.
