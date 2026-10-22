import { journal } from "./intent";
import { useCommand } from "./useCommand";
import { Act, Tech } from "./ui";

type Body = { operation_id: string; trip_id: number; expected_version: number; source_hash: string };
type Receipt = { operation_id: string; trip_id: number; updated_legs: number; provider: string };
const pending = journal<Body>("road-refresh", "TC.ROAD.UI", b => Number.isSafeInteger(b.trip_id) && b.trip_id > 0
  && Number.isSafeInteger(b.expected_version) && b.expected_version >= 0 && /^[a-f0-9]{64}$/.test(b.source_hash), "дорожный расчёт");
const help = (id: string, text: string) => ({ id: "tradecase.route.road." + id, text, anchor: "route" });

export function RoadRefresh({ wh, user, trip, version, sourceHash, refreshing, onSaved }: {
  wh: string; user: string; trip: number; version: number; sourceHash: string; refreshing: boolean; onSaved: () => void;
}) {
  const cmd = useCommand<Body, Receipt>(pending, "/api/transport/preflight/road-refreshes", user, wh, {
    ROAD_REFRESH_SOURCE_CHANGED: "Рейс, дорожные данные или координаты изменились. Перечитайте маршрут перед новым расчётом.",
    ROAD_REFRESH_ROUTE_REQUIRED: "Задайте адрес склада и порядок точек доставки.",
    ROAD_ADDRESS_COORDINATES_REQUIRED: "Проверьте координаты адресов склада и магазинов.",
    ROAD_PROVIDER_UNAVAILABLE: "Дорожный сервис недоступен. Исходная команда сохранена для повтора.",
    ROAD_REFRESH_OPERATION_CONFLICT: "Этот номер операции уже связан с другим запросом.",
  }, (r, b) => r.operation_id !== b.operation_id || r.trip_id !== b.trip_id
    || !Number.isSafeInteger(r.updated_legs) || r.updated_legs <= 0 || !["osrm", "valhalla"].includes(r.provider)
    ? null : `Обновлено дорожных плеч: ${r.updated_legs}. Проверьте окна доставки и заново утвердите время рейса.`);
  return <div className="tc-panel">
    <h5>Дорожное время по точкам рейса</h5>
    <p className="tc-note">Расчёт обновляет только плечи этого рейса через дорожный сервис. Он не утверждает рейс и не меняет товар.</p>
    {cmd.stored.kind === "damaged" && <p role="alert" className="tc-err">Сохранённая команда повреждена; новый расчёт заблокирован.<Tech value={cmd.stored.raw} /></p>}
    {cmd.stored.kind === "ok" && <div className="tc-msg warn"><p>Расчёт рейса № {cmd.stored.intent.body.trip_id} не подтверждён.</p>
      <Act help={help("retry", "Повторить сохранённый дорожный расчёт с тем же номером операции и исходными полями.")}
        disabled={cmd.busy || cmd.stored.intent.body.trip_id !== trip}
        onClick={() => { if (cmd.stored.kind === "ok") void cmd.send(cmd.stored.intent, onSaved); }}>Повторить дорожный расчёт</Act></div>}
    {cmd.msg && <p role="status" className={"tc-msg " + cmd.msg.tone}>{cmd.msg.text}{cmd.msg.tech !== undefined && <Tech value={cmd.msg.tech} />}</p>}
    <Act help={help("refresh", "Получить время движения и расстояния между соседними точками текущего рейса, включая выезд и возврат на склад. Требуются координаты адресов и подключённый дорожный сервис.")}
      disabled={cmd.busy || refreshing || cmd.stored.kind !== "none" || !Number.isSafeInteger(version) || !/^[a-f0-9]{64}$/.test(sourceHash)}
      onClick={() => cmd.start({ trip_id: trip, expected_version: version, source_hash: sourceHash }, onSaved)}>Обновить дорожные плечи</Act>
  </div>;
}
