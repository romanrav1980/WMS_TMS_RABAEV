export type DriverDayResult = {
  time_zone: string; driver_id: number | null; status: string;
  days: {local_day: string; drive_min: string; planning_limit_min: string; limit_exceeded: boolean;
    unresolved_trip_ids: number[]; unknown_drive_operation_ids: number[];
    continuity?: {continuous_limit_min:string;minimum_break_min:string;violations:{code:string;operation_id?:number;continuous_min?:string}[];unknown_intervals:{code:string;operation_id?:number}[]};
    sources: {trip_id: number; drive_min: string; time_zone: string}[]}[];
};
export function TransportDriverDay({value}: {value: DriverDayResult}) {
  return <section aria-label="Вождение за день">
    <strong>Записанные планы водителя за день ({value.time_zone})</strong>
    {!value.driver_id && <p>Назначьте водителя.</p>}
    {value.days.map(day => <div key={day.local_day}>
      <p>{day.local_day}: {day.drive_min} мин из {day.planning_limit_min} мин по параметрам проекта.
        {day.limit_exceeded && <strong> Превышен плановый лимит.</strong>}</p>
      <ul>{day.sources.map(source => <li key={source.trip_id}>Рейс #{source.trip_id}:
        {" "}{source.drive_min} мин ({source.time_zone})</li>)}</ul>
      {day.unresolved_trip_ids.length > 0 && <p>Не подтверждено время рейсов:
        {" "}{day.unresolved_trip_ids.map(id => `#${id}`).join(", ")}</p>}
      {day.continuity && <p>Непрерывное вождение между рейсами: лимит {day.continuity.continuous_limit_min} мин; перерыв не менее {day.continuity.minimum_break_min} мин.
        {day.continuity.violations.length > 0 && <strong> Есть нарушение непрерывного вождения или перерыва.</strong>}
        {day.continuity.unknown_intervals.length > 0 && <span> Цепочка работы содержит пропуски или пересечения; уточните план.</span>}</p>}
      {day.unknown_drive_operation_ids.length > 0 && <p>Есть операции движения без достоверной длительности.</p>}
    </div>)}
    <p>Сумма относится к утверждённым записанным планам. Работа вне ВМС, предыдущая смена и правовые нормы
      ещё не подтверждены; допуск водителя этим расчётом не выдаётся.</p>
  </section>;
}
