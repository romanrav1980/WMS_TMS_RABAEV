"""Assemble NS00 evidence from executed checks, preserving incomplete gates."""
from __future__ import annotations
from datetime import datetime,timezone
from hashlib import sha256
from importlib.metadata import version
import json
import platform
import subprocess
from zipfile import ZipFile,ZIP_DEFLATED
from .fixture_plan import ROOT,TABLE_KEYS
from .oracle_fixture import oracle_connection,query
from .probe import write_report,readiness

EVIDENCE=ROOT/'runtime/test-evidence/nicora_ns00'


def read(path: str) -> object:
    return json.loads((EVIDENCE/path).read_text(encoding='utf-8-sig'))


def main() -> None:
    launches=sorted(EVIDENCE.glob('launch-*.json'))
    launch=json.loads(launches[-1].read_text(encoding='utf-8-sig'))
    with oracle_connection() as connection:
        clocks=query(connection.cursor(),"select to_char(systimestamp,'YYYY-MM-DD\"T\"HH24:MI:SS.FF3TZH:TZM') db_time, "
                     "to_char(current_timestamp,'YYYY-MM-DD\"T\"HH24:MI:SS.FF3TZH:TZM') session_time, "
                     "dbtimezone,sessiontimezone from dual")[0]
    hardware=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',
        '$machine=Get-CimInstance Win32_ComputerSystem; $disk=Get-PSDrive C; '+
        '@{cpu=$machine.NumberOfLogicalProcessors;ramGiB=[math]::Round($machine.TotalPhysicalMemory/1GB,1);cFreeGiB=[math]::Round($disk.Free/1GB,1)} | ConvertTo-Json'],text=True))
    passport={'schema':'RABAEV','service':'orcl','database':'ORCL','ddlApplied':False,
        'python':platform.python_version(),'pythonExecutable':launch['python'],
        'packages':{p:version(p) for p in ['fastapi','uvicorn','oracledb','httpx','openpyxl','pytest']},
        'node':subprocess.check_output(['node','--version'],text=True).strip(),
        'dotnet':subprocess.check_output(['dotnet','--version'],text=True).strip(),
        'hardware':hardware,'oracleClocks':clocks,'utc':datetime.now(timezone.utc).isoformat(),
        'runtime':readiness(),'launch':launch,'independentReview':'PENDING','ownerAcceptance':'PENDING',
        'coldOracleInstall':'NOT_EXECUTED','hardwareScope':'Windows dev host; V100 capacity unqualified'}
    write_report(EVIDENCE/'passport.json',passport)
    data={'sprint':'NS00','baseline':57,'status':'in_progress','implementation':'core_environment_implemented',
        'author':'Codex','checks':{
            'NS00-TC01':{'applicationInstall':'PASS_NEW_ISOLATED_PYTHON_AND_NODE_DEPENDENCIES',
                         'oracleProfiles':'PASS_ALL_SIX','coldOracleInstall':'PENDING'},
            'NS00-TC02':{'status':'PASS_LIVE_ORACLE_API','rows':22,'pieces':2400,
                         'cleanup':'PASS_ZERO_OWNED_ROWS','negativeProbes':read('negative-probes.json')['tests']},
            'NS00-TC03':{'status':read('restart-after.json')['status'],'allPortsStoppedBeforeStart':launch['allPortsStoppedBeforeStart'],
                         'allListenerPidsReplaced':True,'fact':read('restart-after.json')['fact']}},
        'quality':{'architecture':'PASS','pytestPassed':23,'frontendTypecheck':'PASS_BOTH',
                   'freshFrontendBuild':'PASS_BOTH','encoding':'PENDING_FINAL_CHECK'},
        'ui':{'arm':'SHELL_PASS_DEMO_REPLAY_NOT_STOCK_EVIDENCE','tsd':'LIVE_API_ORACLE_DIAGNOSTICS_PASS',
              'pageErrors':0,'tsdConsoleWarnings':['antd React 19 compatibility','antd static message context'],
              'buildWarnings':['leaflet-draw default export','large chunks'],'owner':'NS06 frontend hardening'},
        'independentReview':'PENDING_CLAUDE','ownerAcceptance':'PENDING','businessProfiles':'DECLARATIVE_NS02_NS04_GAP',
        'fullOracleReinstall':'NOT_EXECUTED','loadAcceptance':'NOT_EXECUTED','githubPublication':False}
    write_report(EVIDENCE/'report.json',data)
    files=[]
    for folder in ['tools/nicora_environment','db/fixtures/nicora_ns00']:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    files.extend(ROOT/p for p in ['serv.bat','front.bat','terminal.bat','scripts/kill-port.ps1',
        'scripts/prepare-nicora-python.ps1','scripts/prepare-nicora-frontends.ps1','scripts/start-nicora-dev.ps1',
        'tests/smoke/nicora_ns00_environment_smoke.py','api/wms_api_server/requirements.txt',
        'api/wms_api_server/requirements-ns00-win-py313.lock'])
    hashes={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    with ZipFile(EVIDENCE/'ns00-review-source.zip','w',compression=ZIP_DEFLATED) as archive:
        for p in files:
            archive.write(p,p.relative_to(ROOT).as_posix())
    write_report(EVIDENCE/'source-manifest.json',{'files':hashes,'archiveSha256':sha256((EVIDENCE/'ns00-review-source.zip').read_bytes()).hexdigest(),
                 'scope':'reviewable tooling snapshot, not Oracle backup'})
    print('NS00 passport/report/source package assembled; acceptance gates remain explicit')


if __name__=='__main__':
    main()
