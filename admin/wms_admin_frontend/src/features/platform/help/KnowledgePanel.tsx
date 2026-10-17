import { useEffect, useRef, useState } from "react";
import { apiFetch } from "../../../api";
import { HelpButton } from "./HelpButton";
import { HELP_OPEN_EVENT, helpActions } from "./catalog";
import { readOfflinePublicKnowledge, type KnowledgeArticle as Article, type KnowledgeSummary as Summary } from "./offlinePublicKnowledge";
import "./help.css";

export function KnowledgePanel() {
  const [opened, setOpened] = useState(() => new URLSearchParams(location.search).has("help"));
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(() => new URLSearchParams(location.search).get("help") || "using-help");
  const [rows, setRows] = useState<Summary[]>([]);
  const [article, setArticle] = useState<Article | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [offline, setOffline] = useState(false);
  const [reload, setReload] = useState(0);
  const dialog = useRef<HTMLDialogElement>(null);
  const search = useRef<HTMLInputElement>(null);
  const trigger = useRef<HTMLElement | null>(null);
  const open = () => { trigger.current = document.activeElement as HTMLElement; setOpened(true); };
  const close = () => {
    setOpened(false); const url = new URL(location.href); url.searchParams.delete("help");
    history.replaceState(history.state, "", url); trigger.current?.focus();
  };
  useEffect(() => {
    const handler = (event: KeyboardEvent) => { if (event.key === "F1") { event.preventDefault(); open(); } };
    // «Подробнее» из подсказок любого экрана открывает нужную статью поверх работы, не сбрасывая её.
    const article = (event: Event) => { const id = (event as CustomEvent<string>).detail; if (id) { setSelected(id); setQuery(""); } open(); };
    window.addEventListener("keydown", handler);
    window.addEventListener(HELP_OPEN_EVENT, article);
    return () => { window.removeEventListener("keydown", handler); window.removeEventListener(HELP_OPEN_EVENT, article); };
  }, []);
  useEffect(() => {
    if (opened) { dialog.current?.showModal(); search.current?.focus(); }
    else dialog.current?.close();
  }, [opened]);
  useEffect(() => {
    if (!opened) return;
    const controller = new AbortController();
    setLoading(true); setError(""); setRows([]); setArticle(null); setOffline(false);
    const timer = window.setTimeout(() => {
      const path = query.trim() ? "/api/help/articles?query=" + encodeURIComponent(query.trim()) : "/api/help/articles/" + encodeURIComponent(selected);
      apiFetch<Summary[] | Article>(path, { signal: controller.signal }).then(data => {
        if (controller.signal.aborted) return;
        if (Array.isArray(data)) setRows(data); else setArticle(data);
      }).catch(reason => {
        if (controller.signal.aborted) return;
        // HTTP denials/errors remain authoritative; only a failed transport uses public copies.
        if (!(reason instanceof TypeError)) { setError(String(reason)); return; }
        setOffline(true);
        const copy = readOfflinePublicKnowledge(query, selected);
        if (Array.isArray(copy)) setRows(copy);
        else if (copy) setArticle(copy);
        else setError("Эта статья недоступна без связи. Откройте базовую инструкцию или повторите после восстановления сети.");
      })
        .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    }, 200);
    return () => { window.clearTimeout(timer); controller.abort(); };
  }, [opened, query, selected, reload]);
  const read = (id: string) => {
    setSelected(id); setQuery(""); const url = new URL(location.href); url.searchParams.set("help", id);
    history.replaceState(history.state, "", url);
  };
  return <>
    <div className="knowledge-launch"><HelpButton action="open" onClick={open}>?<span className="knowledge-launch-text"> Справка</span></HelpButton></div>
    <dialog ref={dialog} className="knowledge-panel" aria-labelledby="knowledge-title" onCancel={event => { event.preventDefault(); close(); }}>
      <header><h2 id="knowledge-title">База знаний retailcase</h2><HelpButton action="close" onClick={close}>Закрыть</HelpButton></header>
      <label htmlFor="knowledge-search">Найти инструкцию</label>
      <input id="knowledge-search" ref={search} value={query} maxLength={120} placeholder="Роли, связь, команды…"
        title={helpActions.search.text} data-help-id={helpActions.search.id} aria-describedby="knowledge-search-help"
        onChange={event => setQuery(event.target.value)} />
      <small id="knowledge-search-help">{helpActions.search.text}</small>
      <nav aria-label="Разделы справки">
        <HelpButton action="article" onClick={() => read("using-help")}>О справке</HelpButton>
        <HelpButton action="article" onClick={() => read("access-model")}>Роли и доступ</HelpButton>
        <HelpButton action="article" onClick={() => read("operation-recovery")}>Потеря связи</HelpButton>
      </nav>
      <div className="knowledge-content" aria-busy={loading}>
        {loading && <p role="status">Загрузка справки…</p>}
        {!loading && offline && <p role="status" data-help-id="knowledge.offline">Без связи · публичная копия из приложения. Опубликованная версия может отличаться.</p>}
        {error && <div role="alert"><p>Справка не загружена: {error}</p><HelpButton action="retry" onClick={() => setReload(value => value + 1)}>Повторить</HelpButton></div>}
        {!loading && !error && query.trim() && <><p role="status">Найдено: {rows.length}</p>{rows.map(row => <section key={row.article_id}>
          <HelpButton action="article" onClick={() => read(row.article_id)}>{row.title}</HelpButton><p>{row.summary}</p></section>)}</>}
        {!loading && !error && article && <article><h3>{article.title}</h3><p>{article.summary}</p>
          {article.body.split("\n\n").map((paragraph, index) => <p key={index}>{paragraph}</p>)}
          <h4>Связанные инструкции</h4>{article.related.map(item => <HelpButton key={item.article_id} action="article" onClick={() => read(item.article_id)}>{item.title}</HelpButton>)}
          <details><summary title="Показать проектные источники и редакцию инструкции для проверки актуальности." data-help-id="knowledge.provenance">Источники и редакция</summary>
            <p>Редакция: {article.revision}</p>{article.sources.map(source => <p key={source}>{source}</p>)}</details>
        </article>}
      </div>
    </dialog>
  </>;
}
