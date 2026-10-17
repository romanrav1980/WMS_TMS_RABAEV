import { useEffect, useRef, useState } from "react";
import { listReceiptPhotos, uploadReceiptPhoto } from "./photoApi";
import { isAuthError } from "./api";
import type { StorePreview, StoreCredentials, ReceiptPhoto } from "./contracts";

export const photoViews = [{ code: "FRONT", label: "Спереди" }, { code: "LEFT", label: "Слева" }, { code: "RIGHT", label: "Справа" }];
export function useStorePhotos(preview: StorePreview, credentials: StoreCredentials, onAuthError: () => void) {
 const scope = credentials.username + ":" + preview.load_operation_id + ":" + preview.store_address;
 const current = useRef(scope), [photos, setPhotos] = useState<ReceiptPhoto[]>([]), [busy, setBusy] = useState(false), [message, setMessage] = useState("");
 const [retry, setRetry] = useState<{ file: File; view: string } | null>(null);
 const visible = photoViews.map(view => ({ ...view, photo: [...photos].reverse().find(photo => photo.view === view.code) }));
 const unique = new Set<string>();
 const evidence = visible.flatMap(view => { if (!view.photo || unique.has(view.photo.sha256)) return []; unique.add(view.photo.sha256); return [view.photo.photo_id]; });
 function fail(error: unknown) { setMessage(String(error).replace(/^Error: /, "")); if (isAuthError(error)) onAuthError(); }
 async function refresh() {
  if (busy) return;
  setBusy(true);
  try { const rows = await listReceiptPhotos(preview.load_operation_id, preview.store_address, credentials); if (current.current === scope) setPhotos(rows); }
  catch (error) { if (current.current === scope) fail(error); }
  finally { if (current.current === scope) setBusy(false); }
 }
 useEffect(() => { current.current = scope; setPhotos([]); setRetry(null); setMessage(""); void refresh(); return () => { current.current = ""; }; }, [scope]);
 async function upload(file: File, view: string) {
  if (busy) return;
  if (!["image/jpeg", "image/png"].includes(file.type) || file.size > 4 * 1024 * 1024) { setMessage("Выберите JPEG/PNG до 4 МБ. При необходимости уменьшите размер фотографии."); return; }
  setBusy(true); setMessage(""); setRetry({ file, view });
  try {
   await uploadReceiptPhoto(preview.load_operation_id, preview.store_address, view, file, credentials);
   const rows = await listReceiptPhotos(preview.load_operation_id, preview.store_address, credentials);
   if (current.current === scope) { setPhotos(rows); setRetry(null); setMessage("Фотография сохранена."); }
  } catch (error) { if (current.current === scope) fail(error); }
  finally { if (current.current === scope) setBusy(false); }
 }
 return { visible, evidence, busy, message, retry, upload, refresh };
}
