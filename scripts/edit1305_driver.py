from pathlib import Path
p=Path("admin/wms_admin_frontend/src/components/DriverMobilePage.tsx")
s=p.read_text(encoding="utf-8")
lines=s.splitlines()
for i,line in enumerate(lines):
 if 'aria-label="?????' in line: lines[i]=line.replace('aria-label="?????"','aria-label="Выйти"')
 if '<strong>????' in line: lines[i]='        <strong>Ожидает подтверждения: рейс #{pending.trip}</strong>'
 if '<p>????' in line: lines[i]='        <p>Отметка сохранена на этом устройстве. Повтор не изменит первоначальное время.</p>'
 if 'onClick={()=>void retry()}' in line: lines[i]='        <button disabled={opLoading} onClick={()=>void retry()}>Повторить сохранённую отметку</button>'
 if 'role="status">????' in line: lines[i]='      {loading && activeView !== "trips" && <div className="driver-loading" role="status">Загрузка рейса…</div>}'
 if 'tripOps.length === 0' in line: lines[i]='          {!loading && tripOps.length === 0 && <div className="driver-empty">Операции рейса ещё не запланированы диспетчером.</div>}'
s="\n".join(lines)+"\n"
s=s.replace('import { DriverLogin, useDriverWorkspace }','import "../features/transport/DriverWorkspace.css";\nimport { DriverLogin, useDriverWorkspace }')
p.write_text(s,encoding="utf-8")
