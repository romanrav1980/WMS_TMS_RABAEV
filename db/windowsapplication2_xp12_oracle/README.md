WindowsApplication2 desktop app currently matches the `xp12` database line from `MINI WMS\WindowsApplication2\WindowsApplication2\Form2.cs`.

Chosen Oracle schema source:
- `SQL\MINI WMS\Создание БАЗЫ\Таблицы.sql`
- `SQL\MINI WMS\Создание БАЗЫ\последовательности.sql`
- `SQL\MINI WMS\Создание БАЗЫ\функции.sql`
- `SQL\MINI WMS\Создание БАЗЫ\процедуры.sql`

Why this set:
- the desktop app calls Oracle routines such as `RRL_AUTH3`, `RRL_ACCEPT_ORDER2_3`, `RRL_GIVE_DESTINATION_CELL2`, `ADD_RRL_OTHOD_NAKLAD`, `RRL_SET_TRANSPORT_PRICE`
- those routines exist in `функции.sql`
- audit tables used by the app, including `LOT_AUDIT_ERROR_LINES`, are already present in `Таблицы.sql`
- the separate file `WMS Эталон\Версия бд от 06.11.2011` looks like an older delta and is not needed on top of this schema export

How to build the desktop app:
```powershell
powershell -ExecutionPolicy Bypass -File C:\projects\TMS\scripts\build-windowsapplication2-desktop.ps1
```

How to create the Oracle schema:
```sql
@C:\projects\TMS\db\windowsapplication2_xp12_oracle\create_schema.sql
```

Notes:
- `create_schema.sql` creates or updates schema `RABAEV` and then loads schema objects from the normalized ASCII-path copies in this folder
- it creates schema objects only; large `data*.sql` files are not loaded automatically
- the application still depends on external schemas and data such as `SUPERMAG` and business reference data in `RABAEV`
