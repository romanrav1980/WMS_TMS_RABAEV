/** Bundled public instructions only. Native articles and granted access are never cached. */
import publication from "./offline-public.json";

export type KnowledgeSummary = { article_id: string; title: string; summary: string };
export type KnowledgeArticle = KnowledgeSummary & {
  body: string; revision: string; sources: string[];
  related: { article_id: string; title: string }[];
};

export function readOfflinePublicKnowledge(query: string, selected: string): KnowledgeSummary[] | KnowledgeArticle | null {
  const terms = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  if (terms.length) return publication.filter(row => {
    const text = `${row.title} ${row.summary} ${row.body}`.toLocaleLowerCase();
    return terms.every(term => text.includes(term));
  }).slice(0, 20).map(({ article_id, title, summary }) => ({ article_id, title, summary }));
  const row = publication.find(item => item.article_id === selected);
  if (!row) return null;
  return { ...row, related: row.related.flatMap(id => {
    const target = publication.find(item => item.article_id === id);
    return target ? [{ article_id: target.article_id, title: target.title }] : [];
  }) };
}
