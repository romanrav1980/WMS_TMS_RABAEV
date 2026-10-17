import { useEffect, useRef, useState } from "react";

export interface HelpCredentials { username: string; password: string }
interface Article { article_id: string; title: string; summary: string; body: string; related: { id: string; title: string }[] }

/** Reads the published local knowledge service; no private articles are cached. */
export function NativeHelp({ articleId, credentials }: { articleId: string; credentials: HelpCredentials }) {
 const [open, setOpen] = useState<string | null>(null);
 const [article, setArticle] = useState<Article | null>(null);
 const [message, setMessage] = useState("");
 const [loadedFor, setLoadedFor] = useState("");
 const dialog = useRef<HTMLElement>(null), trigger = useRef<HTMLButtonElement>(null);
 const key = credentials.username + ":" + open;
 useEffect(() => {
  if (!open) return;
  const controller = new AbortController();
  setArticle(null); setLoadedFor(""); setMessage("Загрузка опубликованной справки…");
  dialog.current?.focus();
  const bytes = new TextEncoder().encode(credentials.username + ":" + credentials.password);
  const authorization = "Basic " + btoa(Array.from(bytes, byte => String.fromCharCode(byte)).join(""));
  void fetch("/api/help/articles/" + encodeURIComponent(open), { headers: { Authorization: authorization }, signal: controller.signal })
   .then(async response => {
    if (!response.ok) throw new Error(response.status === 401 || response.status === 403
     ? "Нет доступа к статье для текущей учётной записи." : "Статья сейчас недоступна. Проверьте связь с сервером.");
    const data = await response.json() as Record<string, unknown>;
    if (data.article_id !== open || typeof data.title !== "string" || typeof data.body !== "string") throw new Error("Сервер вернул неполную статью.");
    const related = Array.isArray(data.related) ? data.related.flatMap(row => {
     if (typeof row === "string") return [{ id: row, title: row }];
     if (row && typeof row.article_id === "string") return [{ id: row.article_id, title: String(row.title ?? row.article_id) }];
     return [];
    }) : [];
    if (!controller.signal.aborted) {
     setArticle({ article_id: open, title: data.title, summary: String(data.summary ?? ""), body: data.body, related });
     setLoadedFor(key); setMessage("База знаний · редакция " + String(data.revision ?? data.version ?? "—"));
    }
   }).catch(error => { if (!controller.signal.aborted) setMessage(error instanceof Error ? error.message : "Справка недоступна."); });
  return () => controller.abort();
 }, [open, credentials.username, credentials.password, key]);
 function close() { setOpen(null); trigger.current?.focus(); }
 const current = loadedFor === key ? article : null;
 return <>
  <button ref={trigger} type="button" title="Открыть инструкцию из встроенной базы знаний" data-help-id={articleId + ".help"} onClick={() => setOpen(articleId)}>Справка</button>
  {open && <div className="wms-help-overlay" onClick={close}>
   <section ref={dialog} tabIndex={-1} role="dialog" aria-modal="true" aria-label="Справка" className="wms-help-dialog"
    onClick={event => event.stopPropagation()} onKeyDown={event => { if (event.key === "Escape") close(); }}>
    <header><h2>{current?.title ?? "Справка"}</h2><button type="button" title="Закрыть справку и вернуться к сборке" data-help-id="help.close" aria-label="Закрыть справку" onClick={close}>×</button></header>
    <p role="status">{message}</p>
    {current && <><p>{current.summary}</p>{current.body.split(/\r?\n\r?\n/).map((text, index) => <p key={index}>{text}</p>)}
     <nav aria-label="Связанные инструкции">{current.related.map(row => <button type="button" key={row.id}
      title="Открыть связанную статью в приложении" data-help-id="help.related" onClick={() => setOpen(row.id)}>{row.title}</button>)}</nav>
    </>}
   </section>
  </div>}
 </>;
}
