import { useCallback, useRef, useState } from "react";
import { HelpButton } from "../help/HelpButton";
import { AssignmentsPanel } from "./AssignmentsPanel";
import { ExplainPanel } from "./ExplainPanel";
import { GroupsPanel } from "./GroupsPanel";
import { ObjectsPanel } from "./ObjectsPanel";
import { PendingCommandBanner } from "./PendingCommandBanner";
import { RolesPanel } from "./RolesPanel";
import { accessHelp } from "./help";
import { formatMoment, useApiRead } from "./useApiRead";
import { useMetadataCommands } from "./useMetadataCommands";
import type { AccessCatalog, AccessMe } from "./types";
import "./access-admin.css";

type Tab = "roles" | "groups" | "objects" | "assign" | "explain";
const TABS: { id: Tab; label: string; help: keyof typeof accessHelp }[] = [
  { id: "assign", label: "Назначения", help: "tabAssign" }, { id: "groups", label: "Группы объектов", help: "tabGroups" },
  { id: "objects", label: "Оргобъекты", help: "tabObjects" }, { id: "roles", label: "Роли", help: "tabRoles" }, { id: "explain", label: "Объяснение доступа", help: "tabExplain" },
];

/** Администрирование ролей, групп объектов и назначений поверх /api/access/* (C0056 блок 2).
 *  Сервер/Oracle — единственный источник решения о доступе; экран только показывает и отправляет команды. */
export function AccessAdminPage({ onBack }: { onBack?: () => void }) {
  const [tab, setTab] = useState<Tab>("assign");
  const [reload, setReload] = useState(0);
  const me = useApiRead<AccessMe>("/api/access/me", reload);
  const catalog = useApiRead<AccessCatalog>("/api/access/catalog", reload);
  const refresh = useCallback(() => setReload(n => n + 1), []);
  const commands = useMetadataCommands("access", refresh);
  const tabRefs = useRef<Record<Tab, HTMLButtonElement | null>>({ roles: null, groups: null, objects: null, assign: null, explain: null });
  const caps = me.data?.capabilities ?? {};
  const submit = (type: string, payload: Record<string, unknown>, label: string) => void commands.submit(type, payload, label, "ACCESS." + type);
  const onTabKey = (event: React.KeyboardEvent, index: number) => {
    const delta = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    if (!delta) return;
    const next = TABS[(index + delta + TABS.length) % TABS.length].id;
    setTab(next); tabRefs.current[next]?.focus();
  };
  return <main className="aa-page" aria-labelledby="aa-title">
    <header className="aa-header">
      {onBack && <HelpButton help={{ id: "access.back", text: "Вернуться к предыдущему экрану. Незавершённая команда сохраняется.", article: "access-admin" }} onClick={onBack}>← Назад</HelpButton>}
      <h2 id="aa-title">Права и назначения</h2>
      <HelpButton help={accessHelp.refresh} onClick={refresh}>Обновить</HelpButton>
      <span className="aa-meta">{me.data ? <>Вы: <b>{me.data.username}</b> · группа {me.data.legacy_group || "—"} · ваших назначений: действуют по сроку {me.data.assignments.filter(a => a.assignment_state === "ACTIVE").length} из {me.data.assignments.length} · ревизия {me.data.access_revision}</>
        : me.loading ? "Читаем профиль…" : me.error}{catalog.at && <> · данные {formatMoment(catalog.at.toISOString())}</>}</span>
    </header>
    <PendingCommandBanner pending={commands.pending} busy={commands.busy} message={commands.message}
      onCheck={() => void commands.check()} onRetry={() => void commands.retry()} onArchive={commands.archive} />
    <div role="tablist" aria-label="Разделы администрирования" className="aa-tabs">
      {TABS.map((t, i) => <button key={t.id} ref={el => { tabRefs.current[t.id] = el; }} role="tab" id={"aa-tab-" + t.id} aria-selected={tab === t.id} aria-controls={"aa-panel-" + t.id}
        tabIndex={tab === t.id ? 0 : -1} title={accessHelp[t.help].text} data-help-id={accessHelp[t.help].id} onClick={() => setTab(t.id)} onKeyDown={e => onTabKey(e, i)}>{t.label}</button>)}
    </div>
    <section role="tabpanel" id={"aa-panel-" + tab} aria-labelledby={"aa-tab-" + tab} className="aa-panel">
      {catalog.error && <p role="alert">Каталог прав не прочитан: {catalog.error}</p>}
      {catalog.loading && !catalog.data && <p role="status">Загрузка каталога…</p>}
      {catalog.data && tab === "roles" && <RolesPanel catalog={catalog.data} canManage={Boolean(caps.manage_roles)} blocked={commands.blocked} busy={commands.busy}
        onSave={(payload, label) => submit("ROLE_SAVE", payload, label)} />}
      {tab === "objects" && <ObjectsPanel reload={reload} canManage={Boolean(caps.manage_objects)} blocked={commands.blocked} busy={commands.busy} onSave={(payload, label) => submit("OBJECT_SAVE", payload, label)} />}
      {tab === "groups" && <GroupsPanel reload={reload} blocked={commands.blocked} busy={commands.busy} onSave={(payload, label) => submit("GROUP_SAVE", payload, label)} />}
      {catalog.data && tab === "assign" && <AssignmentsPanel catalog={catalog.data} accessRevision={me.data?.access_revision ?? null} reload={reload}
        blocked={commands.blocked} busy={commands.busy} onSubmit={submit} />}
      {tab === "explain" && <ExplainPanel rights={catalog.data?.rights ?? []} />}
    </section>
  </main>;
}
