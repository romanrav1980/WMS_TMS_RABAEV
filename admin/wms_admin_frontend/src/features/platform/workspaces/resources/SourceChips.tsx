import { ganttHelp } from "./ganttHelp";
import { fmtTime, zoneKnown } from "./timelineModel";
import type { ResourceTimeline } from "./timelineTypes";

const STATUS = { OK: "", ERROR: "ошибка", NO_ACCESS: "нет права", NOT_MAPPED: "источник не подключён" } as const;

/** Источники таймлайна: время чтения, лимит, ошибка. Ошибка источника = неизвестность, не пустота. */
export function SourceChips({ timeline }: { timeline: ResourceTimeline }) {
  const tz = zoneKnown(timeline) ? timeline.warehouse.time_zone : null;
  return <div className="ops-sources" aria-label="Источники Ганта">
    <span className="ops-chip plan" title={ganttHelp.source.text} data-help-id={ganttHelp.source.id}>прочитано {fmtTime(tz, timeline.read_at)}</span>
    {timeline.sources.map(s => <span key={s.source} className={"ops-chip " + (s.status === "OK" ? (s.truncated ? "other" : "closed") : "bad")}
      title={`${ganttHelp.source.text}${s.message ? "\n" + s.message : ""}`} data-help-id={ganttHelp.source.id + "." + s.source}>
      {s.title ?? s.source}{s.status !== "OK" ? " · " + STATUS[s.status] : ""}{s.row_count != null ? ` · ${s.row_count}${s.truncated ? "+" : ""}` : ""}{s.truncated && s.limit ? ` (выборка до ${s.limit})` : ""}
    </span>)}
  </div>;
}
