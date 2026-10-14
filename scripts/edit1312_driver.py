from pathlib import Path
p=Path("admin/wms_admin_frontend/src/components/DriverMobilePage.tsx");s=p.read_text(encoding="utf-8").replace('selectedTrip && activeView === "sts" && <','selectedTrip && !loading && activeView === "sts" && <');p.write_text(s,encoding="utf-8")
p=Path("scripts/browser1311_driver.mjs");s=p.read_text(encoding="utf-8").replace(" await receipt.getByLabel('Пользователь получателя')"," await receipt.getByLabel('Адрес магазина').selectOption({index:1});\n await receipt.getByLabel('Пользователь получателя')");p.write_text(s,encoding="utf-8")
