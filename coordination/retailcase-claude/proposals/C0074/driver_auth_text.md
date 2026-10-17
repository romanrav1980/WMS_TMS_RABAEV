# Аудит текста отказа входа водителя (C-0093)

**Наблюдение** (`reports/.../C0074/block5/scripts/driver_identity_check.cjs`): при неверном входе водителю показывается «Error: Admin login required.».

Идентичность при этом изолирована: запрос идёт от учётной записи водителя, без cookie, ответ 401.

**Причины:**
1. `api/wms_api_server/app/auth.py:211` — `raise_unauthorized()` для любого Basic-отказа отдаёт `detail="Admin login required."`. Текст общий для всех клиентов, включая `/api/driver/*`.
2. `admin/wms_admin_frontend/src/features/transport/driverApi.ts:13` показывает `body.detail` как есть.
3. `useDriverWorkspace.ts:23,29` выводит `String(e)`, отсюда префикс «Error: ».

**Рекомендация** — клиентское сопоставление статуса для экрана водителя. Сервер менять не обязательно: его текст служебный.

```ts
// driverApi.ts, вместо строки 13
const DRIVER_STATUS: Record<number, string> = {
  401: "Неверный пользователь или пароль. Проверьте данные и войдите снова.",
  403: "Учётная запись не привязана к этому водителю или нет доступа к рейсу. Обратитесь к диспетчеру.",
  404: "Рейс или операция не найдены. Обновите список рейсов.",
};
if(!response.ok)throw new DriverApiError(DRIVER_STATUS[response.status]??(typeof body.detail?.message==="string"?body.detail.message:"Сервер отклонил запрос."),response.status);
```

```ts
// useDriverWorkspace.ts, строки 23 и 29: без «Error: »
setError(e instanceof Error ? e.message : String(e));
```

Для 409 и других бизнес-отказов можно сохранить `detail.message` сервера: это понятные пользователю тексты. Неизвестный исход отметки (сеть или 5xx) уже обрабатывается сохранённой отметкой и повтором — его не трогать.

Владелец файлов — transport/root. Claude их не правил.
