import { createContext, useContext, useMemo, useState, useEffect, type ReactNode } from "react";
import { findHelpArticle, type HelpArticle } from "./helpArticles";
import { HelpPanel } from "./HelpPanel";
import { storeAppRequest, isAuthError } from "../api";
import type { StoreCredentials } from "../contracts";

interface HelpContextValue {
 openHelp: (articleId: string) => void;
}

const HelpContext = createContext<HelpContextValue | null>(null);

export function HelpProvider({ children, credentials }: { children: ReactNode; credentials: StoreCredentials | null }) {
 const [openArticleId, setOpenArticleId] = useState<string | null>(null);
 const value = useMemo<HelpContextValue>(() => ({ openHelp: setOpenArticleId }), []);
 const [published, setPublished] = useState<HelpArticle | undefined>();
 const [resolvedFor, setResolvedFor] = useState("");
 const [blocked, setBlocked] = useState(false);
 const helpKey = (credentials?.username ?? "") + ":" + (openArticleId ?? "");
 const [source, setSource] = useState("Встроенная справка этой версии приложения");
 useEffect(() => {
  let active = true;
  setPublished(undefined);
  setBlocked(false);
  setResolvedFor(credentials ? "" : helpKey);
  setSource(credentials ? "Проверяется опубликованная справка…" : "Встроенная справка этой версии приложения");
  if (openArticleId && credentials) {
   void storeAppRequest<Record<string, unknown>>("/api/help/articles/" + encodeURIComponent(openArticleId), credentials)
    .then(data => {
     if (!active) return;
     if (data.article_id !== openArticleId || typeof data.title !== "string" || typeof data.body !== "string" || !Array.isArray(data.related)) throw new Error("Некорректная статья");
     setPublished({ article_id: openArticleId, title: data.title, body: data.body,
      summary: typeof data.summary === "string" ? data.summary : "",
      related: data.related.map(row => typeof row === "string" ? row : row.article_id).filter(id => typeof id === "string") });
     setSource("Опубликованная база знаний · редакция " + String(data.revision ?? data.version));
     setResolvedFor(helpKey);
    }).catch(error => {
     if (!active) return;
     const denied = isAuthError(error) || (error instanceof Error && "status" in error && error.status === 404);
     setBlocked(denied); setResolvedFor(helpKey);
     setSource(denied ? "Статья недоступна для текущей учётной записи. Войдите заново или обратитесь к администратору."
      : "Опубликованная справка недоступна. Встроенная копия этой версии приложения; актуальность не подтверждена.");
    });
  }
  return () => { active = false; };
 }, [openArticleId, credentials, helpKey]);
 const article = blocked || resolvedFor !== helpKey ? undefined : published ?? (openArticleId ? findHelpArticle(openArticleId) : undefined);
 return <HelpContext.Provider value={value}>
  {children}
  {openArticleId && <HelpPanel source={source} article={article} requestedId={openArticleId} onClose={() => setOpenArticleId(null)} onOpenRelated={setOpenArticleId} />}
 </HelpContext.Provider>;
}

export function useHelp(): HelpContextValue {
 const context = useContext(HelpContext);
 if (!context) throw new Error("useHelp используется без HelpProvider");
 return context;
}
