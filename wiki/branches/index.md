# Logical Branches

The TMS repository is organized into four logical branches.

These are not Git branches. They are architectural branches: stable mental folders for understanding where logic belongs and where to look first.

They map to the target subrepository model in [`../repositories/index.md`](../repositories/index.md).

## Branches

1. [Oracle / PL/SQL Core](01_oracle_plsql_core.md)
2. [C# Desktop Client](02_csharp_desktop_client.md)
3. [Terminal Contour](03_terminal_contour.md)
4. [External Integrations](04_external_integrations.md)

## System Shape

```text
External systems
  -> integration scripts / external schemas
  -> Oracle staging or source schemas
  -> RABAEV Oracle core
  -> desktop client and terminal contour
```

```text
Terminal device
  -> terminal client
  -> terminal server / gateway
  -> RABAEV stored procedures
  -> confirmed warehouse operation
```

```text
Desktop operator
  -> WindowsApplication2
  -> RABAEV stored procedures and views
  -> documents, pallets, inventory, transport, users
```

## Ownership Rule

When deciding where a change belongs, first ask:

- Is this persistent business state or warehouse algorithm? Put it in [[oracle_plsql_core]].
- Is this operator UI or desktop workflow? Put it in [[csharp_desktop_client]].
- Is this barcode/scanner/warehouse-floor confirmation? Put it in [[terminal_contour]].
- Is this data coming from or going to another system? Put it in [[external_integrations]].
