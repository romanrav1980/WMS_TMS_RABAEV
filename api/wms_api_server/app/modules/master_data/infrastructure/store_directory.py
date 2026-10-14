from typing import Any

# Справочник магазинов собирается из уже существующих источников без копирования данных:
# RRL_ADDR — адрес, логистика и ограничения доставки; RRL_STORE_RECEIPT_POLICY — режим приёмки;
# RRL_STORE_RECEIPT_USER — назначенные получатели; RRL_TARE_RETURN_POLICY — срок возврата тары;
# RRL_CUSTOMER_STORE_MAP / RRL_SAP_STORE_CALENDAR — код магазина в ERP и календарь поставок.
# Ключ магазина — ADDR (как в СТ, правилах качества и приёмке). Поиск ограничен keyset-страницей.
# Связь с ERP (RRL_CUSTOMER_STORE_MAP.LEGACY_ADDR) уникальна только по нормализованному ключу, само поле не ограничено:
# поиск даёт ровно одну строку на ADDR (совпадение кода через EXISTS, число связей отдельно), карточка — полный
# список связей; при нескольких активных связях код ERP не выбирается произвольно (erp_link_state=AMBIGUOUS).
_SEARCH = """select a.ADDR,a.REGION,a.RAION,a.NAPR,a.TRANSPORT_TYPE,a.SHIPPING_TIME,a.STOL,
       (select count(*) from RRL_CUSTOMER_STORE_MAP m where m.LEGACY_ADDR=a.ADDR and m.ACTIVE=1) ERP_LINK_COUNT,
       (select max(m.STORE_CODE) from RRL_CUSTOMER_STORE_MAP m where m.LEGACY_ADDR=a.ADDR and m.ACTIVE=1
         having count(*)=1) STORE_CODE
  from RRL_ADDR a
 where nvl(a.DELETED3,0)=0
   and(:pattern is null or upper(a.ADDR) like :pattern escape '!' or upper(a.REGION) like :pattern escape '!'
       or upper(a.RAION) like :pattern escape '!'
       or exists(select 1 from RRL_CUSTOMER_STORE_MAP m where m.LEGACY_ADDR=a.ADDR and m.ACTIVE=1 and upper(m.STORE_CODE) like :pattern escape '!'))
   and(:after is null or a.ADDR>:after)
 order by a.ADDR fetch first :fetch rows only"""

_CARD = """select a.ADDR,a.REGION,a.RAION,a.NAPR,a.ORD,a.TRANSPORT_TYPE,a.STOL,a.SHIROTA LATITUDE,a.DOLGOTA LONGITUDE,
       nvl(a.GEO_FENCE_RADIUS_M,200) GEO_FENCE_RADIUS_M,a.LEAD_TIME,a.SHIPPING_TIME,a.DOCK_DEFAULT,a.MAX_VEHICLE_TONS,
       a.UNLOAD_NORM_MIN,a.TW_STRICT,a.CLIENT_GROUP,a.RESERVATION_ORDER,a.PRIM1,a.PRIM2,a.EMAIL,
       p.RECEIPT_MODE,p.POLICY_VERSION RECEIPT_POLICY_VERSION,
       (select count(*) from RRL_STORE_RECEIPT_USER u where u.STORE_ADDR=a.ADDR) RECEIVER_COUNT,
       t.RETURN_MODE TARE_RETURN_MODE,t.RETURN_DAYS TARE_RETURN_DAYS,t.TIMEZONE_REGION TARE_TIMEZONE,t.POLICY_VERSION TARE_POLICY_VERSION
  from RRL_ADDR a
  left join RRL_STORE_RECEIPT_POLICY p on p.STORE_ADDR=a.ADDR
  left join RRL_TARE_RETURN_POLICY t on t.SCOPE_KIND='STORE' and t.SCOPE_KEY=a.ADDR
 where a.ADDR=:address and nvl(a.DELETED3,0)=0"""

_ERP_LINKS = """select m.CUSTOMER_STORE_MAP_ID,m.STORE_CODE,m.STORE_NAME,m.GLN,m.EDI_ID,m.CUSTOMER_ID
  from RRL_CUSTOMER_STORE_MAP m where m.LEGACY_ADDR=:address and m.ACTIVE=1
 order by m.CUSTOMER_STORE_MAP_ID fetch first 11 rows only"""

# Календарь поставок привязан к складу: показываются только склады, доступные пользователю (GLOBAL_ADMIN или свой WARE_ID).
_CALENDARS = """select c.CUSTOMER_STORE_MAP_ID,c.WARE_ID,c.DELIVERY_WEEKDAYS,c.ALLOW_SAME_DAY,c.UTC_OFFSET_MINUTES,c.UPDATED_AT
  from RRL_SAP_STORE_CALENDAR c join RRL_CUSTOMER_STORE_MAP m on m.CUSTOMER_STORE_MAP_ID=c.CUSTOMER_STORE_MAP_ID
 where m.LEGACY_ADDR=:address and m.ACTIVE=1 and exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
       and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN' or u.WARE_ID=c.WARE_ID))
 order by c.CUSTOMER_STORE_MAP_ID,c.WARE_ID fetch first 50 rows only"""


def _pattern(query: str | None) -> str | None:
    text = (query or "").strip().upper()
    if not text:
        return None
    return "%" + text.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"


class StoreDirectory:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def search(self, query: str | None, after: str | None, limit: int) -> dict[str, Any]:
        rows = self.gateway.fetch_all(_SEARCH, {"pattern": _pattern(query), "after": after or None, "fetch": limit + 1})
        items = rows[:limit]
        return {"items": items, "next_after": items[-1]["addr"] if len(rows) > limit and items else None,
                "source": "RRL_ADDR", "deleted_excluded": True}

    def card(self, address: str, actor: str) -> dict[str, Any] | None:
        rows = self.gateway.fetch_all(_CARD, {"address": address})
        if not rows:
            return None
        card = dict(rows[0])
        links = self.gateway.fetch_all(_ERP_LINKS, {"address": address})
        card["erp_links"] = links[:10]
        card["erp_link_state"] = "NONE" if not links else "SINGLE" if len(links) == 1 else "AMBIGUOUS"
        single = links[0] if len(links) == 1 else {}
        for key in ("store_code", "store_name", "gln", "edi_id"):
            card[key] = single.get(key)
        card["delivery_calendars"] = self.gateway.fetch_all(_CALENDARS, {"address": address, "actor": actor}) if links else []
        card["calendar_scope"] = "ACTOR_WAREHOUSES"
        card["profile_extensions"] = None  # окна приёма, подсобка и др. — отдельно: GET /api/master-data/stores/profile
        return card
