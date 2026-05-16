# DB/Application Compatibility Check 2026-05-11

## Scope

Checked compatibility between the restored Oracle VM schema and:

- `WindowsApplication2` C# desktop client;
- `Tserver` terminal gateway.

The first check was intentionally read-only against Oracle except for build outputs and temporary local smoke-test files. A follow-up compatibility fix pass was applied only after creating VirtualBox snapshot `before-compat-fixes-2026-05-11` (`2c2da6c9-77b1-4f97-bffe-88b971f9af7e`).

No real warehouse operation flow was executed. The package smoke for mutating functions used synthetic values and finished with `rollback`.

## Oracle Target

- Host/service: `127.0.0.1:1521/orcl`
- Schema: `RABAEV`
- Password used by legacy apps: `RABAEVWMS`
- TNS alias: `DBWMS`

`tnsping DBWMS` resolves to:

```text
(DESCRIPTION = (ADDRESS = (PROTOCOL = TCP)(HOST = 127.0.0.1)(PORT = 1521)) (CONNECT_DATA = (SERVER = DEDICATED) (SERVICE_NAME = orcl)))
```

## Build Results

### WindowsApplication2

Command:

```powershell
powershell.exe -ExecutionPolicy Bypass -File scripts\build-windowsapplication2-desktop.ps1
```

Result:

- build succeeded;
- `0` errors;
- `128` legacy warnings;
- output: `MINI WMS/WindowsApplication2/WindowsApplication2/bin/Release/WindowsApplication2.exe`.

Connection status:

- current `app.config` maps `DBWMS`, `DBWMSSUR`, and `DBWMSUFA` to `127.0.0.1:1521/orcl`;
- login form builds the WMS connection as `RABAEV/RABAEVWMS`;
- desktop client uses `Oracle.ManagedDataAccess` through the local compatibility wrapper.

### Tserver

Command:

```powershell
MSBuild.exe "MINI WMS\Tserver\Tserver\Tserver.csproj" /t:Rebuild /p:Configuration=Release /p:Platform=AnyCPU
```

Result:

- build succeeded;
- `0` errors;
- `40` warnings;
- warnings are mainly `System.Data.OracleClient` deprecation warnings;
- output: `MINI WMS/Tserver/Tserver/bin/Release/Tserver.exe`.

## Read-Only Oracle Probes

Managed ODP.NET probe:

```text
CONNECTED_USER  SERVICE_NAME
RABAEV          orcl
```

Legacy `System.Data.OracleClient` probe:

```text
Server=(DESCRIPTION=...127.0.0.1...orcl)  OK USER=RABAEV
Server=DBWMS                              OK USER=RABAEV
```

Final object status:

```text
FUNCTION      VALID 176
INDEX         VALID 125
LOB           VALID 2
PACKAGE       VALID 10
PACKAGE BODY  VALID 10
PROCEDURE     VALID 6
SEQUENCE      VALID 33
TABLE         VALID 79
TRIGGER       VALID 21
VIEW          VALID 1
```

Key table counts:

```text
RRL_ARTICULS             5328
RRL_CELLS                28641
RRL_PALLETS              758336
RRL_SBORKA_PALLET_ROWS   379194
RRL_SBORKA_PALLETS       379194
RRL_TRANSPORT_TASK       30256
RUSERS                   923
```

## Tserver Smoke Test

Created a temporary local `adr.txt` for the smoke run:

```text
127.0.0.1
20019

DBWMS
```

Started `Tserver.exe` from a temporary folder and sent a read-only terminal command:

```text
FUNC=GET_RUSER|USERID=DO|
```

Result:

```text
FUNC=USER_INFO|ID=DO|NAME=Диспетчер отгрузки|PRAVO_INVENTORY_EDIT=0|PRAVO_CHECK_ORDER=1|PRAVO_LIGHT_INVENTORY_CHECK=0|PRAVO_RAZVOZ_ZAYAVOK=0|PRAVO_EAN_PRODUCT_CHANGE=0|PRAVO_KARSHIK=0|ware_id=1|...
```

Conclusion: `Tserver` can bind locally, use `DBWMS`, connect to Oracle, and return a valid read-only response.

After the config fix, the checked-in `adr.txt` format is:

```text
127.0.0.1
20009
3
DBWMS
```

Smoke test against the checked-in config returned:

```text
FUNC=USER_INFO|ID=DO|NAME=Диспетчер отгрузки|PRAVO_INVENTORY_EDIT=0|...
```

## Static Call Registry Findings

Extracted direct stored function/procedure-style calls from:

- `MINI WMS/WindowsApplication2/WindowsApplication2/**/*.cs`;
- `MINI WMS/Tserver/Tserver/**/*.cs`.

Summary:

- code call tokens found: `139`;
- callable Oracle objects/subprograms found: `304`;
- missing call targets from the restored schema: `28`.

Missing package/subprogram references:

```text
COMPL.ADD_ART_2PALL
COMPL.DIVIDE_ORDER_BYPAL2
COMPL.UPDATE_SEQ2
HELP.UPDATE_OBJECT
PALL_SPLITTER.ADD_ROW_2SBORKA_PALLETS
PALL_SPLITTER.CREATE_RETURN_TASK
PALL_SPLITTER.SPLIT_UFA
PALL_SPLITTER.SPLIT_VEGETABLES
PRIHOD.CLOSE_PRICE_CONTROL
PRIHOD.PRIHOD_IS_CLOSED
PRIHOD.SET_BRAK_PERC_NEW
PRIHOD.SET_DOCK
PRIHOD.SET_PRIHOD_KPP
PRIHOD.SET_PRIORITY
PRIHOD.SET_WARE_ID
STORE_ADRESSES.UPDATE_CELL
TRANSPORT_PLN.GET_DIST_M
TRANSPORT_PLN.GET_DISTANCE
TRANSPORT_PLN.GET_TIME
TRANSPORT_PLN.GET_TIME_M
TRANSPORT_PLN.IS_TT_JUST_OUT_GO
TRANSPORT_PLN.SET_DISTANCE
TRANSPORT_PLN.SET_DISTANCE_M
TRANSPORT_PLN.SET_MAIL_SENDED
TRANSPORT_PLN.SET_TIME
TRANSPORT_PLN.SET_TIME_M
TRANSPORT_PLN.SET_TT_CLOSED
TRANSPORT_PLN.UPD_TT_PERDICTION
```

Missing table-like references from static SQL token extraction:

```text
INVOICE_DH
RRL_PALL_TRASH_REASON
RRL_PALLETS_HIST
RRL_SUPPLIERS
RRL_TRP_REGIONS
```

Notes:

- Some table-like tokens may be external or false positives from dynamic SQL.
- Several missing packages exist in historical scripts under `SQL/Перенос версий/`, especially `HELP`, `PALL_SPLITTER`, `PRIHOD`, and `STORE_ADRESSES`.
- `TRANSPORT_PLN` was referenced by desktop transport/distance screens but was not present in the restored schema.

## Tserver Configuration Risk

`Tserver` reads `adr.txt` from its current working directory and expects `DBWMSString = str4[3]`.

Before the fix, `MINI WMS/Tserver/adr.txt` contained only:

```text
192.168.208.200
20009
```

Because the parser expects a fourth line, it throws and falls back to hardcoded defaults:

- IP: `192.168.208.200`;
- port: `20007`;
- database alias: `DBWMS`.

On this workstation the safe working test required a four-line local `adr.txt`.

Fixed in `MINI WMS/Tserver/Tserver/Program.cs`:

- config is searched in the working directory and next to the executable;
- `adr.txt` must contain `IP`, `PORT`, `WARE_ID`, `DB_ALIAS`;
- malformed config stops startup with an explicit error;
- old hardcoded `192.168.208.200` fallback was removed;
- `adr.txt` is included as `Tserver.csproj` content and is copied to `bin/Release` during build.
- `Tserver.sln` header was normalized to modern solution format so MSBuild 17 can build the solution directly.

Both checked-in files were updated:

- `MINI WMS/Tserver/adr.txt`;
- `MINI WMS/Tserver/Tserver/adr.txt`.

## Compatibility Fix Pass

Applied script:

```text
db/compatibility_fixes/2026-05-11/001_client_tserver_compat.sql
```

This adds the missing table-like objects:

```text
INVOICE_DH
RRL_PALL_TRASH_REASON
RRL_PALLETS_HIST
RRL_SUPPLIERS
RRL_TRP_REGIONS
```

It also creates compatibility packages:

```text
HELP
PALL_SPLITTER
PRIHOD
STORE_ADRESSES
TRANSPORT_PLN
```

`COMPL` was extended in:

```text
db/windowsapplication2_xp12_oracle/11_compl_contract.sql
```

Added `COMPL` subprograms:

```text
ADD_ART_2PALL
DIVIDE_ORDER_BYPAL2
UPDATE_SEQ2
```

Additional compatibility columns were added for the desktop screens that already reference them, including `RRL_PRIHOD_NAKLAD.PROOVED`, `DOCK`, `INVITE_TIME`, `PRIORITY1`, `OHRANA_KPP`, and `RRL_PALLETS.REASON_ID`.

The desktop pallet-history query was corrected from `rs.PUID` to `PUID` because the SQL did not define alias `rs`.

Final post-fix Oracle status:

```text
INVALID_COUNT
0
```

The formerly missing package/subprogram references are now present in `USER_PROCEDURES`.

## Compatibility Verdict

### Green

- Restored Oracle schema is reachable as `RABAEV`.
- All current Oracle objects are valid after the compatibility fix pass and recompile.
- C# desktop client builds.
- `Tserver` builds.
- Managed ODP.NET connection works.
- Legacy `System.Data.OracleClient` connection works.
- `DBWMS` alias currently resolves to the local Oracle VM.
- `Tserver` read-only `GET_RUSER` command works against the restored database.
- Previously missing package/table-like references are now present.
- `Tserver` no longer silently falls back to `192.168.208.200`.

### Yellow

- Desktop application was not manually opened through the UI in this check.
- Login procedure `RRL_AUTH3` was not executed because it may write login history.
- Mutating terminal flows were not executed.
- The new compatibility packages are intentionally conservative wrappers where the original historical implementation was absent or incomplete.

## Next Steps

1. Add an automated compatibility smoke script for:
   - managed ODP.NET DB ping;
   - legacy OracleClient DB ping;
   - key table counts;
   - critical object existence;
   - `Tserver` `GET_RUSER`.
2. Manually open desktop client screens that rely on the new compatibility layer:
   - receiving / `PRIHOD`;
   - distance matrix / `TRANSPORT_PLN`;
   - store addresses / `STORE_ADRESSES`;
   - return-to-supplier / `PALL_SPLITTER`.
3. Only after a fresh VM snapshot, run controlled mutation smoke tests:
   - desktop login;
   - scan confirmation;
   - pallet/cell movement;
   - inventory line creation.
4. Replace conservative compatibility wrappers with recovered original business logic where historical DDL is found and validated.
