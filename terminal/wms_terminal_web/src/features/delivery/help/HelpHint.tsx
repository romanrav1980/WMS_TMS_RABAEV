import { useHelp } from "./HelpContext";

export function HelpHint({ helpId, tip, article }: { helpId: string; tip: string; article: string }) {
 const { openHelp } = useHelp();
 return <button
  type="button"
  className="store-app-help-hint"
  data-help-id={helpId}
  title={tip}
  aria-label={"Справка: " + tip}
  onClick={() => openHelp(article)}
 >?</button>;
}
