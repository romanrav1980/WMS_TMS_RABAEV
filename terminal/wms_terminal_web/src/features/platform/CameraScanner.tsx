import { useEffect, useRef, useState } from "react";
import { createCameraReader, decodePhoto, type CameraControls } from "./cameraDecoder";

export function CameraScanner({ onCode, onClose }: { onCode: (code: string) => void; onClose: () => void }) {
 const video = useRef<HTMLVideoElement>(null), controls = useRef<CameraControls | undefined>(undefined);
 const active = useRef(true), file = useRef<HTMLInputElement>(null);
 const [message, setMessage] = useState("Наведите камеру на этикетку: штрихкод, QR или DataMatrix.");
 const [busy, setBusy] = useState(false);
 useEffect(() => {
  let cancelled = false;
  active.current = true;
  if (!navigator.mediaDevices?.getUserMedia || !window.isSecureContext) {
   setMessage("Камера недоступна по этому адресу. Откройте приложение через HTTPS или считайте код с фотографии.");
  } else {
   void createCameraReader().decodeFromConstraints({ audio: false, video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 } } },
    video.current!, (result, _error, camera) => {
     if (!cancelled && active.current && result) { active.current = false; camera.stop(); onCode(result.getText()); }
    }).then(camera => { if (!cancelled && active.current) controls.current = camera; else camera.stop(); })
    .catch(() => { if (!cancelled && active.current) setMessage("Нет доступа к камере. Разрешите её в браузере или считайте код с фотографии."); });
  }
  return () => { cancelled = true; active.current = false; controls.current?.stop(); };
 }, []); // callbacks belong to this mounted scan, never a later recipient
 async function readPhoto(value: File) {
  controls.current?.stop(); setBusy(true);
  try { const code = await decodePhoto(value); if (active.current) { active.current = false; onCode(code); } }
  catch (error) { if (active.current) setMessage(String(error).replace(/^Error: /, "")); }
  finally { if (active.current) setBusy(false); }
 }
 return <div className="store-app-help-overlay" role="presentation">
  <section className="store-app-help-panel store-app-camera" role="dialog" aria-label="Сканирование кода" aria-modal="true">
   <header className="store-app-header"><h2>Сканировать код</h2><button type="button" title="Выключить камеру и вернуться к приёмке" data-help-id="scanner.close" onClick={onClose}>Закрыть</button></header>
   <video ref={video} playsInline muted aria-label="Изображение камеры" style={{ width: "100%", maxHeight: "45dvh", objectFit: "cover", borderRadius: 12 }} />
   <p role="status">{message}</p>
   <input ref={file} type="file" accept="image/*" capture="environment" hidden aria-label="Фотография кода" onChange={event => { const image = event.target.files?.[0]; if (image) void readPhoto(image); }} />
   <button type="button" title="Сфотографировать этикетку и распознать код на устройстве" data-help-id="scanner.photo" disabled={busy} onClick={() => file.current?.click()}>Считать с фото</button>
  </section>
 </div>;
}
