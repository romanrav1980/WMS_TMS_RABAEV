import { useState } from "react";
import { HelpButton } from "../help/HelpButton";
import { HelpHint } from "../help/HelpHint";
import { useApiRead } from "../access-admin";
import { editorHelp } from "./help";
import type { ArticleSummary, WikiPreview, WikiSource } from "./types";

/** «Из wiki»: только разрешённые источники (C-0063). Импорт создаёт ЧЕРНОВИК из редакции, показанной в предпросмотре. */
export function WikiImportPanel({ known, reload, blocked, busy, onImport }: {
  known: ArticleSummary[]; reload: number; blocked: boolean; busy: boolean;
  onImport: (payload: Record<string, unknown>, label: string) => void;
}) {
  const sources = useApiRead<WikiSource[]>("/api/knowledge/wiki-sources", reload);
  const [selected, setSelected] = useState<string | null>(null);
  const [reason, setReason] = useState("");
  const preview = useApiRead<WikiPreview>(selected ? `/api/knowledge/wiki-sources/${encodeURIComponent(selected)}/preview` : null, reload);
  const target = preview.data ? known.find(k => k.article_id === preview.data?.article_id) : undefined;
  const lock = blocked ? "есть незавершённая команда" : busy ? "идёт запрос" : !preview.data ? "сначала откройте предпросмотр" : !reason.trim() ? "укажите причину" : "";
  return <section className="aa-split" aria-label="Импорт из wiki">
    <div>
      <h3>Разрешённые источники wiki <HelpHint help={editorHelp.wikiTab} /></h3>
      {sources.loading && <p role="status">Загрузка…</p>}{sources.error && <p role="alert">{sources.error}</p>}
      {sources.data && (sources.data.length === 0 ? <p className="aa-empty">Источников нет.</p> :
        <ul className="aa-list">{sources.data.map(s => <li key={s.source_id} className={selected === s.source_id ? "aa-selected" : ""}>
          <span><b>{s.title}</b> → <code>{s.article_id}</code><br /><small>{s.summary} · {s.status} · {s.owner}</small></span>
          <HelpButton help={editorHelp.wikiPreview} onClick={() => setSelected(s.source_id)}>Предпросмотр</HelpButton></li>)}</ul>)}
    </div>
    <div className="aa-form">
      {!selected && <p className="aa-empty">Выберите источник для предпросмотра.</p>}
      {preview.loading && <p role="status">Читаем источник…</p>}{preview.error && <p role="alert">{preview.error}</p>}
      {preview.data && <>
        <h3>{preview.data.title}</h3>
        <p>Станет черновиком статьи <code>{preview.data.article_id}</code>{target ? ` (сейчас ${target.status}, v${target.version})` : " (новая статья)"}.</p>
        <p className="aa-note">Редакция источника: <code>{preview.data.source_revision.slice(0, 12)}…</code></p>
        <div className="ke-preview">{preview.data.body.replace(/\r\n/g, "\n").split("\n\n").map((p, i) => <p key={i}>{p}</p>)}</div>
        <label>Причина импорта<input value={reason} maxLength={500} onChange={e => setReason(e.target.value)} title="Сохраняется в истории статьи." data-help-id="knowledge.editor.wiki.reason" /></label>
        <div className="aa-actions">
          <HelpButton help={editorHelp.wikiImport} unavailable={lock} onClick={() => preview.data && onImport({ source_id: preview.data.source_id, source_revision: preview.data.source_revision,
            expected_version: target?.version ?? 0, reason: reason.trim() }, `Импорт ${preview.data.source_id} → ${preview.data.article_id}`)}>Создать черновик из wiki</HelpButton>
          <HelpHint help={editorHelp.wikiImport} />
        </div>
      </>}
    </div>
  </section>;
}
