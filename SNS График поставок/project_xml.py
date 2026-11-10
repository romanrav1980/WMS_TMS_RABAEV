"""Transactional project snapshots: schedules, datasets and original source documents."""
import base64
import binascii
import hashlib
import json
import sqlite3
import zlib
import xml.etree.ElementTree as ET
from pathlib import PurePosixPath
from xml.sax.saxutils import quoteattr

import database_xml

MAX_XML = 768 * 1024 * 1024
MAX_FILE = 192 * 1024 * 1024
MAX_TOTAL = 640 * 1024 * 1024
REQUIRED = {'data/october.json', 'data/trip_details.json', 'data/planned_delivery.json', 'data/rc_districts.json'}


def init(db):
    db.execute('CREATE TABLE IF NOT EXISTS project_files (name TEXT PRIMARY KEY, content BLOB NOT NULL)')


def allowed(name):
    path = PurePosixPath(name)
    if path.name.startswith('~$'):
        return False  # Office lock files are not source documents.
    if not name or '\\' in name or ':' in name or path.is_absolute() or any(p in ('..', '.') for p in name.split('/')):
        return False
    if path.as_posix() != name:
        return False
    ext = path.suffix.lower()
    return ((len(path.parts) == 2 and path.parts[0] == 'data' and ext == '.json') or
            (len(path.parts) == 1 and ext in ('.xlsx', '.xls', '.csv', '.json', '.jsonl')) or
            (len(path.parts) > 1 and path.parts[0] in ('Данные', 'Протоколы совещаний') and
             ext in ('.txt', '.csv', '.xlsx', '.xls', '.json', '.jsonl', '.docx', '.pdf', '.xml')))


def assets(db, root):
    if db.execute('SELECT 1 FROM project_files LIMIT 1').fetchone():
        yield from db.execute('SELECT name,content FROM project_files ORDER BY name')
    else:
        paths = list(root.glob('*')) + list((root / 'data').glob('*'))
        for folder in ('Данные', 'Протоколы совещаний'):
            paths.extend((root / folder).rglob('*'))
        for path in sorted(paths):
            name = path.relative_to(root).as_posix()
            if path.is_file() and allowed(name):
                yield name, path.read_bytes()


def export(db, root, stream):
    stream.write(b'<?xml version="1.0" encoding="utf-8"?>\n<sns_project version="2">\n')
    schedule = ET.fromstring(database_xml.serialize(db))
    stream.write(ET.tostring(schedule, encoding='utf-8'))
    stream.write(b'\n<files>\n')
    names = set()
    for name, content in assets(db, root):
        names.add(name)
        attr = f'<file path={quoteattr(name)} size="{len(content)}" sha256="{hashlib.sha256(content).hexdigest()}" encoding="zlib-base64">'
        stream.write(attr.encode('utf-8'))
        stream.write(base64.b64encode(zlib.compress(content, 6)))
        stream.write(b'</file>\n')
    if not REQUIRED <= names:
        raise ValueError('В проекте отсутствуют обязательные таблицы данных')
    stream.write(b'</files></sns_project>')


def validate_dataset(name, content):
    if not name.startswith('data/'):
        return
    value = json.loads(content.decode('utf-8-sig'))
    if name == 'data/october.json':
        if not isinstance(value, dict) or not isinstance(value.get('records'), list):
            raise ValueError('Некорректные данные операций')
        if any(not isinstance(r, dict) or not all(k in r for k in ('trip', 'operation', 'end', 'chain')) for r in value['records']):
            raise ValueError('Некорректная строка операции')
    elif name == 'data/trip_details.json':
        if not isinstance(value, dict) or any(not isinstance(v, dict) or not isinstance(v.get('goods'), list) or not isinstance(v.get('orders'), list) for v in value.values()):
            raise ValueError('Некорректные данные транспортировок')
    elif name in ('data/planned_delivery.json', 'data/rc_districts.json'):
        if not isinstance(value, list) or any(not isinstance(v, dict) for v in value):
            raise ValueError('Некорректная таблица данных')


def restore(db, stream, valid_value, chains):
    # Reject entity/DOCTYPE declarations in any UTF-8 chunk before XML parsing.
    tail = b''
    while chunk := stream.read(1024 * 1024):
        block = tail + chunk.upper()
        if b'<!DOCTYPE' in block or b'<!ENTITY' in block or b'\x00' in block:
            raise ValueError('Требуется XML UTF-8 без DTD и сущностей')
        tail = block[-16:]
    stream.seek(0)
    names = set()
    total = 0
    setting = records = None
    depth = 0
    root_tag = None
    db.execute('BEGIN IMMEDIATE')
    try:
        for event, element in ET.iterparse(stream, events=('start', 'end')):
            if event == 'start':
                depth += 1
                if depth == 1:
                    root_tag = element.tag
                    if (root_tag, element.get('version')) not in (('sns_project', '2'), ('sns_schedule', '1')):
                        raise ValueError('Неизвестный формат XML проекта')
                    if root_tag == 'sns_project':
                        db.execute('DELETE FROM project_files')
                continue
            if root_tag == 'sns_project' and element.tag == 'file' and depth == 3:
                name = element.get('path', '')
                if not allowed(name) or name in names or len(names) >= 10000:
                    raise ValueError('Недопустимый или повторяющийся файл в XML')
                size = int(element.get('size', '-1'))
                if not 0 <= size <= MAX_FILE or total + size > MAX_TOTAL or element.get('encoding') != 'zlib-base64':
                    raise ValueError('Превышен размер данных или неизвестная кодировка файла')
                packed = base64.b64decode(element.text or '', validate=True)
                decoder = zlib.decompressobj()
                content = decoder.decompress(packed, size + 1)
                if len(content) != size or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                    raise ValueError('Повреждено содержимое файла XML')
                if hashlib.sha256(content).hexdigest() != element.get('sha256'):
                    raise ValueError('Не совпала контрольная сумма файла XML')
                validate_dataset(name, content)
                db.execute('INSERT INTO project_files(name,content) VALUES(?,?)', (name, content))
                names.add(name)
                total += size
                element.clear()
            elif element.tag == 'sns_schedule' and depth == (2 if root_tag == 'sns_project' else 1):
                if setting is not None:
                    raise ValueError('Повторяющийся раздел рекомендаций')
                setting, records = database_xml.parse(ET.tostring(element, encoding='utf-8'), valid_value, chains)
                element.clear()
            depth -= 1
        if setting is None or (root_tag == 'sns_project' and not REQUIRED <= names):
            raise ValueError('XML не содержит полного набора данных проекта')
        db.execute('DELETE FROM schedule_recommendations')
        db.execute('DELETE FROM schedule_settings')
        db.execute('INSERT INTO schedule_settings(id,companion_limit) VALUES(1,?)', (setting,))
        db.executemany("INSERT INTO schedule_recommendations(chain,address_key,frequency,days,minimum,recommended_source,companion_limit,updated_at) VALUES(?,?,?,?,?,?,?,COALESCE(NULLIF(?,''),CURRENT_TIMESTAMP))", records)
        db.commit()
    except (ET.ParseError, binascii.Error, zlib.error, UnicodeError) as exc:
        db.rollback()
        raise ValueError('Повреждён XML или данные внутри него') from exc
    except Exception:
        db.rollback()
        raise
    return {'ok': True, 'count': len(records), 'files': len(names), 'bytes': total, 'full_project': root_tag == 'sns_project'}
