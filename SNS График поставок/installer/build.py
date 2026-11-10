from pathlib import Path
import argparse, hashlib, json, shutil, sqlite3, subprocess, sys, tempfile, zipfile
from contextlib import closing
root=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(root))
import project_xml
parser=argparse.ArgumentParser()
parser.add_argument('--db',type=Path,default=root/'runtime'/'schedule.sqlite3')
args=parser.parse_args()
out=root/'installer'/'SNS-Setup.exe'
csc=Path(r'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe')
python=Path(sys.base_prefix)
with tempfile.TemporaryDirectory(prefix='sns-build-',dir=root/'installer') as temp:
 stage=Path(temp)/'payload'; stage.mkdir(); rt=stage/'python';rt.mkdir()
 for name in ['python.exe','pythonw.exe','python313.dll','python3.dll','vcruntime140.dll','vcruntime140_1.dll','LICENSE.txt']:shutil.copy2(python/name,rt/name)
 dlls=rt/'DLLs';dlls.mkdir()
 for item in (python/'DLLs').iterdir():
  if item.suffix.lower() in ('.pyd','.dll') and not item.name.startswith('_test') and item.name not in ('_tkinter.pyd','tcl86t.dll','tk86t.dll'):shutil.copy2(item,dlls/item.name)
 (rt/'python313._pth').write_text('python313.zip\nDLLs\n.\n',encoding='utf-8')
 if (python/'python313.zip').is_file():
  shutil.copy2(python/'python313.zip',rt/'python313.zip')
 else:
  with zipfile.ZipFile(rt/'python313.zip','w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
   for f in (python/'Lib').rglob('*.py'):
    rel=f.relative_to(python/'Lib')
    if any(x in ('site-packages','test','tests','idlelib','tkinter','ensurepip','venv','__pycache__') for x in rel.parts):continue
    z.write(f,rel.as_posix())
 for folder in ['site']:
  shutil.copytree(root/folder,stage/folder)
 for name in ['server.py','database_xml.py','project_xml.py','start_server.py']:shutil.copy2(root/name,stage/name)
 (stage/'runtime').mkdir()
 if not args.db.is_file():raise FileNotFoundError(args.db)
 with closing(sqlite3.connect(args.db)) as source,closing(sqlite3.connect(stage/'runtime'/'schedule.sqlite3')) as target:
  source.backup(target)
  project_xml.init(target);target.commit()
  assert target.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
  manifest={}
  for name,content in project_xml.assets(target,root):
   dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
   manifest[name]={'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()}
  if not project_xml.REQUIRED<=set(manifest):raise ValueError('Incomplete package datasets')
  # The installed files are the seed snapshot; avoid duplicating them in SQLite.
  target.execute('DELETE FROM project_files');target.commit();target.execute('VACUUM')
  manifest['recommendation_rows']=target.execute('SELECT COUNT(*) FROM schedule_recommendations').fetchone()[0]
 (root/'installer'/'package-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 shutil.copy2(root/'installer'/'Установка.txt',stage/'Установка.txt')
 launcher=stage/'График поставок.exe'
 subprocess.run([str(csc),'/nologo','/target:winexe','/codepage:65001','/reference:System.Windows.Forms.dll','/out:'+str(launcher),str(root/'installer'/'Launcher.cs')],check=True)
 subprocess.run([str(rt/'python.exe'),'-c','import sys;sys.path.insert(0,".");import sqlite3,http.server,ssl,unicodedata,project_xml,server; print("portable Python and application OK")'],cwd=stage,check=True)
 payload=Path(temp)/'payload.zip'
 with zipfile.ZipFile(payload,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for f in stage.rglob('*'):
   if f.is_file():z.write(f,f.relative_to(stage).as_posix())
 subprocess.run([str(csc),'/nologo','/target:winexe','/codepage:65001','/reference:System.Windows.Forms.dll','/reference:System.IO.Compression.dll','/reference:System.IO.Compression.FileSystem.dll','/reference:Microsoft.CSharp.dll','/resource:'+str(payload)+',payload.zip','/out:'+str(out),str(root/'installer'/'Setup.cs')],check=True)
print('Installer:',out,'size:',out.stat().st_size)
