import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { apiFetch } from "../../../api";
import { AccessAdminPage } from "../access-admin";
import { KnowledgeEditorPage } from "../knowledge-editor";
import { WorkplaceHome } from "../workspaces";
import { HelpButton } from "../help/HelpButton";
import { openHelpArticle } from "../help/catalog";
import "./entry.css";

type Navigation = { username: string; access_admin: boolean; knowledge_editor: boolean; knowledge_publish: boolean; manage_roles: boolean; manage_groups: boolean; manage_assignments: boolean; access_revision: number };
const currentPage = () => new URLSearchParams(location.search).get("page") || "twin";
const platformPage = (page: string) => page === "access-admin" || page === "knowledge-editor" || page === "workspace";

/** Platform routes live outside the legacy App function; switching preserves mounted legacy work. */
export function PlatformEntry({legacy}: {legacy: ReactNode}) {
  const [page,setPage] = useState(currentPage);
  const [legacyMounted,setLegacyMounted] = useState(() => !platformPage(currentPage()));
  const [navigation,setNavigation] = useState<Navigation | null>(null);
  const [error,setError] = useState("");
  const [refresh,setRefresh] = useState(0);
  const [sectionsOpen,setSectionsOpen] = useState(false);
  const sectionsToggle = useRef<HTMLButtonElement>(null);
  const lastLegacy = useRef(platformPage(page) ? "twin" : page);
  useEffect(() => {
    const onPop = () => { const next=currentPage();setPage(next);if(!platformPage(next)){setLegacyMounted(true);lastLegacy.current=next;} };
    window.addEventListener("popstate",onPop);return()=>window.removeEventListener("popstate",onPop);
  },[]);
  useEffect(() => {
    const controller = new AbortController();setError("");
    apiFetch<Navigation>("/api/access/navigation",{signal:controller.signal}).then(data=>{if(!controller.signal.aborted)setNavigation(data);})
      .catch(reason=>{if(!controller.signal.aborted){setNavigation(null);setError(String(reason));}});
    return()=>controller.abort();
  },[refresh,page]);
  const navigate = (next: string) => {
    if(sectionsOpen && matchMedia("(max-width:600px)").matches)sectionsToggle.current?.focus();
    if(!platformPage(page))lastLegacy.current=page;
    if(!platformPage(next))setLegacyMounted(true);
    const url=new URL(location.href);url.searchParams.set("page",next);history.pushState(history.state,"",url);setPage(next);setSectionsOpen(false);
  };
  return <div className="platform-root" data-platform-view={platformPage(page) ? "platform" : "legacy"}>
    <button ref={sectionsToggle} className="platform-menu-toggle" type="button" aria-expanded={sectionsOpen} aria-controls="platform-sections"
      title="Открыть или свернуть разделы системы, сохранив текущую работу." data-help-id="shell.sections"
      onClick={()=>setSectionsOpen(value=>!value)}>Разделы системы {sectionsOpen ? "▴" : "▾"}</button>
    <nav id="platform-sections" className={"platform-navigation"+(sectionsOpen?" is-open":"")} aria-label="Разделы retailcase">
      <HelpButton help={{id:"shell.work",text:"Вернуться к рабочему экрану. Состояние открытого экрана сохраняется.",article:"using-help"}} onClick={()=>navigate(lastLegacy.current)}>Рабочий экран</HelpButton>
      {navigation?.access_admin && <HelpButton help={{id:"shell.access",text:"Открыть роли, группы объектов и назначения. Полномочия проверяет сервер.",article:"access-admin"}} onClick={()=>navigate("access-admin")}>Права и назначения</HelpButton>}
      <HelpButton help={{id:"shell.workspace",text:"Открыть рабочее место (директор РЦ, диспетчер, комплектовщик, водитель). Данные и права проверяет сервер.",article:"workspaces"}} onClick={()=>navigate("workspace")}>Моё рабочее место</HelpButton>
      {navigation?.knowledge_editor && <HelpButton help={{id:"shell.knowledge_editor",text:"Открыть редактор: черновики, публикация, импорт выбранных знаний wiki. Сервер проверяет полномочия.",article:"knowledge-editor"}} onClick={()=>navigate("knowledge-editor")}>Редактор знаний</HelpButton>}
      <HelpButton help={{id:"shell.knowledge",text:"Открыть поиск по опубликованным инструкциям и связанные знания, сохранив текущую работу.",article:"using-help"}} onClick={()=>openHelpArticle("using-help")}>База знаний</HelpButton>
      <HelpButton help={{id:"shell.refresh_access",text:"Перечитать доступные разделы после назначения или отзыва роли.",article:"access-model"}} onClick={()=>setRefresh(value=>value+1)}>Обновить доступ</HelpButton>
      {navigation && <span className="platform-nav-user">{navigation.username} · доступ v{navigation.access_revision}</span>}
    </nav>
    {error && <p role="alert" className="platform-message">Разделы не прочитаны: {error}</p>}
    <div className="platform-legacy" hidden={platformPage(page)}>{legacyMounted && legacy}</div>
    {page==="access-admin" && (navigation?.access_admin ? <AccessAdminPage onBack={()=>navigate(lastLegacy.current)}/>
      : <p role="status" className="platform-message">{navigation ? "Нет права просмотра администрирования доступа." : "Проверяем доступ к разделу…"}</p>)}
    {page==="workspace" && <WorkplaceHome onBack={()=>navigate(lastLegacy.current)}/>}
    {page==="knowledge-editor" && (navigation?.knowledge_editor ? <KnowledgeEditorPage onBack={()=>navigate(lastLegacy.current)}/>
      : <p role="status" className="platform-message">{navigation ? "Нет права редактирования базы знаний." : "Проверяем доступ к разделу…"}</p>)}
  </div>;
}
