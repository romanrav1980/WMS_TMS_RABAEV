// C-0033: форма ответа GET /api/transport/preflight/trips/{id}/delivery-windows (native RRL_TT_ROUTE_SCHEDULE)
// и подписи. Только отображение серверного расчёта; статус и причины определяет сервер.
export type ScheduleStop={address:string;st_numbers:string[];window_from:string|null;window_to:string|null;arrival_at:string|null;
  service_start_at?:string|null;service_finish_at:string|null;wait_min:string|null;late_min:string|null;unload_norm_min?:string|null;
  window_strict?:number|null;issues:string[];window_source?:string|null;
  // Настроенная неделя магазина из того же snapshot (C-0038). Не разрешение работать вне window_from/to; в старом ответе полей нет.
  profile_version?:number|null;store_window_mode?:string|null;store_time_zone?:string|null;
  configured_weekly_windows?:{weekday:number;from_minute:number;to_minute:number}[]};
export type ScheduleSegment={code:string;start_at:string;finish_at:string;duration_min?:string;address?:string};
export type ScheduleReport={status:string;time_zone:string;stops:ScheduleStop[];segments?:ScheduleSegment[];
  issues:{code:string;address?:string}[];warnings?:{code:string;address?:string}[];return_at:string|null;departure_at?:string|null;
  drive_min?:string|null;policy_id?:string;estimate_basis?:string;legal_compliance_verified?:boolean;operational_admission?:boolean;
  destination_time_zones_verified?:boolean;depot_address:string|null;source_hash?:string};

export const ISSUE_LABELS:Record<string,string>={
  ROUTE_ROAD_MISSING_STALE_OR_UNSUPPORTED:"Дорожные данные отсутствуют или устарели",ROUTE_ORDER_INVALID:"Некорректный порядок адресов",
  DELIVERY_WINDOW_MISSING_OR_DISJOINT:"Окна СТ не заданы или не пересекаются",DESTINATION_RULE_INVALID:"Некорректный норматив или правило окна адресата",
  DRIVER_TRIP_DRIVE_LIMIT:"Превышен предел вождения за рейс",ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE:"Маршрут не помещается в плановое время ресурса",
  DELIVERY_WINDOW_MISSING:"Окно доставки не задано",DELIVERY_WINDOWS_HAVE_NO_INTERSECTION:"Окна СТ одного адреса не пересекаются",
  DESTINATION_ADDRESS_NOT_UNIQUE:"Адрес отсутствует или неоднозначен",DESTINATION_UNLOAD_NORM_UNKNOWN:"Норматив разгрузки неизвестен",
  DESTINATION_WINDOW_POLICY_UNKNOWN:"Строгость окна не задана",DESTINATION_ROAD_DURATION_UNKNOWN:"Дорожное время неизвестно",
  PREVIOUS_ROUTE_TIME_UNKNOWN:"Время предыдущего этапа неизвестно",DELIVERY_HARD_WINDOW_MISSED:"Строгое окно пропущено",
  DELIVERY_SOFT_WINDOW_MISSED:"Плановое окно пропущено",ROUTE_RETURN_TIME_UNKNOWN:"Возврат не рассчитан",
  ROUTE_DEPARTURE_STAGE_UNKNOWN:"Начало движения неизвестно",WAREHOUSE_DEPOT_NOT_CONFIGURED:"База склада не настроена",
  STORE_CLOSED:"Магазин закрыт в день прибытия",STORE_NO_FEASIBLE_INTERVAL:"Разгрузка не помещается ни в один интервал приёма",
  DELIVERY_WINDOW_UNCONFIGURED:"Окна приёма не заданы",DELIVERY_WINDOW_PARTIAL:"Окно СТ задано частично",
  DELIVERY_WINDOW_REVERSED_OR_EMPTY:"Окно СТ пустое или перевёрнуто",DELIVERY_WINDOW_DISJOINT:"Окна СТ и магазина не пересекаются",
  STORE_TIMEZONE_REQUIRED:"У магазина не задан часовой пояс",STORE_TIMEZONE_OR_WINDOW_INVALID:"Часовой пояс или окно магазина некорректны",
  STORE_WINDOW_DST_AMBIGUOUS_OR_NONEXISTENT:"Окно попадает на перевод часов",STORE_WEEKLY_INTERVAL_INVALID:"Интервал недельного расписания некорректен",
  DELIVERY_MEMBERS_MISSING:"Нет СТ остановки",ROUTE_ARRIVAL_UNKNOWN:"Время прибытия неизвестно",
};
export const issueText=(code:string)=>ISSUE_LABELS[code]||"Требуется уточнение";

export const SEGMENT_LABELS:Record<string,string>={DRIVE:"Движение",DRIVE_BACK:"Возврат на базу",REST:"Перерыв водителя",WAIT:"Ожидание окна",
  UNLOAD:"Разгрузка",DOCK_ASSIGN:"Назначение ворот",WAIT_LOAD:"Ожидание погрузки",LOADING:"Погрузка",CLOSE_GATE:"Закрытие ворот",
  DOCUMENTS:"Документы",DEPART:"Выезд",LOAD_RETURNS:"Погрузка возвратов",RETURN_HANDOVER:"Сдача возвратов",CLEAN_RETURNS:"Разбор возвратов"};

// Серверный статус → тон. Неизвестный статус не считается готовностью.
export function statusView(status:string):{tone:"ok"|"warn"|"bad"|"neutral";text:string}{
  if(status==="NO_EARLIEST_WINDOW_VIOLATION")return{tone:"ok",text:"В ранней оценке окна соблюдены (это не допуск к выезду)"};
  if(status==="WINDOW_VIOLATION")return{tone:"bad",text:"Есть пропущенные окна"};
  if(status==="INSUFFICIENT_EVIDENCE")return{tone:"warn",text:"Недостаточно данных для расчёта"};
  return{tone:"neutral",text:"Статус сервера: "+status};
}

export const WINDOW_SOURCES:Record<string,string>={ST_MATERIALIZED:"окно СТ",STORE_WEEKLY:"недельное расписание магазина",ST_AND_STORE_WEEKLY:"окно СТ и расписание магазина"};
const DAYS=["Пн","Вт","Ср","Чт","Пт","Сб","Вс"];
const hm=(m:number)=>String(Math.floor(m/60)).padStart(2,"0")+":"+String(m%60).padStart(2,"0");
// Настроенная неделя магазина: интервалы по дням без склейки; день без интервалов — закрыт. Старый ответ без полей → null (не показывается).
export function weeklyText(s:ScheduleStop):string|null{
  if(s.store_window_mode===undefined)return null;
  const v=s.profile_version!=null?"профиль v"+s.profile_version:"профиль магазина отсутствует";
  if(s.store_window_mode!=="WEEKLY")return v+": окна приёма не заданы";
  const days=DAYS.map((d,i)=>{const w=(s.configured_weekly_windows||[]).filter(x=>x.weekday===i+1);return d+" "+(w.length?w.map(x=>hm(x.from_minute)+"–"+hm(x.to_minute)).join(", "):"закрыто");});
  return v+", "+(s.store_time_zone||"пояс не задан")+": "+days.join("; ");
}

// Время в часовом поясе отчёта; дата показывается, только если отличается от даты отправления.
export function clock(iso:string|null|undefined,zone:string,baseDay?:string):string{
  if(!iso)return"—";const d=new Date(iso);if(Number.isNaN(d.getTime()))return iso;
  try{
    const day=new Intl.DateTimeFormat("ru-RU",{timeZone:zone,day:"2-digit",month:"2-digit"}).format(d);
    const time=new Intl.DateTimeFormat("ru-RU",{timeZone:zone,hour:"2-digit",minute:"2-digit"}).format(d);
    return baseDay&&day===baseDay?time:day+" "+time;
  }catch{return iso;}
}
export function minutesBetween(a:string,b:string):number|null{const x=Date.parse(a),y=Date.parse(b);return Number.isNaN(x)||Number.isNaN(y)?null:Math.round((y-x)/60000);}
