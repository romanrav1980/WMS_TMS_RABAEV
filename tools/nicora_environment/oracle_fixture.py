"""Atomic fixture DML; exact-key provenance; non-fixture inventory preservation."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import time
from tools.mcp.tms_mcp_server import oracle_connection
from .fixture_plan import ROOT, TABLE_KEYS, plan, validate_plan

METRICS: list[dict] = []


def serial(value: object) -> str:
    return value.isoformat() if isinstance(value, datetime) else str(value)


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, default=serial, ensure_ascii=False,
                                    sort_keys=True, separators=(',',':')).encode()).hexdigest()


def query(cursor, sql: str, binds: dict | None=None) -> list[dict]:
    started = time.perf_counter()
    cursor.execute(sql, binds or {})
    names = [col[0] for col in cursor.description]
    result = [dict(zip(names, row)) for row in cursor.fetchall()]
    METRICS.append({'sql':sql, 'rows':len(result), 'elapsed_ms':round((time.perf_counter()-started)*1000,2)})
    return result


def predicate(table: str, row: dict) -> tuple[str, dict]:
    keys = TABLE_KEYS[table]
    return ' and '.join(f'{key}=:{key}' for key in keys), {key:row[key] for key in keys}


def outside_clause(table: str, records: list[dict]) -> tuple[str, dict]:
    clauses, binds = [], {}
    for index, row in enumerate(records):
        parts = []
        for key in TABLE_KEYS[table]:
            name = f'v{index}_{key}'
            parts.append(f'{key}=:{name}')
            binds[name] = row[key]
        clauses.append('('+' and '.join(parts)+')')
    # Include NULL legacy keys: NOT equality alone would silently exclude them.
    is_null = ' or '.join(f'{key} is null' for key in TABLE_KEYS[table])
    return '(('+is_null+') or not ('+' or '.join(clauses)+'))', binds


def owned(cursor, table: str, records: list[dict], lock: bool=False) -> list[dict]:
    result = []
    for row in records:
        clause, binds = predicate(table, row)
        found = query(cursor, f'select * from {table} where {clause}'+(' for update nowait' if lock else ''), binds)
        if len(found)>1:
            raise RuntimeError(f'Duplicate physical key in {table}')
        result.extend(found)
    return result


def target(cursor) -> dict:
    actual = query(cursor, "select sys_context('USERENV','SESSION_USER') usr, "
                   "sys_context('USERENV','DB_NAME') db, sys_context('USERENV','SERVICE_NAME') service from dual")[0]
    if actual!={'USR':'RABAEV','DB':'ORCL','SERVICE':'orcl'}:
        raise RuntimeError('NS00 restricted to owner-authorized ORCL/orcl/RABAEV')
    return actual


def external_references(cursor, rows: dict) -> None:
    values = {}
    columns = {'UID_PALLET','UID_POLETA','ACTICUL','ARTICUL','WARE_ID','CELL',
               'CUSTOMER_ID','CUSTOMER_ORDER_ID','CUSTOMER_ORDER_ROW_ID','PRIHOD_NAKLAD_ID'}
    for records in rows.values():
        for row in records:
            for column, value in row.items():
                if column in columns:
                    values.setdefault(column,set()).add(value)
    values['UID_POLETA'] = values['UID_PALLET']
    values['ARTICUL'] = values['ACTICUL']
    metadata = query(cursor, "select c.table_name,c.column_name from user_tab_columns c "
                     "join user_tables t on t.table_name=c.table_name where t.table_name not like 'BIN$%'")
    for item in metadata:
        table, column = item['TABLE_NAME'], item['COLUMN_NAME']
        if column not in values:
            continue
        if not re.fullmatch(r'[A-Z][A-Z0-9_]*',table):
            raise RuntimeError('Unreviewed Oracle identifier')
        binds = {f'ref{i}':value for i,value in enumerate(sorted(values[column],key=str))}
        marks = ','.join(':'+key for key in binds)
        extra = ''
        if table in TABLE_KEYS:
            clause, outside_binds = outside_clause(table,rows[table])
            extra = ' and '+clause
            binds.update(outside_binds)
        if query(cursor,f'select 1 found from {table} where {column} in ({marks}){extra} and rownum=1',binds):
            raise RuntimeError(f'External fixture reference: {table}.{column}; reset refused')


def preservation(cursor, rows: dict) -> dict:
    result = {}
    for table, records in rows.items():
        clause, binds = outside_clause(table,records)
        sql = f'select * from {table} where {clause}'
        if table=='RRL_PALLETS':
            sql += ' and exists (select 1 from RRL_REMAINS r where r.UID_POLETA=RRL_PALLETS.UID_PALLET)'
        cursor.arraysize = 1000
        started = time.perf_counter()
        cursor.execute(sql,binds)
        names = [col[0] for col in cursor.description]
        hashes = []
        while batch := cursor.fetchmany(1000):
            hashes.extend(digest(dict(zip(names,row))) for row in batch)
            if len(hashes)>150000:
                raise RuntimeError('Preservation row cap exceeded; transaction will roll back')
        elapsed = round((time.perf_counter()-started)*1000,2)
        result[table] = {'rows':len(hashes),'sha256':digest(sorted(hashes)),'elapsed_ms':elapsed}
        METRICS.append({'sql':sql,'rows':len(hashes),'elapsed_ms':elapsed})
    return result


def comparable(snapshot: dict) -> dict:
    return {table:{key:value[key] for key in ('rows','sha256')} for table,value in snapshot.items()}


def templates(name: str) -> dict[str,str]:
    content = (ROOT/'db/fixtures/nicora_ns00'/name).read_text(encoding='utf-8')
    parts = re.split(r'^-- TABLE: ([A-Z_]+)\s*$',content,flags=re.M)
    return {parts[i]:parts[i+1].strip().rstrip(';') for i in range(1,len(parts),2)}


def checkpoint_write(path: Path, value: dict) -> None:
    pending = path.with_suffix('.pending.json')
    pending.write_text(json.dumps(value,default=serial,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    pending.replace(path)


def seed_reset(manifest: Path, *, reset: bool=False, cleanup: bool=False) -> dict:
    rows = plan()
    validate_plan(rows)
    manifest.parent.mkdir(parents=True,exist_ok=True)
    previous = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else None
    with oracle_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("begin dbms_application_info.set_module('NICORA_NS00','FIXTURE'); end;")
        actual = target(cursor)
        for table in sorted(TABLE_KEYS):
            cursor.execute(f'lock table {table} in share row exclusive mode nowait')
        triggers = query(cursor,"select trigger_name from user_triggers where status='ENABLED' and "
                         "trigger_name not like 'BIN$%' and table_name in ("+
                         ','.join("'"+t+"'" for t in TABLE_KEYS)+')')
        if triggers:
            raise RuntimeError('Unreviewed DML trigger on fixture table')
        current = {table:owned(cursor,table,records,True) for table,records in rows.items()}
        pending = manifest.with_suffix('.pending.json')
        if pending.exists():
            candidate = json.loads(pending.read_text(encoding='utf-8'))
            if candidate['target']==actual and candidate['plan_sha256']==digest(rows) and candidate['owned_sha256']==digest(current):
                pending.replace(manifest)
                previous = candidate
            else:
                raise RuntimeError('Unresolved pre-commit checkpoint; inspect before retry')
        exists = any(current.values())
        if exists and (not previous or previous['target']!=actual or previous['plan_sha256']!=digest(rows)):
            raise RuntimeError('Existing keys without matching provenance; no adoption or deletion')
        if exists and digest(current)!=previous['owned_sha256']:
            raise RuntimeError('Fixture changed since confirmed checkpoint; reset refused')
        if exists and not reset and not cleanup:
            return {'status':'UNCHANGED','rows':sum(map(len,current.values()))}
        external_references(cursor,rows)
        before = preservation(cursor,rows)
        for table in reversed(TABLE_KEYS):
            for row in rows[table]:
                clause, binds = predicate(table,row)
                cursor.execute(templates('reset.sql')[table],binds)
        if not cleanup:
            inserts = templates('seed.sql')
            for table,records in rows.items():
                for row in records:
                    # Optional product fields differ by SKU; only reviewed plan columns may be added.
                    if table=='RRL_ARTICULS':
                        fields = ','.join(row)
                        sql = f'insert into {table} ({fields}) values ({",".join(":"+key for key in row)})'
                    else:
                        sql = inserts[table]
                    cursor.execute(sql,row)
        after = preservation(cursor,rows)
        if comparable(before)!=comparable(after):
            raise RuntimeError('Non-fixture stock/data changed; rolling back')
        saved = {table:owned(cursor,table,records) for table,records in rows.items()}
        report = {'target':actual,'plan_sha256':digest(rows),'owned_rows':saved,
                  'owned_sha256':digest(saved),'outside':after,'rows':sum(map(len,saved.values())),
                  'status':'CLEANED' if cleanup else 'SEEDED'}
        pending.write_text(json.dumps(report,ensure_ascii=False,default=serial,indent=2)+'\n',encoding='utf-8')
        try:
            connection.commit()
        except Exception:
            # Leave pending evidence; next call distinguishes committed from uncommitted rows.
            raise
        pending.replace(manifest)
        return report


def acknowledge_owned_change(manifest: Path) -> dict:
    previous = json.loads(manifest.read_text(encoding='utf-8'))
    with oracle_connection() as connection:
        cursor = connection.cursor()
        target(cursor)
        current = {table:owned(cursor,table,records) for table,records in plan().items()}
        stripped = json.loads(json.dumps(current,default=serial))
        old = previous['owned_rows']
        for records in (stripped['RRL_ARTICULS'],old['RRL_ARTICULS']):
            for row in records:
                if row['ACTICUL']=='DS-BASE-D10':
                    row.pop('SHIPMENT_AGING_HOURS',None)
                    row.pop('SHIPMENT_AGING_COMMENT',None)
        if digest(stripped)!=digest(old):
            raise RuntimeError('Unexpected change; provenance update refused')
        previous.update(owned_rows=current,owned_sha256=digest(current))
        checkpoint_write(manifest,previous)
        return previous
