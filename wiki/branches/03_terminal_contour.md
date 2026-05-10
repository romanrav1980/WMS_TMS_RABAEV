# Branch: Terminal Contour

## Role

This branch covers handheld terminal and scanner workflows on the warehouse floor.

Its job is to let warehouse workers confirm operations close to the physical action: scan a barcode, confirm a pallet, move stock, audit a cell, or record inventory facts.

## What Lives Here

Terminal workflows belong here:

- barcode scanner UI
- terminal screens
- terminal-to-server communication
- scanner-specific device code
- operation confirmation from the warehouse floor
- terminal gateway/server logic that calls Oracle procedures

## Main Current Locations

- [`../../MINI WMS/CS_CATClient/`](../../MINI%20WMS/CS_CATClient/)
- [`../../MINI WMS/Tserver/`](../../MINI%20WMS/Tserver/)
- [`../../MINI WMS/DeviceApplication3/`](../../MINI%20WMS/DeviceApplication3/)
- [`../../WMSTerm/`](../../WMSTerm/)

## Observed Shape

The terminal contour appears to be split into:

- terminal/client code such as `CS_CATClient`
- a server/gateway process such as `Tserver`
- device-specific barcode/scanner code such as `DeviceApplication3`

The gateway layer talks to Oracle and calls `RABAEV.*` routines. The client side focuses on scanning and operator prompts.

`Tserver` should be treated as a legacy API gateway. It accepts a custom TCP `FUNC=...|key=value|...` protocol, dispatches fixed commands, and also has a generic `CALL_SPF` path for Oracle stored procedure calls.

## What It Depends On

- [[oracle_plsql_core]] for actual operation validation and state changes.
- scanner/barcode SDKs and device APIs for hardware input.

## Boundaries

- Do not treat terminal UI as the source of truth for warehouse state.
- Terminal actions should end in Oracle-backed confirmation.
- Device-specific scanner handling should stay separate from core warehouse rules.
- Do not expose arbitrary stored procedure names to new clients; migrate `CALL_SPF` to explicit allowlisted API operations.

## API Migration Notes

- [Tserver legacy API registry](../concepts/tserver_api_registry.md)
- [Create WMS API server](../runbooks/create_api_server.md)

## Primary Sources

- [`../../MINI WMS/CS_CATClient/CS_CATClient.csproj`](../../MINI%20WMS/CS_CATClient/CS_CATClient.csproj)
- [`../../MINI WMS/CS_CATClient/FormMain.cs`](../../MINI%20WMS/CS_CATClient/FormMain.cs)
- [`../../MINI WMS/Tserver/Tserver/Tserver.csproj`](../../MINI%20WMS/Tserver/Tserver/Tserver.csproj)
- [`../../MINI WMS/Tserver/Tserver/Program.cs`](../../MINI%20WMS/Tserver/Tserver/Program.cs)
- [`../../MINI WMS/DeviceApplication3/DeviceApplication3/DeviceApplication3.csproj`](../../MINI%20WMS/DeviceApplication3/DeviceApplication3/DeviceApplication3.csproj)
- [`../../WMSTerm/постановка.txt`](../../WMSTerm/%D0%BF%D0%BE%D1%81%D1%82%D0%B0%D0%BD%D0%BE%D0%B2%D0%BA%D0%B0.txt)
