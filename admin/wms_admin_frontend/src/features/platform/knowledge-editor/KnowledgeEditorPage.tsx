import { useCallback, useState } from "react";
import { HelpButton } from "../help/HelpButton";
import { PendingCommandBanner, useApiRead, useMetadataCommands } from "../access-admin";
import type { CommandReceipt, PendingCommand } from "../access-admin";
import { ArticleEditor } from "./ArticleEditor";
import { WikiImportPanel } from "./WikiImportPanel";
import { editorHelp } from "./help";
import { clearLocalDraftIfSent } from "./localDraft";
import type { Article, ArticleStatus, ArticleSummary, KnowledgeSpace } from "./types";
import "../access-admin/access-admin.css";
import "./knowledge-editor.css";

/** Редактор базы знаний поверх /api/knowledge/* (C0056 блок 3). Читателю — только опубликованная разрешённая редакция (сервер). */
export function KnowledgeEditorPage({ onBack }: { onBack?: () => void }) {
  const [reload, setReload] = useState(0);
  const [space, setSpace] = useState("");
  const [status, setStatus] = useState<"" | ArticleStatus>("");
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState("");
  const [openId, setOpenId] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [mode, setMode] = useState<"articles" | "wiki">("articles");
  const spaces = useApiRead<KnowledgeSpace[]>("/api/knowledge/spaces", reload);
  const params = new URLSearchParams({ limit: "100" });
  if (space) params.set("space_id", space); if (status) params.set("status", status); if (submitted) params.set("query", submitted);
  const list = useApiRead<ArticleSummary[]>("/api/knowledge/articles?" + params, reload);
  const known = useApiRead<ArticleSummary[]>("/api/knowledge/articles?limit=100", reload);
  const article = useApiRead<Article>(openId ? "/api/knowledge/articles/" + encodeURIComponent(openId) : null, reload);
  // Решение по исходному намерению (command.command_type), а не по native-типу квитанции: импорт wiki возвращает ARTICLE_SAVE.
  const onDone = useCallback((receipt: CommandReceipt, command: PendingCommand) => {
    if (command.command_type === "ARTICLE_SAVE") { clearLocalDraftIfSent(receipt.object_id, command.payload); setOpenId(receipt.object_id); setCreating(false); }
    if (command.command_type === "WIKI_IMPORT") { setMode("articles"); setCreating(false); if (receipt.object_id) setOpenId(receipt.object_id); }
    setReload(n => n + 1);
  }, []);
  const commands = useMetadataCommands("knowledge", onDone);
  const submit = (type: string, payload: Record<string, unknown>, label: string, endpoint?: string) => void commands.submit(type, payload, label, "KNOWLEDGE." + type, endpoint);
  const current = creating ? null : article.data;
  return <main className="aa-page" aria-labelledby="ke-title">
    <header className="aa-header">
      {onBack && <HelpButton help={{ id: "knowledge.editor.back", text: "Вернуться к предыдущему экрану. Текст в браузере сохраняется.", article: "knowledge-editor" }} onClick={onBack}>← Назад</HelpButton>}
      <h2 id="ke-title">База знаний: редактор</h2>
      <HelpButton help={editorHelp.refresh} onClick={() => setReload(n => n + 1)}>Обновить</HelpButton>
      <div className="ke-mode" role="tablist" aria-label="Раздел">
        <button role="tab" aria-selected={mode === "articles"} title={editorHelp.open.text} data-help-id="knowledge.editor.mode.articles" onClick={() => setMode("articles")}>Статьи</button>
        <button role="tab" aria-selected={mode === "wiki"} title={editorHelp.wikiTab.text} data-help-id={editorHelp.wikiTab.id} onClick={() => setMode("wiki")}>Из wiki</button>
      </div>
    </header>
    <PendingCommandBanner pending={commands.pending} busy={commands.busy} message={commands.message} help={editorHelp}
      onCheck={() => void commands.check()} onRetry={() => void commands.retry()} onArchive={commands.archive} />
    {mode === "wiki" && <WikiImportPanel known={known.data ?? []} reload={reload} blocked={commands.blocked} busy={commands.busy}
      onImport={(payload, label) => submit("WIKI_IMPORT", payload, label, "/api/knowledge/wiki-sources/import")} />}
    {mode === "articles" && <div className="ke-layout">
      <aside className="ke-list" aria-label="Статьи">
        <form className="aa-inline" onSubmit={e => { e.preventDefault(); setSubmitted(query.trim()); }}>
          <label>Поиск<input value={query} maxLength={120} onChange={e => setQuery(e.target.value)} title={editorHelp.search.text} data-help-id={editorHelp.search.id} /></label>
          <HelpButton help={editorHelp.search} type="submit">Найти</HelpButton>
        </form>
        <div className="aa-inline">
          <label>Пространство<select value={space} onChange={e => setSpace(e.target.value)} title={editorHelp.space.text} data-help-id={editorHelp.space.id}>
            <option value="">все</option>{(spaces.data ?? []).map(s => <option key={s.space_id} value={s.space_id}>{s.title}</option>)}</select></label>
          <label>Статус<select value={status} onChange={e => setStatus(e.target.value as "" | ArticleStatus)} title={editorHelp.status.text} data-help-id={editorHelp.status.id}>
            <option value="">все</option><option value="DRAFT">черновики</option><option value="PUBLISHED">опубликованные</option><option value="ARCHIVED">архив</option></select></label>
        </div>
        {list.loading && <p role="status">Загрузка…</p>}{list.error && <p role="alert">{list.error}</p>}
        {list.data && (list.data.length === 0 ? <p className="aa-empty">Статей не найдено.</p> :
          <ul className="aa-list">{list.data.map(a => <li key={a.article_id} className={openId === a.article_id && !creating ? "aa-selected" : ""}>
            <span><b>{a.title}</b><br /><small><code>{a.article_id}</code> · {a.status} · v{a.version}</small></span>
            <HelpButton help={editorHelp.open} onClick={() => { setCreating(false); setOpenId(a.article_id); }}>Открыть</HelpButton></li>)}</ul>)}
        <HelpButton help={editorHelp.create} onClick={() => { setCreating(true); setOpenId(null); }}>Новая статья</HelpButton>
      </aside>
      <div className="ke-main">
        {!creating && !openId && <p className="aa-empty">Выберите статью или создайте новую.</p>}
        {openId && !creating && article.loading && <p role="status">Загрузка статьи…</p>}
        {openId && !creating && article.error && <p role="alert">{article.error}</p>}
        {(creating || current) && spaces.data && <ArticleEditor article={current} spaces={spaces.data} known={known.data ?? []} reload={reload}
          blocked={commands.blocked} busy={commands.busy} onSave={(payload, label) => submit("ARTICLE_SAVE", payload, label)}
          onPublish={reason => current && submit("PUBLISH", { article_id: current.article_id, expected_version: current.version, reason }, `Публикация ${current.article_id}`)}
          onArchive={reason => current && submit("ARCHIVE", { article_id: current.article_id, expected_version: current.version, reason }, `Архив ${current.article_id}`)} />}
      </div>
    </div>}
  </main>;
}
