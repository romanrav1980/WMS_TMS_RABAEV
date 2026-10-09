# Локальное администрирование существующего Oracle dev

08.10.2026. VM **Oracle DB Developer VM**, PDB/service **orcl**, рабочая схема **RABAEV**. Новый экземпляр не создавался.

## Подтверждённый способ

В существующей консоли VM открыт терминал пользователя oracle. Для локального SYSDBA надо убрать сетевое переопределение подключения: TWO_TASK/LOCAL превращали `connect / as sysdba` в сетевую попытку с ORA-01017. Фактический ORACLE_SID из стартовой информации VM — orclcdb.

```sh
unset TWO_TASK LOCAL
export ORACLE_SID=orclcdb
sqlplus -s /nolog
connect / as sysdba
alter session set container=orcl;
select sys_context('USERENV','CON_NAME'), user from dual;
```

Перед изменениями результат должен быть ORCL/SYS. Применять только конкретный versioned SQL, не create_schema и не восстановление всей базы. Этот способ использует уже авторизованную OS-сессию; пароль не нужен и не сохраняется в repository/environment.

08.10.2026 выполнены три grant из [016_privileges_as_sys.sql](../../db/migrations/2026-10-08_stock_posting_core/016_privileges_as_sys.sql): EXECUTE DBMS_LOCK, DBMS_CRYPTO и DBMS_FLASHBACK для RABAEV. Все три подтверждены USER_TAB_PRIVS_RECD. [Результат консоли](../../runtime/stock_posting_20261008/oracle-vm-grants-result.png).

## Автоматизация консоли

Для существующего терминала использован VBoxManage keyboardputstring, затем отдельный Enter scancode 1c/9c. Windows PowerShell legacy native argument passing убирает вложенные двойные кавычки: поэтому используется `sqlplus -s /nolog` и SQL*Plus `connect / as sysdba`, а не кавычки вокруг shell connection argument.

Не вводить команды вслепую в неизвестное окно. Сначала screenshotpng и проверка terminal prompt. Не выводить стартовый экран VM с credential hints в отчёты; сохранять результат изменяющих команд и read-only verification. SSH по имеющемуся host key не авторизовал oracle; подбирать пароль не потребовалось.

## Минимальный контроль после grants

```powershell
api/wms_api_server/.venv/Scripts/python.exe scripts/stock_posting_install.py
```

Grant prerequisite не активирует новое stock ядро. Штатная installation остаётся в PREPARED; full cutover описан в [[../database/nicora_stock_posting_implementation]].
