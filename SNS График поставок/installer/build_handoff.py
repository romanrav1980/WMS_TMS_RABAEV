"""Archive the verified portable runtime together with complete project sources."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import zipfile
from contextlib import closing

ROOT = Path(__file__).resolve().parents[1]
stage = ROOT / 'installer/handoff-stage/install'
out = ROOT / 'installer/handoff-20261110'
out.mkdir(exist_ok=True)
assert (stage / 'python/python.exe').is_file(), 'Extract the current installer to handoff-stage/install first'
for p in ROOT.glob('*.py'):
    shutil.copy2(p, stage / p.name)
for folder in ('wiki', 'tools'):
    shutil.copytree(ROOT / folder, stage / folder, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
for p in (ROOT / 'installer').iterdir():
    if p.is_file() and p.suffix in ('.py', '.cs'):
        shutil.copy2(p, stage / 'installer' / p.name)
live = Path(os.environ['LOCALAPPDATA']) / 'SNS Delivery Schedule/runtime/schedule.sqlite3'
with closing(sqlite3.connect(live)) as src, closing(sqlite3.connect(stage / 'runtime/schedule.sqlite3')) as dst:
    src.backup(dst)
    assert dst.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    recommendations = dst.execute('SELECT COUNT(*) FROM schedule_recommendations').fetchone()[0]
shutil.copy2(stage / 'График поставок.exe', stage / 'SNS-Start.exe')
(stage / 'START.cmd').write_bytes(b'@echo off\r\ncd /d "%~dp0"\r\nstart "" "%~dp0SNS-Start.exe"\r\n')
(stage / 'START_DEBUG.cmd').write_bytes(b'@echo off\r\ncd /d "%~dp0"\r\n"%~dp0python\\python.exe" "%~dp0server.py" --port 4379\r\npause\r\n')
shutil.copy2(stage / 'START_DEBUG.cmd', stage / 'start_sns.bat')
(stage / 'AGENTS.md').write_text('''# SNS «График поставок»: правила для нового Codex

Это самостоятельный переносимый проект, не WMS и не TMS-2.
Сначала прочитать wiki/TRANSFER_CONTEXT.md, wiki/index.md, затем релевантную wiki-страницу.
Источники SAP/Excel не изменять. Не публиковать проект и SAP-материалы на GitHub.
Файлы проекта UTF-8; PowerShell читать с -Encoding UTF8. Изменять только относящееся к задаче.
После устойчивых изменений обновлять соответствующую wiki-страницу, wiki/index.md и wiki/log.md.
База runtime/schedule.sqlite3 — сохранить backup перед изменениями и переносом.
Не сбрасывать рекомендации пользователя. Не запускать SAP без поручения.
Один рабочий адрес: 127.0.0.1:4379. Запуск START.cmd, диагностика START_DEBUG.cmd.
Пути определять относительно текущей рабочей папки; прежний C:/projects/TMS не предполагается.
Не заявлять о проверке на ноутбуке пользователя, если проведена только локальная проверка.
Публикация запрошенных сборок в папку Google Drive разрешена постоянно; адрес в wiki/deployment.md.
Не пересобирать и не публиковать установщик после каждой мелкой UI-правки без задачи на сборку.
''', encoding='utf-8')
(stage / 'START_PROMPT.txt').write_text('''Продолжаем проект SNS «График поставок» в этой папке.
Прочитай AGENTS.md, wiki/TRANSFER_CONTEXT.md, wiki/index.md и wiki/deployment.md.
Определи текущую папку и используй относительные пути. Здесь уже есть встроенный Python, SQLite, исходники, исходные SAP/Excel, рабочие JSON и актуальная база рекомендаций.
Сначала проверь целостность базы и запуск через START.cmd на 127.0.0.1:4379. Не создавай параллельную копию базы и не пересобирай JSON без необходимости.
Владелец сообщил, что прежний установщик закрывался после окна установки. В этом комплекте доступен прямой переносимый запуск, а ошибки пишутся в runtime/server.log и runtime/launcher.log. Если запуск не удался, прочитай журналы и исправь фактическую причину.
Сохрани все рекомендации и данные. Плановая дата заказа — VBAK-VDATU; факт — окончание BLC. Подробные согласованные правила и незакрытая ошибка отображения факта описаны в контексте.
Сообщи, что реально проверено на этом компьютере, затем продолжай по моим следующим поручениям.
''', encoding='utf-8')
(stage / 'ПРОЧИТАЙТЕ.txt').write_text('''ПЕРЕНОСИМЫЙ ПРОЕКТ SNS

1. Разместите всю папку install в выбранном каталоге компьютера.
2. Для запуска дважды нажмите START.cmd. Устанавливать Python или SQL Server не требуется.
3. Приложение: http://127.0.0.1:4379/site/. Интернет нужен только для фоновой карты.
4. Если приложение не открылось, запустите START_DEBUG.cmd и сохраните текст ошибки; журналы находятся в runtime.
5. Для продолжения разработки откройте именно папку install в Codex и отправьте ему текст START_PROMPT.txt.

Рабочая база: runtime/schedule.sqlite3. Не удаляйте её. Исходные документы и данные находятся рядом с кодом и в папке Данные.
Нельзя одновременно запускать эту копию и другую копию SNS на порту 4379.
Папку можно назвать иначе и переместить: приложение использует пути относительно себя.
''', encoding='utf-8')
(stage / 'wiki/log.md').write_text('# Журнал переноса\n\n10.11.2026 — подготовлен переносимый проект с исходниками, встроенным Python и снимком рабочей базы. Предыдущая история — в тематических wiki-страницах.\n', encoding='utf-8')
manifest = {}
for p in sorted(stage.rglob('*')):
    rel = p.relative_to(stage)
    if p.is_file() and '__pycache__' not in rel.parts and p.suffix not in ('.pyc', '.log') and not p.name.startswith('~$'):
        content = p.read_bytes()
        manifest[rel.as_posix()] = {'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
(stage / 'TRANSFER_MANIFEST.json').write_text(json.dumps({'recommendations': recommendations, 'files': manifest}, ensure_ascii=False, indent=2), encoding='utf-8')
archive = out / 'SNS-install-project.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for name in manifest:
        z.write(stage / name, 'install/' + name)
    z.write(stage / 'TRANSFER_MANIFEST.json', 'install/TRANSFER_MANIFEST.json')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert 'install/START_PROMPT.txt' in z.namelist()
raw = archive.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
parts = []
for n, offset in enumerate(range(0, len(raw), 90_000_000), 1):
    part = out / f'SNS-install-project.zip.{n:03}'
    part.write_bytes(raw[offset:offset+90_000_000])
    parts.append(part.name)
items = ','.join("'"+p+"'" for p in parts)
command = f"$ErrorActionPreference='Stop'; if(Test-Path -LiteralPath 'install'){{throw 'Folder install already exists. Use an empty folder to preserve its database.'}}; $parts=@({items}); foreach($p in $parts){{if(!(Test-Path -LiteralPath $p)){{throw ('Missing part: '+$p)}}}}; $out=[IO.File]::Create((Join-Path (Get-Location) 'SNS-install-project.zip')); try{{foreach($p in $parts){{$s=[IO.File]::OpenRead((Join-Path (Get-Location) $p));try{{$s.CopyTo($out)}}finally{{$s.Dispose()}}}}}}finally{{$out.Dispose()}}; if((Get-FileHash -LiteralPath 'SNS-install-project.zip' -Algorithm SHA256).Hash -ne '{sha}'){{throw 'Checksum mismatch'}}; Expand-Archive -LiteralPath 'SNS-install-project.zip' -DestinationPath (Get-Location); Write-Host 'Ready. Open install/START.cmd. For Codex use install/START_PROMPT.txt.'"
bat='@echo off\r\ncd /d "%~dp0"\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -Command "'+command+'"\r\nif errorlevel 1 (echo Unpacking failed. See the error above. & pause & exit /b 1)\r\npause\r\n'
(out / 'UNPACK.cmd').write_bytes(bat.encode('ascii'))
(out / 'ПРОЧИТАЙТЕ.txt').write_text('Скачайте все части SNS-install-project.zip.001, .002, .003 и UNPACK.cmd в одну пустую папку. Запустите UNPACK.cmd. Он проверит архив и распакует папку install. Затем откройте install/START.cmd для запуска приложения. Для продолжения разработки откройте папку install в Codex и отправьте текст install/START_PROMPT.txt. Если Google Drive скачал внешний ZIP, сначала извлеките его полностью.\n', encoding='utf-8')
(out / 'SHA256.txt').write_text(sha+'  SNS-install-project.zip\n', encoding='ascii')
print(json.dumps({'archive_bytes': len(raw), 'files': len(manifest), 'recommendations': recommendations, 'sha256': sha, 'parts': parts}), flush=True)
