"""Bounded read-only native source checkpoint; never overwrite before images."""
import argparse, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]


def object_key(value:str)->tuple[str,str]:
    kind,separator,name=value.partition(':');kind=kind.replace('_',' ').upper();name=name.upper()
    if not separator or kind not in {'PACKAGE','PACKAGE BODY','PROCEDURE','FUNCTION','TRIGGER'}or not re.fullmatch(r'[A-Z][A-Z0-9_$#]{0,127}',name):
        raise argparse.ArgumentTypeError('Use exact source type:name, e.g. PACKAGE_BODY:RRL_NAME')
    return kind,name


def capture(objects:list[tuple[str,str]],folder:Path)->dict:
    from stock_posting_environment import load_local_oracle_environment
    load_local_oracle_environment()
    from app.db import oracle_connection
    if not 1<=len(objects)<=16 or len(set(objects))!=len(objects):raise ValueError('Capture1..16 distinct sources')
    folder=folder.resolve();folder.relative_to(ROOT)
    if folder.exists()and any(folder.iterdir()):raise ValueError('Before-image directory must be new/empty')
    sources=[]
    with oracle_connection()as connection:
        cursor=connection.cursor()
        try:
            cursor.execute('set transaction read only')
            cursor.execute("select user,sys_context('USERENV','SERVICE_NAME'),sys_context('USERENV','SERVER_HOST')from dual")
            schema,service,host=cursor.fetchone()
            if schema!='RABAEV'or service.lower()!='orcl':raise ValueError('Expected isolated dev RABAEV/orcl')
            cursor.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");invalid=cursor.fetchone()[0]
            for kind,name in objects:
                cursor.execute('select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE',name=name,kind=kind)
                source=''.join(row[0]for row in cursor.fetchall())
                if not source:raise ValueError('Missing source '+kind+':'+name)
                cursor.execute('select LINE,POSITION,TEXT from USER_ERRORS where NAME=:name and TYPE=:kind order by SEQUENCE',name=name,kind=kind)
                errors=[dict(line=r[0],position=r[1],text=r[2])for r in cursor.fetchall()]
                sources.append((kind,name,source,errors))
        finally:connection.rollback()
    folder.mkdir(parents=True,exist_ok=True)
    manifest=dict(captured_at_utc=datetime.now(timezone.utc).isoformat(),schema=schema,service=service,host=host,read_only=True,invalid_count=invalid,sources=[])
    for kind,name,source,errors in sources:
        filename=name.lower()+'_'+kind.lower().replace(' ','_')+'.sql';payload=('create or replace '+source.rstrip()+'\n/\n').encode('utf-8')
        with(folder/filename).open('xb')as stream:stream.write(payload)
        manifest['sources'].append(dict(name=name,type=kind,file=filename,errors=errors,user_source_sha256=hashlib.sha256(source.encode('utf-8')).hexdigest(),normalized_source_sha256=hashlib.sha256(source.replace('\r','').encode('utf-8')).hexdigest(),artifact_sha256=hashlib.sha256(payload).hexdigest()))
    with(folder/'manifest.json').open('x',encoding='utf-8')as stream:json.dump(manifest,stream,ensure_ascii=False,indent=2);stream.write('\n')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True,type=Path);parser.add_argument('--object',action='append',required=True,type=object_key)
    args=parser.parse_args();result=capture(args.object,args.out)
    print(json.dumps(dict(status='CAPTURED_READ_ONLY',objects=len(result['sources']),invalid_count=result['invalid_count'],out=str(args.out))))
