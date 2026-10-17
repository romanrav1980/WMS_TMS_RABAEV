// Knowledge v1 (ACCESS_KNOWLEDGE_API_V1 + C-0063). Body — безопасный текст без HTML; ссылки — стабильные article_id.
export type ArticleStatus = "DRAFT" | "PUBLISHED" | "ARCHIVED";
export type KnowledgeSpace = { space_id: string; title: string; version: number };
export type ArticleSummary = { article_id: string; title: string; summary: string; status: ArticleStatus; version: number; space_id: string; updated_by?: string; updated_at?: string };
export type Article = ArticleSummary & { body: string; related: string[]; sources: string[]; required_permissions: string[] };
export type ArticleHistory = { version: number; status: ArticleStatus; actor: string; created_at: string; reason: string };
export type WikiSource = { source_id: string; article_id: string; title: string; summary: string; status: string; owner: string };
export type WikiPreview = WikiSource & { space_id: string; body: string; source_revision: string; sources: string[]; related: string[]; required_permissions: string[] };

export type ArticleDraft = { article_id: string; space_id: string; title: string; summary: string; body: string; related: string; sources: string; required_permissions: string; reason: string; expected_version: number };
export const ARTICLE_ID = /^[a-z][a-z0-9-]{1,79}$/;
export const splitList = (value: string) => value.split(/[\n,]/).map(x => x.trim()).filter(Boolean);
