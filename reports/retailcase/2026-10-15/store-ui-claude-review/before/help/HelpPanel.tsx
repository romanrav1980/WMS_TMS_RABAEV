import { findHelpArticle, type HelpArticle } from "./helpArticles";

export function HelpPanel({ source, article, requestedId, onClose, onOpenRelated }: {
 source: string;
 article: HelpArticle | undefined;
 requestedId: string;
 onClose: () => void;
 onOpenRelated: (articleId: string) => void;
}) {
 return <div className="store-app-help-overlay" role="presentation" onClick={onClose}>
  <section className="store-app-help-panel" role="dialog" aria-label="Справка" onClick={(event) => event.stopPropagation()}>
   <header>
    <h2>{article ? article.title : "Справка"}</h2>
    <button type="button" title="Закрыть справку и вернуться к работе" aria-label="Закрыть справку" onClick={onClose}>×</button>
   </header>
   <p role="status">{source}</p>
   {article ? <>
    <p className="store-app-help-summary">{article.summary}</p>
    {article.body.split("\n\n").map((paragraph, index) => <p key={index}>{paragraph}</p>)}
    {article.related.length > 0 && <nav aria-label="Связанные статьи">
     <p>См. также:</p>
     <ul>{article.related.map((relatedId) => {
      const related = findHelpArticle(relatedId);
      return <li key={relatedId}>
       <button type="button" title="Открыть связанную статью в справке приложения" onClick={() => onOpenRelated(relatedId)}>{related ? related.title : relatedId}</button>
      </li>;
     })}</ul>
    </nav>}
   </> : <p>Содержимое статьи «{requestedId}» сейчас недоступно.</p>}
  </section>
 </div>;
}
