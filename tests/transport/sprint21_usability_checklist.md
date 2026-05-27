# Sprint 21 — Usability Checklist
## Биллинг: раздельные права доступа

**Scope:** API `/api/admin/transport/billing/` · права `edit_bill_tt`, `calc_tt_price`, `create_tt_price`

---

### 1. Права чтения биллинга

| # | Проверка | Ожидание | ✓/✗ |
|---|----------|----------|-----|
| 1.1 | GET /billing/orders — пользователь с transport_dispatch_view | 200 OK | |
| 1.2 | GET /billing/orders/{id} — только просмотр | 200 OK | |
| 1.3 | GET /billing/orders/{id}/tasks — только просмотр | 200 OK | |

---

### 2. Права редактирования биллинга (edit_bill_tt)

| # | Проверка | Ожидание | ✓/✗ |
|---|----------|----------|-----|
| 2.1 | POST /billing/orders без edit_bill_tt | 403 Forbidden | |
| 2.2 | PATCH /billing/orders/{id}/close без edit_bill_tt | 403 Forbidden | |
| 2.3 | PATCH /billing/orders/{id}/pay без edit_bill_tt | 403 Forbidden | |
| 2.4 | POST /billing/orders/{id}/tasks без edit_bill_tt | 403 Forbidden | |
| 2.5 | DELETE /billing/orders/{id}/tasks/{tt} без edit_bill_tt | 403 Forbidden | |
| 2.6 | POST /tasks/{id}/billing/open без edit_bill_tt | 403 Forbidden | |

---

### 3. Право пересчёта цены (calc_tt_price)

| # | Проверка | Ожидание | ✓/✗ |
|---|----------|----------|-----|
| 3.1 | POST /tasks/{id}/recalculate-price без calc_tt_price | 403 Forbidden | |
| 3.2 | POST /tasks/{id}/recalculate-price с calc_tt_price | 200 OK | |

---

### 4. Право ручной установки цены (create_tt_price)

| # | Проверка | Ожидание | ✓/✗ |
|---|----------|----------|-----|
| 4.1 | PATCH /tasks/{id}/price без create_tt_price | 403 Forbidden | |
| 4.2 | PATCH /tasks/{id}/price с create_tt_price | 200 OK | |

---

### Итоговая оценка

| Категория | Пройдено | Всего |
|-----------|----------|-------|
| 1. Чтение | | 3 |
| 2. Редактирование | | 6 |
| 3. Пересчёт цены | | 2 |
| 4. Ручная цена | | 2 |
| **ИТОГО** | | **13** |

**Проверил:** _______________  **Дата:** _______________
