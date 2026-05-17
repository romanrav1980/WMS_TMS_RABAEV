# Runbook: Project Onramp

## First Five Minutes

1. Read [`../index.md`](../index.md).
2. Read [`../overview.md`](../overview.md).
3. Check `git status --short` before editing.
4. Pick the relevant subproject page.
5. Open raw sources only after the synthesis page points you there.

## If Working On Legacy WMS

Read:

- [`../subprojects/windowsapplication2.md`](../subprojects/windowsapplication2.md)
- [`../subprojects/oracle_schema.md`](../subprojects/oracle_schema.md)
- [`../concepts/external_integration_supermag.md`](../concepts/external_integration_supermag.md)

## Before Finalizing Work

- If code changed, run the relevant local checks when available.
- If durable context changed, update the relevant wiki page.
- If wiki navigation changed, update [`../index.md`](../index.md).
- Append [`../log.md`](../log.md).
- For Russian text changes, run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-encoding.ps1` or at least read files with `Get-Content -Encoding UTF8`.

## Local Launch Discipline

- Prefer root [`../../serv.bat`](../../serv.bat) for the WMS API server.
- Prefer root [`../../front.bat`](../../front.bat) for the WMS admin frontend or raw UI reference.
- Prefer root [`../../terminal.bat`](../../terminal.bat) for the WMS terminal Web/PWA app.
- These scripts free their target ports before starting so local checks do not reuse stale processes.

## Encoding Discipline

- The repository standard is UTF-8.
- PowerShell can show mojibake when it guesses the wrong encoding; inspect Russian files with `Get-Content -Encoding UTF8`.
- Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-encoding.ps1` before committing wiki, HTML, SQL, Python, or JavaScript files containing Russian text.
