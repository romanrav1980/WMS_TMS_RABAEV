export type DriverRestResult = {
  basis: string; status: string; drive_min: string;
  continuous_limit_min: string; minimum_break_min: string; trip_drive_limit_min: string;
  violations: {code: string; operation_id?: number; excess_min?: string; duration_min?: string}[];
  unknown_intervals: {code: string; operation_id: number}[];
};
const labels: Record<string, string> = {
  DRIVER_CONTINUOUS_DRIVE_LIMIT: "Превышено непрерывное вождение",
  DRIVER_TRIP_DRIVE_LIMIT: "Превышен лимит вождения одного рейса",
  DRIVER_BREAK_TOO_SHORT: "Недостаточный перерыв",
  DRIVER_ROUTE_DURATION_UNKNOWN: "Не задано время движения",
  DRIVER_INTERVAL_MISSING: "Не задан интервал операции",
  DRIVER_INTERVAL_INVALID: "Некорректный интервал операции",
  DRIVER_CHAIN_GAP_OR_OVERLAP: "Разрыв или пересечение операций",
  DRIVER_CHANGE_BINDING_NOT_PROVEN: "Не подтверждена смена водителя",
};
export function TransportDriverRest({value}: {value: DriverRestResult}) {
  return <section aria-label="Перерывы водителя">
    <strong>Вождение и перерывы в этом рейсе</strong>
    <p>Вождение: {value.drive_min} мин. Параметры плана: непрерывно до {value.continuous_limit_min} мин,
      перерыв от {value.minimum_break_min} мин, в рейсе до {value.trip_drive_limit_min} мин.</p>
    {[...value.violations, ...value.unknown_intervals].length > 0
      ? <ul>{[...value.violations, ...value.unknown_intervals].map((item, i) =>
        <li key={i}>{labels[item.code] || item.code}{item.operation_id ? ` (#${item.operation_id})` : ""}</li>)}</ul>
      : <p>Нарушений параметров в записанной цепочке этого рейса не найдено.</p>}
    <p>Предыдущая работа, другие рейсы за сутки и применимые правовые нормы ещё не подтверждены.
      Разгрузка и свободные промежутки не засчитываются как отдых.</p>
  </section>;
}
