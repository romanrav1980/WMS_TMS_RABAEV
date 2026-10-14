import { useMemo, useState } from "react";
import type { Selection } from "../contracts/twin";
import { SPEEDS, useTwin } from "../store/twinStore";
import { clock } from "../ui/format";
import { CONNECTION_LABEL, snapshotAge } from "../ui/opsFormat";

type Hit = { sel: Selection; title: string; note: string };

function useSearch(query: string): Hit[] {
  const world = useTwin((s) => s.world);
  const hudVersion = useTwin((s) => s.hudVersion);
  return useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q.length < 2) return [];
    const hits: Hit[] = [];
    for (const t of world.trips) {
      if (`${t.id} ${t.plate} ${t.carrier} ${t.route}`.toLowerCase().includes(q)) hits.push({ sel: { kind: "trip", id: t.id }, title: t.id, note: `${t.plate} · ${t.route}` });
    }
    for (const st of Object.values(world.sts)) {
      if (`${st.id} ${st.store}`.toLowerCase().includes(q)) hits.push({ sel: { kind: "st", id: st.id }, title: st.id, note: st.store });
    }
    for (const r of world.resources) {
      if (`${r.id} ${r.name}`.toLowerCase().includes(q)) hits.push({ sel: { kind: "resource", id: r.id }, title: r.id, note: r.name });
    }
    for (const g of world.gates) if (g.id.toLowerCase().includes(q)) hits.push({ sel: { kind: "gate", id: g.id }, title: g.id, note: "ворота" });
    if (/^a\d/.test(q)) {
      for (const c of world.cells) {
        if (c.id.toLowerCase().startsWith(q)) hits.push({ sel: { kind: "cell", id: c.id }, title: c.id, note: c.sku ?? "пусто" });
        if (hits.length > 30) break;
      }
    }
    return hits.slice(0, 10);
  }, [query, world, hudVersion]);
}

export function TopBar() {
  const world = useTwin((s) => s.world);
  useTwin((s) => s.hudVersion);
  const source = useTwin((s) => s.source);
  const speed = useTwin((s) => s.speed);
  const paused = useTwin((s) => s.paused);
  const setSpeed = useTwin((s) => s.setSpeed);
  const togglePause = useTwin((s) => s.togglePause);
  const select = useTwin((s) => s.select);
  const [query, setQuery] = useState("");
  const hits = useSearch(query);
  const status = source.status();
  return (
    <header className="topbar">
      <div className="brand">
        <span className="brand-cube">◆</span>
        <div>
          <b>Цифровой двойник</b>
          <small>Склад + транспорт · ТМС</small>
        </div>
      </div>
      <div className="search">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Поиск: рейс, госномер, СТ, магазин, ячейка A01-S003-L1, P01, G03"
          onKeyDown={(e) => {
            if (e.key === "Enter" && hits[0]) {
              select(hits[0].sel);
              setQuery("");
            }
          }}
        />
        {hits.length > 0 && (
          <div className="search-hits">
            {hits.map((h) => (
              <button type="button" key={`${h.sel.kind}:${h.sel.id}`} onClick={() => { select(h.sel); setQuery(""); }}>
                <b>{h.title}</b>
                <span>{h.note}</span>
              </button>
            ))}
          </div>
        )}
      </div>
      <button type="button" className="site-chip" onClick={() => select({ kind: "site", id: world.layout.siteId })}>
        <span className="site-code">{world.layout.siteId}</span>
        <span>
          <b>{world.layout.siteName}</b>
          <small>Ворота {world.gates.filter((g) => g.occupiedBy).length}/{world.gates.length} · СТ в работе {Object.values(world.sts).filter((s) => ["created", "picking", "qc", "staged", "loading"].includes(s.stage)).length}</small>
        </span>
      </button>
      <div className="speed">
        <button type="button" className={paused ? "active" : ""} onClick={togglePause} title="Пауза">{paused ? "▶" : "❚❚"}</button>
        {SPEEDS.map((s) => (
          <button type="button" key={s} className={!paused && speed === s ? "active" : ""} onClick={() => setSpeed(s)}>×{s}</button>
        ))}
      </div>
      <div className={`source-badge ${source.mode} conn-${world.connection.state.toLowerCase()} ${status.ok ? "ok" : ""}`} title={status.message}>
        {CONNECTION_LABEL[world.connection.state]}
        {source.mode === "live" && world.connection.snapshotAt ? ` · ${snapshotAge(world.connection.snapshotAt)}` : ""}
      </div>
      <div className="clock">
        <span className="live-dot" />
        {clock(world.simTime, true)}
      </div>
    </header>
  );
}
