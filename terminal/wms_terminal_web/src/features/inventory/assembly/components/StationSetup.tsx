import { rawApiGet } from "../api";
import { useEffect, useRef, useState } from "react";
import { ScanField, NativeHelp } from "../../../platform";
import { ASSEMBLY_ARTICLE_ID, help } from "../help";
import type { AssemblyContext, AssemblyCredentials, OpenSessionBody } from "../contracts";
import type { WarehouseWeighState } from "../useWarehouseWeigh";
import { terminalWeigh } from "../physicalContracts";
export function StationSetup({ context, credentials, refreshContext, weigh, busy, onOpenSession }: {
  context: AssemblyContext; credentials: AssemblyCredentials; refreshContext: () => void; weigh: WarehouseWeighState; busy: boolean; onOpenSession: (body: OpenSessionBody) => void;
}) {
  const [deviceId, setDeviceId] = useState<string | null>(context.stations.length === 1 ? context.stations[0].device_id : null);
  const [tareKey, setTareKey] = useState<string | null>(null), [container, setContainer] = useState("");
  const [checking, setChecking] = useState(false), [checkError, setCheckError] = useState("");
  const live = useRef(true); useEffect(() => { live.current = true; return () => { live.current = false; }; }, []);
  const station = context.stations.find(s => s.device_id === deviceId) ?? null;
  useEffect(() => { if (weigh.entry?.body.purpose === "EMPTY_TARE") { setDeviceId(weigh.entry.body.device_id); setContainer(weigh.entry.body.scan_container); } }, [weigh.entry]);
  const scanned = !!container && container === context.scan_container;
  const canRequest = !weigh.entry || !!weigh.state && terminalWeigh(weigh.state);
  const requestTare = () => { if (!station || !scanned) return;
    weigh.start({ request_id: `ASM.EMPTY:${crypto.randomUUID()}`, device_id: station.device_id, purpose: "EMPTY_TARE", case_task_id: context.task_id,
      expected_content_version: context.content_version, scan_container: container, zero_progress_required: true,
      ...(context.resource_session_id != null ? { resource_session_id: context.resource_session_id } : {}) });
  };
  const open = async () => { if (!station || !tareKey || !scanned || checking) return;
    setChecking(true); setCheckError("");
    try {
      const fresh = await rawApiGet<AssemblyContext>(`/api/inventory/assembly-scale/context?task_id=${context.task_id}`, credentials);
      if (!live.current) return;
      if (fresh.task_id !== context.task_id || fresh.content_version !== context.content_version || fresh.scan_container !== container
        || !fresh.stations?.find(s => s.device_id === station.device_id)?.tare_captures.some(t => t.capture_key === tareKey)) throw new Error("Замер тары или задание изменились. Обновите список и выберите текущий замер.");
      onOpenSession({ session_id: crypto.randomUUID(), task_id: context.task_id, device_id: station.device_id, expected_content_version: context.content_version, tare_capture_key: tareKey, scan_container: container });
    } catch (err) { if (live.current) { setCheckError(err instanceof Error ? err.message : String(err)); refreshContext(); } }
    finally { if (live.current) setChecking(false); }
  };
  if (!["IN_PROGRESS","PARTIAL","WAIT_REPLENISHMENT"].includes(context.task_state)) return <InactiveSetup context={context} credentials={credentials} refreshContext={refreshContext} />;
  return <div className="asm-setup">
    <header className="asm-header"><div><h2>Пост и тара</h2><span data-testid="assembly-setup-identity">Задание {context.task_id} · {credentials.username}</span></div><NativeHelp articleId={ASSEMBLY_ARTICLE_ID} credentials={credentials} /></header>
    <ScanField label="Идентификатор паллеты / сборочной тары" value={container} onChange={setContainer} disabled={busy || checking} />
    {context.scan_container && container && !scanned && <p className="asm-err">Идентификатор не совпадает с тарой этого задания. Проверьте скан.</p>}
    {context.stations.length === 0 && <p className="asm-note">Для задания нет настроенных постов весов.</p>}
    <div className="asm-station-list" role="radiogroup" aria-label="Пост весов">
      {context.stations.map(s => <button key={s.device_id} type="button" role="radio" aria-checked={s.device_id === deviceId}
        disabled={busy || checking || (!!weigh.entry && !canRequest)} className={"asm-pick" + (s.device_id === deviceId ? " selected" : "")}
        onClick={() => { setDeviceId(s.device_id); setTareKey(null); }} title={help.station.title} data-help-id={help.station.id}>
        <b>{s.post_cell}</b><small>{s.confirmation_mode === "AUTO" ? "Авто" : "По кнопке"} · {s.device_id}</small>
        {s.device_mode === "TEST" && <span className="asm-chip asm-test">ТЕСТ — физические весы не подтверждены</span>}
      </button>)}
    </div>
    <button type="button" disabled={busy || checking || !station || !scanned || !canRequest || weigh.busy || weigh.denied || (!!weigh.error && !weigh.entry)} onClick={requestTare}
      title="Сохранить запрос веса пустой тары. Сначала освободите платформу; ставить тару можно только после подтверждённого нуля." data-help-id="assembly.empty-request">Взвесить пустую тару</button>
    <button type="button" onClick={refreshContext} title="Перечитать разрешённые посты и сохранённые замеры. Новое взвешивание не запускается." data-help-id="assembly.setup-refresh">Обновить посты и замеры</button>
    {station && <div className="asm-tare-list" role="radiogroup" aria-label="Фактическая тара">
      {station.tare_captures.length === 0 ? <p className="asm-note">Нет замера пустой тары. Отсканируйте её идентификатор и запросите взвешивание.</p> : station.tare_captures.map(t => <button key={t.capture_key} type="button" role="radio" aria-checked={t.capture_key === tareKey}
        className={"asm-pick" + (t.capture_key === tareKey ? " selected" : "")} onClick={() => setTareKey(t.capture_key)} title={help.tare.title} data-help-id={help.tare.id}>
        <b>{t.weight_kg} кг</b><small>Фактическая тара</small></button>)}
    </div>}
    {checkError && <p className="asm-err" role="alert">{checkError}</p>}
    <button type="button" disabled={busy || checking || weigh.blocked || !station || !tareKey || !scanned} onClick={() => void open()} title={help.openSession.title} data-help-id={help.openSession.id}>{busy ? "Открываем…" : "Открыть сессию"}</button>
  </div>;
}


function InactiveSetup({ context, credentials, refreshContext }: { context: AssemblyContext; credentials: AssemblyCredentials; refreshContext: () => void }) {
  const labels: Record<string, string> = { CANCELLED: "Отменено", SHIPPED: "Отгружено", WAIT_CONTROL: "На контроле", CONTROLLED: "Контроль завершён", READY_TO_SHIP: "Готово к отгрузке" };
  return <section className="asm-setup"><header className="asm-header"><div><b>Задание {context.task_id}</b><span>{credentials.username} · {labels[context.task_state] ?? context.task_state}</span></div><NativeHelp articleId={ASSEMBLY_ARTICLE_ID} credentials={credentials} /></header>
    <p className="asm-note">В этом состоянии новая сессия сборки и запрос пустой тары недоступны. Сохранённые запросы можно только сверить.</p>
    <button type="button" onClick={refreshContext} title="Прочитать текущее состояние задания без создания сессии или запроса к весам." data-help-id="assembly.inactive-refresh">Обновить состояние</button></section>;
}



