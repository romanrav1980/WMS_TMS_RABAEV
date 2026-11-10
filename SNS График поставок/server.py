"""Local SNS dashboard server and SQLite storage for recommended schedules."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import argparse
import json
import os
import math
import sqlite3
import shutil
import tempfile
import threading
import datetime
from contextlib import closing
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import database_xml
import project_xml

# pythonw.exe has no console streams; HTTP logging still needs a writable stderr.
if sys.stdout is None: sys.stdout=open(os.devnull,'w')
if sys.stderr is None: sys.stderr=open(os.devnull,'w')

ROOT=Path(__file__).resolve().parent
DB=ROOT/'runtime'/'schedule.sqlite3'
CHAINS={'drinks','tobacco'}
PROJECT_LOCK=threading.RLock()

def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(DB,timeout=10)
    db.execute('PRAGMA busy_timeout=10000')
    db.execute('CREATE TABLE IF NOT EXISTS schedule_recommendations (chain TEXT NOT NULL, address_key TEXT NOT NULL, frequency INTEGER NOT NULL, days TEXT NOT NULL, minimum REAL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (chain,address_key))')
    if 'recommended_source' not in {row[1] for row in db.execute('PRAGMA table_info(schedule_recommendations)')}:
        try:db.execute('ALTER TABLE schedule_recommendations ADD COLUMN recommended_source TEXT')
        except sqlite3.OperationalError:
            if 'recommended_source' not in {row[1] for row in db.execute('PRAGMA table_info(schedule_recommendations)')}:raise
    if 'companion_limit' not in {row[1] for row in db.execute('PRAGMA table_info(schedule_recommendations)')}:
        try:db.execute('ALTER TABLE schedule_recommendations ADD COLUMN companion_limit INTEGER')
        except sqlite3.OperationalError:
            if 'companion_limit' not in {row[1] for row in db.execute('PRAGMA table_info(schedule_recommendations)')}:raise
    db.execute('CREATE TABLE IF NOT EXISTS schedule_settings (id INTEGER PRIMARY KEY CHECK(id=1), companion_limit INTEGER NOT NULL)')
    project_xml.init(db)
    db.commit()
    return db

def valid_value(value):
    if not isinstance(value,dict): raise ValueError('Ожидается объект рекомендации')
    frequency,days,minimum=value.get('frequency',0),value.get('days',[]),value.get('minimum')
    if isinstance(frequency,bool) or not isinstance(frequency,int) or not 0<=frequency<=7: raise ValueError('Частота должна быть от 0 до 7')
    if not isinstance(days,list) or any(isinstance(d,bool) or not isinstance(d,int) or not 0<=d<=6 for d in days) or len(set(days))!=len(days) or len(days)>frequency: raise ValueError('Некорректный набор дней')
    if minimum is not None and (isinstance(minimum,bool) or not isinstance(minimum,(int,float)) or not math.isfinite(minimum) or not 0<=minimum<=1000000): raise ValueError('Некорректная минимальная партия')
    return frequency,json.dumps(days),minimum

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_json(self,status,value):
        data=json.dumps(value,ensure_ascii=False,separators=(',',':')).encode('utf-8')
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        with PROJECT_LOCK:self.get_project()
    def get_project(self):
        path=urlsplit(self.path)
        if path.path=='/api/database.xml':
            try:
                with tempfile.TemporaryFile() as payload:
                    with closing(connect()) as db:
                        db.execute('BEGIN')
                        project_xml.export(db,ROOT,payload)
                    size=payload.tell();payload.seek(0)
                    name='sns-project-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.xml'
                    self.send_response(200);self.send_header('Content-Type','application/xml; charset=utf-8');self.send_header('Content-Disposition','attachment; filename="'+name+'"');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(size));self.end_headers();shutil.copyfileobj(payload,self.wfile,1024*1024)
                return
            except (sqlite3.Error,OSError,ValueError):return self.send_json(500,{'error':'Не удалось выгрузить все данные проекта'})
        if path.path.startswith('/data/'):
            name=path.path.lstrip('/')
            if not project_xml.allowed(name):return self.send_error(404)
            with closing(connect()) as db:
                row=db.execute('SELECT content FROM project_files WHERE name=?',(name,)).fetchone()
                imported=db.execute('SELECT 1 FROM project_files LIMIT 1').fetchone()
            if row:
                payload=row[0]
                self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
                return
            if imported:return self.send_error(404)
        if path.path=='/api/schedule':
            chain=parse_qs(path.query).get('chain',[''])[0]
            if chain not in CHAINS: return self.send_json(400,{'error':'Неизвестная цепь'})
            try:
                with closing(connect()) as db, db:
                    items=db.execute('SELECT address_key,frequency,days,minimum,recommended_source,companion_limit FROM schedule_recommendations WHERE chain=?',(chain,)).fetchall()
                    setting=db.execute('SELECT companion_limit FROM schedule_settings WHERE id=1').fetchone()
                return self.send_json(200,{'records':{k:{'frequency':f,'days':json.loads(d),'minimum':m,'source':source or '','companion_limit':limit} for k,f,d,m,source,limit in items},'settings':{'companion_limit':setting[0] if setting else 5}})
            except sqlite3.Error:return self.send_json(500,{'error':'База графиков недоступна'})
        target=Path(self.translate_path(path.path)).resolve()
        if target.parent==DB.resolve().parent and target.name in (DB.name,DB.name+'-journal',DB.name+'-wal',DB.name+'-shm'):return self.send_error(404)
        if not any(target.is_relative_to((ROOT/folder).resolve()) for folder in ('site','data')):return self.send_error(404)
        return super().do_GET()
    def do_HEAD(self):self.send_error(405)
    def do_POST(self):
        with PROJECT_LOCK:self.post_project()
    def post_project(self):
        endpoint=urlsplit(self.path).path
        if endpoint not in ('/api/schedule','/api/database.xml'):return self.send_error(404)
        origin=self.headers.get('Origin')
        if origin:
            parsed=urlsplit(origin)
            if parsed.scheme!='http' or parsed.netloc.lower()!=self.headers.get('Host','').lower() or parsed.path or parsed.query or parsed.fragment:return self.send_json(403,{'error':'Недопустимый источник запроса'})
        expected='application/xml' if endpoint=='/api/database.xml' else 'application/json'
        if self.headers.get('Content-Type','').split(';')[0].strip().lower()!=expected:return self.send_json(415,{'error':'Неверный формат данных'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=(project_xml.MAX_XML if endpoint=='/api/database.xml' else 2000000):raise ValueError('Некорректный размер запроса')
            if endpoint=='/api/database.xml':
                with tempfile.TemporaryFile() as stream:
                    remaining=length
                    while remaining:
                        block=self.rfile.read(min(1024*1024,remaining))
                        if not block:raise ValueError('Загрузка XML прервана')
                        stream.write(block);remaining-=len(block)
                    stream.seek(0)
                    backup=DB.parent/'backups'/('before-import-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.sqlite3')
                    backup.parent.mkdir(parents=True,exist_ok=True)
                    with closing(connect()) as db,closing(sqlite3.connect(backup)) as copy:db.backup(copy)
                    with closing(connect()) as db:result=project_xml.restore(db,stream,valid_value,CHAINS)
                result['backup']=str(backup)
                return self.send_json(200,result)
            raw=self.rfile.read(length)
            data=json.loads(raw.decode('utf-8'))
            if not isinstance(data,dict):raise ValueError('Некорректный запрос')
            chain=data.get('chain');records=data.get('records');mode=data.get('mode','update')
            if chain not in CHAINS or mode not in ('update','import') or not isinstance(records,dict) or len(records)>10000:raise ValueError('Некорректный запрос')
            settings=data.get('settings')
            if settings is not None:
                if not isinstance(settings,dict) or set(settings)!={'companion_limit'}:raise ValueError('Некорректные настройки')
                setting_limit=settings['companion_limit']
                if isinstance(setting_limit,bool) or not isinstance(setting_limit,int) or not 0<=setting_limit<=1000:raise ValueError('Количество попутчиков должно быть целым числом от 0 до 1000')
            prepared=[]
            for key,value in records.items():
                if not isinstance(key,str) or len(key)>4000:raise ValueError('Некорректный адрес')
                frequency,days,minimum=valid_value(value); source=value.get('source','')
                if not isinstance(source,str) or len(source)>300:raise ValueError('Некорректный источник')
                limit=value.get('companion_limit')
                if limit is not None and (isinstance(limit,bool) or not isinstance(limit,int) or not 0<=limit<=1000):raise ValueError('Количество попутчиков должно быть целым числом от 0 до 1000')
                prepared.append((chain,key,frequency,days,minimum,source,limit))
            with closing(connect()) as db, db:
                if settings is not None:db.execute('INSERT INTO schedule_settings(id,companion_limit) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET companion_limit=excluded.companion_limit',(setting_limit,))
                if mode=='import': db.executemany('INSERT OR IGNORE INTO schedule_recommendations(chain,address_key,frequency,days,minimum,recommended_source,companion_limit) VALUES(?,?,?,?,?,?,?)',prepared)
                else: db.executemany('INSERT INTO schedule_recommendations(chain,address_key,frequency,days,minimum,recommended_source,companion_limit) VALUES(?,?,?,?,?,?,?) ON CONFLICT(chain,address_key) DO UPDATE SET frequency=excluded.frequency,days=excluded.days,minimum=excluded.minimum,recommended_source=excluded.recommended_source,companion_limit=excluded.companion_limit,updated_at=CURRENT_TIMESTAMP',prepared)
            return self.send_json(200,{'ok':True})
        except (ValueError,TypeError,UnicodeDecodeError,json.JSONDecodeError) as exc:return self.send_json(400,{'error':str(exc)})
        except sqlite3.Error:return self.send_json(500,{'error':'Не удалось сохранить в базе'})
        except OSError:return self.send_json(500,{'error':'Не удалось прочитать или сохранить файлы проекта'})

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Сервер графика поставок SNS')
    parser.add_argument('--host',default=os.environ.get('SNS_HOST','127.0.0.1'))
    parser.add_argument('--port',type=int,default=int(os.environ.get('SNS_PORT','4179')))
    parser.add_argument('--db',default=os.environ.get('SNS_DB',str(DB)))
    parser.add_argument('--backup',metavar='FILE')
    args=parser.parse_args();DB=Path(args.db).expanduser().resolve()
    if args.backup:
        destination=Path(args.backup).expanduser().resolve()
        if destination==DB or destination.exists():parser.error('Файл резервной копии уже существует или совпадает с базой')
        if not DB.is_file():parser.error('Исходная база не найдена')
        destination.parent.mkdir(parents=True,exist_ok=True)
        with closing(connect()) as source,closing(sqlite3.connect(destination)) as target:source.backup(target)
        print(f'Резервная копия создана: {destination}')
    else:
        with closing(connect()):pass
        print(f'SNS: http://{args.host}:{args.port}/site/ | база: {DB}',flush=True)
        ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()

