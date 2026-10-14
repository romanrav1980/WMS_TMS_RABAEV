from pathlib import Path
import json
p=Path("admin/wms_admin_frontend/src/components/TransportRouteInput.tsx");s=p.read_text(encoding="utf-8")
s=s.replace('import {useEffect, useRef, useState} from "react";','import {useEffect, useRef, useState} from "react";\nimport {TransportRoadLegs} from "./TransportRoadLegs";')
needle='    {message && <p role="status">{message}</p>}'
addition="""    <TransportRoadLegs tripId={tripId} apiBase={apiBase} headers={headers} actor={actor} onChoose={value=>{
      if(!context||context.source_hash!==value.source_hash){setMessage("Перечитайте текущий маршрут перед использованием матрицы.");return;}
      setDrive(String(value.drive_min));setBack(String(value.drive_back_min));
      setSource("Дорожная матрица, снимок "+value.road_snapshot_signature);
      setMessage("Время подставлено для рассмотрения. Укажите основание и подтвердите оценку отдельно.");
    }}/>
"""
assert needle in s;s=s.replace(needle,addition+needle)
print(json.dumps({str(p):s},ensure_ascii=True))
