import { useRef, useState } from "react";
import { CameraScanner } from "./CameraScanner";

interface ScanFieldProps {
 label: string; value: string; onChange: (code: string) => void;
 disabled?: boolean; onSubmit?: (code: string) => void; autoFocus?: boolean;
}

export function ScanField({ label, value, onChange, disabled, onSubmit, autoFocus }: ScanFieldProps) {
 const [camera, setCamera] = useState(false), [message, setMessage] = useState("");
 const input = useRef<HTMLInputElement>(null);
 function accept(code: string) {
  if (!code || disabled) return;
  onChange(code); setCamera(false); setMessage("Код считан. " + (onSubmit ? "Проверьте и подтвердите." : ""));
  requestAnimationFrame(() => input.current?.focus());
 }
 return <div className="store-app-scan-field">
  <label>{label}<input ref={input} title="Считайте код USB/Bluetooth-сканером или введите с этикетки" data-help-id="scanner.input"
   autoFocus={autoFocus} autoComplete="off" autoCapitalize="off" spellCheck={false} value={value} disabled={disabled}
   onChange={event => { onChange(event.target.value); setMessage(""); }}
   onKeyDown={event => { if (event.key === "Enter") { event.preventDefault(); if (value && onSubmit) onSubmit(value); } }} /></label>
  <div className="store-app-inline-actions">
   <button type="button" title="Открыть камеру для считывания штрихкода, QR или DataMatrix" data-help-id="scanner.camera" disabled={disabled} onClick={() => setCamera(true)}>Камера</button>
   <button type="button" title="Установить курсор для USB/Bluetooth-сканера с завершением Enter" data-help-id="scanner.hid" disabled={disabled} onClick={() => { input.current?.focus(); setMessage("Сканер подключён к телефону или ТСД как клавиатура. Считайте этикетку; завершение — Enter."); }}>Сканер / ввод</button>
  </div>
  {message && <p className="store-app-hint" role="status">{message}</p>}
  {camera && !disabled && <CameraScanner onCode={accept} onClose={() => setCamera(false)} />}
 </div>;
}
