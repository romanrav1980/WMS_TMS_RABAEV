# -*- coding: utf-8 -*-
"""Seed demo retail distribution-center customers without shell encoding risks.

The script is intentionally kept as a UTF-8 file and uses python-oracledb
bind variables. Do not paste these seed values into inline PowerShell commands:
that is how the previous question marks were written into Oracle.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import oracledb


MARKER = "DEMO_RETAIL_CUSTOMER_SEED"
DEFAULT_DSN = "127.0.0.1:1521/orcl"
DEFAULT_USER = "RABAEV"
DEFAULT_PASSWORD = "RABAEVWMS"


@dataclass(frozen=True)
class DcRecord:
    label: str
    city: str
    region: str


VEHICLES = [
    ("FTL33", "Фура 33 паллеты", 33, 20000, 86),
    ("REF33", "Рефрижератор 33 паллеты", 33, 19000, 82),
    ("FTL20", "Средний грузовик 20 паллет", 20, 12000, 52),
    ("CITY10", "Городская машина 10 паллет", 10, 6000, 28),
]
VEHICLE_CYCLE = ["FTL33", "REF33", "FTL20", "CITY10"]
PRODUCT_CYCLE = ["FG-DOG-10KG", "FG-CAT-5KG", "FG-PUPPY-3KG", "FG-KITTEN-2KG"]
SHELF_DAYS_CYCLE = [30, 45, 60, 75, 90]
SHELF_PERCENT_CYCLE = [65, 70, 75, 80, 85]
STACK_CASES_CYCLE = [48, 54, 60, 66, 72]

MAGNIT_DCS = [
    DcRecord("Краснодар РЦ", "Краснодар", "Краснодарский край"),
    DcRecord("Тихорецк РЦ", "Тихорецк", "Краснодарский край"),
    DcRecord("Ростов РЦ", "Ростов-на-Дону", "Ростовская область"),
    DcRecord("Воронеж РЦ", "Воронеж", "Воронежская область"),
    DcRecord("Самара РЦ", "Самара", "Самарская область"),
    DcRecord("Казань РЦ", "Казань", "Республика Татарстан"),
    DcRecord("Екатеринбург РЦ", "Екатеринбург", "Свердловская область"),
    DcRecord("Новосибирск РЦ", "Новосибирск", "Новосибирская область"),
    DcRecord("Санкт-Петербург РЦ", "Санкт-Петербург", "Ленинградская область"),
    DcRecord("Москва Юг РЦ", "Домодедово", "Московская область"),
    DcRecord("Нижний Новгород РЦ", "Нижний Новгород", "Нижегородская область"),
    DcRecord("Пермь РЦ", "Пермь", "Пермский край"),
]

X5_DCS = [
    DcRecord("Софьино РЦ", "Раменское", "Московская область"),
    DcRecord("Подольск РЦ", "Подольск", "Московская область"),
    DcRecord("Внуково РЦ", "Москва", "Москва"),
    DcRecord("Санкт-Петербург Север РЦ", "Санкт-Петербург", "Ленинградская область"),
    DcRecord("Новгород РЦ", "Великий Новгород", "Новгородская область"),
    DcRecord("Ярославль РЦ", "Ярославль", "Ярославская область"),
    DcRecord("Тула РЦ", "Тула", "Тульская область"),
    DcRecord("Воронеж РЦ", "Воронеж", "Воронежская область"),
    DcRecord("Нижний Новгород РЦ", "Нижний Новгород", "Нижегородская область"),
    DcRecord("Казань РЦ", "Казань", "Республика Татарстан"),
    DcRecord("Самара РЦ", "Самара", "Самарская область"),
    DcRecord("Екатеринбург РЦ", "Екатеринбург", "Свердловская область"),
    DcRecord("Челябинск РЦ", "Челябинск", "Челябинская область"),
    DcRecord("Новосибирск РЦ", "Новосибирск", "Новосибирская область"),
    DcRecord("Красноярск РЦ", "Красноярск", "Красноярский край"),
    DcRecord("Пермь РЦ", "Пермь", "Пермский край"),
    DcRecord("Ростов РЦ", "Ростов-на-Дону", "Ростовская область"),
    DcRecord("Краснодар РЦ", "Краснодар", "Краснодарский край"),
    DcRecord("Уфа РЦ", "Уфа", "Республика Башкортостан"),
    DcRecord("Омск РЦ", "Омск", "Омская область"),
]


def connect() -> oracledb.Connection:
    return oracledb.connect(
        user=os.environ.get("WMS_ORACLE_USER", DEFAULT_USER),
        password=os.environ.get("WMS_ORACLE_PASSWORD", DEFAULT_PASSWORD),
        dsn=os.environ.get("WMS_ORACLE_DSN", DEFAULT_DSN),
    )


def scalar(cur: oracledb.Cursor, sql: str, **params):
    cur.execute(sql, params)
    row = cur.fetchone()
    return row[0] if row else None


def nextval(cur: oracledb.Cursor, sequence_name: str) -> int:
    return int(scalar(cur, f"select {sequence_name}.nextval from dual"))


def upsert_vehicle(cur: oracledb.Cursor, code: str, name: str, pallets: int, weight: int, volume: int) -> int:
    vehicle_id = scalar(
        cur,
        "select VEHICLE_TYPE_ID from RRL_VEHICLE_TYPE where VEHICLE_TYPE_CODE = :code",
        code=code,
    )
    if vehicle_id is None:
        vehicle_id = nextval(cur, "RRL_VEHICLE_TYPE_SQ")
        cur.execute(
            """
            insert into RRL_VEHICLE_TYPE (
              VEHICLE_TYPE_ID, VEHICLE_TYPE_CODE, VEHICLE_TYPE_NAME,
              MAX_PALLET_COUNT, MAX_WEIGHT, MAX_VOLUME, ACTIVE, CREATED_AT, CREATED_BY
            ) values (
              :vehicle_id, :code, :name, :pallets, :weight, :volume, 1, sysdate, :marker
            )
            """,
            vehicle_id=vehicle_id,
            code=code,
            name=name,
            pallets=pallets,
            weight=weight,
            volume=volume,
            marker=MARKER,
        )
    else:
        cur.execute(
            """
            update RRL_VEHICLE_TYPE
               set VEHICLE_TYPE_NAME = :name,
                   MAX_PALLET_COUNT = :pallets,
                   MAX_WEIGHT = :weight,
                   MAX_VOLUME = :volume,
                   ACTIVE = 1,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = :marker
             where VEHICLE_TYPE_ID = :vehicle_id
            """,
            vehicle_id=vehicle_id,
            name=name,
            pallets=pallets,
            weight=weight,
            volume=volume,
            marker=MARKER,
        )
    return int(vehicle_id)


def upsert_customer(cur: oracledb.Cursor, payload: dict) -> int:
    customer_id = scalar(
        cur,
        "select CUSTOMER_ID from RRL_CUSTOMER where CUSTOMER_CODE = :customer_code",
        customer_code=payload["customer_code"],
    )
    if customer_id is None:
        customer_id = nextval(cur, "RRL_CUSTOMER_SQ")
        cur.execute(
            """
            insert into RRL_CUSTOMER (
              CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME, CUSTOMER_TYPE, INN, KPP, GLN, EDI_ID,
              DEFAULT_VEHICLE_TYPE_ID, SPLIT_ORDER_BY_VEHICLE_CAPACITY,
              DEFAULT_MIN_SHELF_LIFE_DAYS, DEFAULT_MIN_SHELF_LIFE_PERCENT,
              ACTIVE, CREATED_AT, CREATED_BY
            ) values (
              :customer_id, :customer_code, :customer_name, 'DISTRIBUTOR', :inn, :kpp, :gln, :edi_id,
              :vehicle_type_id, :split_by_vehicle, :shelf_days, :shelf_percent, 1, sysdate, :marker
            )
            """,
            customer_id=customer_id,
            marker=MARKER,
            **payload,
        )
    else:
        cur.execute(
            """
            update RRL_CUSTOMER
               set CUSTOMER_CODE = :customer_code,
                   CUSTOMER_NAME = :customer_name,
                   CUSTOMER_TYPE = 'DISTRIBUTOR',
                   INN = :inn,
                   KPP = :kpp,
                   GLN = :gln,
                   EDI_ID = :edi_id,
                   DEFAULT_VEHICLE_TYPE_ID = :vehicle_type_id,
                   SPLIT_ORDER_BY_VEHICLE_CAPACITY = :split_by_vehicle,
                   DEFAULT_MIN_SHELF_LIFE_DAYS = :shelf_days,
                   DEFAULT_MIN_SHELF_LIFE_PERCENT = :shelf_percent,
                   ACTIVE = 1,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = :marker
             where CUSTOMER_ID = :customer_id
            """,
            customer_id=customer_id,
            marker=MARKER,
            **payload,
        )
    return int(customer_id)


def upsert_delivery_address(cur: oracledb.Cursor, customer_id: int, payload: dict) -> None:
    address_id = scalar(
        cur,
        """
        select CUSTOMER_ADDRESS_ID
          from RRL_CUSTOMER_ADDRESS
         where CUSTOMER_ID = :customer_id
           and ADDRESS_TYPE = 'DELIVERY'
           and rownum = 1
        """,
        customer_id=customer_id,
    )
    if address_id is None:
        address_id = nextval(cur, "RRL_CUSTOMER_ADDRESS_SQ")
        cur.execute(
            """
            insert into RRL_CUSTOMER_ADDRESS (
              CUSTOMER_ADDRESS_ID, CUSTOMER_ID, ADDRESS_TYPE, ADDRESS_TEXT, CITY, REGION,
              POSTAL_CODE, GLN, ACTIVE, CREATED_AT, CREATED_BY
            ) values (
              :address_id, :customer_id, 'DELIVERY', :address_text, :city, :region,
              :postal_code, :address_gln, 1, sysdate, :marker
            )
            """,
            address_id=address_id,
            customer_id=customer_id,
            marker=MARKER,
            **payload,
        )
    else:
        cur.execute(
            """
            update RRL_CUSTOMER_ADDRESS
               set ADDRESS_TEXT = :address_text,
                   CITY = :city,
                   REGION = :region,
                   POSTAL_CODE = :postal_code,
                   GLN = :address_gln,
                   ACTIVE = 1,
                   UPDATED_AT = sysdate,
                   UPDATED_BY = :marker
             where CUSTOMER_ADDRESS_ID = :address_id
            """,
            address_id=address_id,
            marker=MARKER,
            **payload,
        )


def upsert_shelf_rule(cur: oracledb.Cursor, customer_id: int, articul: str, days: int, percent: int) -> None:
    rule_id = scalar(
        cur,
        """
        select SHELF_LIFE_RULE_ID
          from RRL_CUSTOMER_SHELF_LIFE_RULE
         where CUSTOMER_ID = :customer_id
           and CREATED_BY = :marker
           and rownum = 1
        """,
        customer_id=customer_id,
        marker=MARKER,
    )
    if rule_id is None:
        rule_id = nextval(cur, "RRL_CSL_RULE_SQ")
        cur.execute(
            """
            insert into RRL_CUSTOMER_SHELF_LIFE_RULE (
              SHELF_LIFE_RULE_ID, CUSTOMER_ID, ARTICUL, MIN_SHELF_LIFE_DAYS,
              MIN_SHELF_LIFE_PERCENT, RULE_PRIORITY, ACTIVE, VALID_FROM, CREATED_AT, CREATED_BY
            ) values (
              :rule_id, :customer_id, :articul, :days, :percent, 10, 1, trunc(sysdate), sysdate, :marker
            )
            """,
            rule_id=rule_id,
            customer_id=customer_id,
            articul=articul,
            days=days,
            percent=percent,
            marker=MARKER,
        )
    else:
        cur.execute(
            """
            update RRL_CUSTOMER_SHELF_LIFE_RULE
               set ARTICUL = :articul,
                   MIN_SHELF_LIFE_DAYS = :days,
                   MIN_SHELF_LIFE_PERCENT = :percent,
                   RULE_PRIORITY = 10,
                   ACTIVE = 1
             where SHELF_LIFE_RULE_ID = :rule_id
            """,
            rule_id=rule_id,
            articul=articul,
            days=days,
            percent=percent,
        )


def upsert_stack_rule(cur: oracledb.Cursor, customer_id: int, idx: int, articul: str) -> None:
    rule_id = scalar(
        cur,
        """
        select STACK_RULE_ID
          from RRL_CUSTOMER_PRODUCT_STACK_RULE
         where CUSTOMER_ID = :customer_id
           and CREATED_BY = :marker
           and rownum = 1
        """,
        customer_id=customer_id,
        marker=MARKER,
    )
    payload = {
        "articul": articul,
        "pallet_case_qty": STACK_CASES_CYCLE[idx % len(STACK_CASES_CYCLE)],
        "pallet_layer_qty": 10 + (idx % 4),
        "pallet_layer_count": 4 + (idx % 4),
        "allow_top_stacking": 1 if idx % 5 in (0, 1) else 0,
        "must_be_separate_pallet": 1 if idx in (5, 10, 15, 20) else 0,
    }
    if rule_id is None:
        rule_id = nextval(cur, "RRL_CPS_RULE_SQ")
        cur.execute(
            """
            insert into RRL_CUSTOMER_PRODUCT_STACK_RULE (
              STACK_RULE_ID, CUSTOMER_ID, ARTICUL, PALLET_CASE_QTY, PALLET_LAYER_QTY,
              PALLET_LAYER_COUNT, ALLOW_TOP_STACKING, MUST_BE_SEPARATE_PALLET,
              RULE_PRIORITY, ACTIVE, VALID_FROM, CREATED_AT, CREATED_BY
            ) values (
              :rule_id, :customer_id, :articul, :pallet_case_qty, :pallet_layer_qty,
              :pallet_layer_count, :allow_top_stacking, :must_be_separate_pallet,
              10, 1, trunc(sysdate), sysdate, :marker
            )
            """,
            rule_id=rule_id,
            customer_id=customer_id,
            marker=MARKER,
            **payload,
        )
    else:
        cur.execute(
            """
            update RRL_CUSTOMER_PRODUCT_STACK_RULE
               set ARTICUL = :articul,
                   PALLET_CASE_QTY = :pallet_case_qty,
                   PALLET_LAYER_QTY = :pallet_layer_qty,
                   PALLET_LAYER_COUNT = :pallet_layer_count,
                   ALLOW_TOP_STACKING = :allow_top_stacking,
                   MUST_BE_SEPARATE_PALLET = :must_be_separate_pallet,
                   RULE_PRIORITY = 10,
                   ACTIVE = 1
             where STACK_RULE_ID = :rule_id
            """,
            rule_id=rule_id,
            **payload,
        )


def upsert_vehicle_rule(cur: oracledb.Cursor, customer_id: int, vehicle: tuple, vehicle_id: int, split: int) -> None:
    rule_id = scalar(
        cur,
        """
        select CUSTOMER_VEHICLE_RULE_ID
          from RRL_CUSTOMER_VEHICLE_RULE
         where CUSTOMER_ID = :customer_id
           and CREATED_BY = :marker
           and rownum = 1
        """,
        customer_id=customer_id,
        marker=MARKER,
    )
    _, _, pallets, weight, volume = vehicle
    payload = {
        "vehicle_type_id": vehicle_id,
        "max_pallet_count": pallets,
        "max_weight": weight,
        "max_volume": volume,
        "split_by_vehicle": split,
    }
    if rule_id is None:
        rule_id = nextval(cur, "RRL_CVR_SQ")
        cur.execute(
            """
            insert into RRL_CUSTOMER_VEHICLE_RULE (
              CUSTOMER_VEHICLE_RULE_ID, CUSTOMER_ID, VEHICLE_TYPE_ID, MAX_PALLET_COUNT,
              MAX_WEIGHT, MAX_VOLUME, SPLIT_ORDER_BY_CAPACITY, RULE_PRIORITY,
              ACTIVE, VALID_FROM, CREATED_AT, CREATED_BY
            ) values (
              :rule_id, :customer_id, :vehicle_type_id, :max_pallet_count,
              :max_weight, :max_volume, :split_by_vehicle, 10,
              1, trunc(sysdate), sysdate, :marker
            )
            """,
            rule_id=rule_id,
            customer_id=customer_id,
            marker=MARKER,
            **payload,
        )
    else:
        cur.execute(
            """
            update RRL_CUSTOMER_VEHICLE_RULE
               set VEHICLE_TYPE_ID = :vehicle_type_id,
                   MAX_PALLET_COUNT = :max_pallet_count,
                   MAX_WEIGHT = :max_weight,
                   MAX_VOLUME = :max_volume,
                   SPLIT_ORDER_BY_CAPACITY = :split_by_vehicle,
                   RULE_PRIORITY = 10,
                   ACTIVE = 1
             where CUSTOMER_VEHICLE_RULE_ID = :rule_id
            """,
            rule_id=rule_id,
            **payload,
        )


def seed_customers(cur: oracledb.Cursor, vehicle_ids: dict[str, int], network: str, records: list[DcRecord]) -> None:
    is_magnit = network == "MAGNIT"
    for idx, record in enumerate(records, start=1):
        code = f"MAGNIT-DC-{idx:02d}" if is_magnit else f"X5-DC-{idx:02d}"
        vehicle_code = VEHICLE_CYCLE[(idx - 1) % len(VEHICLE_CYCLE)] if is_magnit else VEHICLE_CYCLE[idx % len(VEHICLE_CYCLE)]
        vehicle = next(row for row in VEHICLES if row[0] == vehicle_code)
        split = 1 if (idx in (1, 2, 3, 8, 10) if is_magnit else idx % 3 == 0 or idx in (1, 2, 19, 20)) else 0
        customer_id = upsert_customer(
            cur,
            {
                "customer_code": code,
                "customer_name": f"Magnit / AO Tander - {record.label}" if is_magnit else f"X5 Group - {record.label}",
                "inn": "2310031475" if is_magnit else "7733574601",
                "kpp": (f"230{idx:03d}001" if is_magnit else f"770{idx:03d}001"),
                "gln": (f"46070010{idx:05d}" if is_magnit else f"46080010{idx:05d}"),
                "edi_id": (f"TANDER-{idx:02d}" if is_magnit else f"X5-{idx:02d}"),
                "vehicle_type_id": vehicle_ids[vehicle_code],
                "split_by_vehicle": split,
                "shelf_days": SHELF_DAYS_CYCLE[(idx - 1 if is_magnit else idx) % len(SHELF_DAYS_CYCLE)],
                "shelf_percent": SHELF_PERCENT_CYCLE[(idx + 1 if is_magnit else idx + 2) % len(SHELF_PERCENT_CYCLE)],
            },
        )
        upsert_delivery_address(
            cur,
            customer_id,
            {
                "address_text": (
                    f"{record.region}, {record.city}, складской комплекс Magnit/Tander {idx:02d}"
                    if is_magnit
                    else f"{record.region}, {record.city}, распределительный центр X5 {idx:02d}"
                ),
                "city": record.city,
                "region": record.region,
                "postal_code": (f"35{idx:04d}" if is_magnit else f"14{idx:04d}"),
                "address_gln": (f"46070020{idx:05d}" if is_magnit else f"46080020{idx:05d}"),
            },
        )
        upsert_shelf_rule(
            cur,
            customer_id,
            PRODUCT_CYCLE[(idx - 1 if is_magnit else idx) % len(PRODUCT_CYCLE)],
            SHELF_DAYS_CYCLE[(idx + 1 if is_magnit else idx + 2) % len(SHELF_DAYS_CYCLE)],
            SHELF_PERCENT_CYCLE[(idx - 1 if is_magnit else idx) % len(SHELF_PERCENT_CYCLE)],
        )
        upsert_stack_rule(cur, customer_id, idx, PRODUCT_CYCLE[(idx if is_magnit else idx + 1) % len(PRODUCT_CYCLE)])
        upsert_vehicle_rule(cur, customer_id, vehicle, vehicle_ids[vehicle_code], split)


def verify_counts(cur: oracledb.Cursor) -> tuple:
    cur.execute(
        """
        select
          (select count(*) from RRL_CUSTOMER where CUSTOMER_CODE like 'MAGNIT-DC-%') MAGNIT_CNT,
          (select count(*) from RRL_CUSTOMER where CUSTOMER_CODE like 'X5-DC-%') X5_CNT,
          (select count(*) from RRL_CUSTOMER_ADDRESS a join RRL_CUSTOMER c on c.CUSTOMER_ID = a.CUSTOMER_ID where c.CUSTOMER_CODE like 'MAGNIT-DC-%' or c.CUSTOMER_CODE like 'X5-DC-%') ADDRESS_CNT,
          (select count(*) from RRL_CUSTOMER_SHELF_LIFE_RULE r join RRL_CUSTOMER c on c.CUSTOMER_ID = r.CUSTOMER_ID where c.CUSTOMER_CODE like 'MAGNIT-DC-%' or c.CUSTOMER_CODE like 'X5-DC-%') SHELF_CNT,
          (select count(*) from RRL_CUSTOMER_PRODUCT_STACK_RULE r join RRL_CUSTOMER c on c.CUSTOMER_ID = r.CUSTOMER_ID where c.CUSTOMER_CODE like 'MAGNIT-DC-%' or c.CUSTOMER_CODE like 'X5-DC-%') STACK_CNT,
          (select count(*) from RRL_CUSTOMER_VEHICLE_RULE r join RRL_CUSTOMER c on c.CUSTOMER_ID = r.CUSTOMER_ID where c.CUSTOMER_CODE like 'MAGNIT-DC-%' or c.CUSTOMER_CODE like 'X5-DC-%') VEHICLE_CNT,
          (select count(*) from USER_OBJECTS where STATUS <> 'VALID') INVALID_CNT
        from dual
        """
    )
    return cur.fetchone()


def main() -> None:
    with connect() as connection:
        cur = connection.cursor()
        vehicle_ids = {
            code: upsert_vehicle(cur, code, name, pallets, weight, volume)
            for code, name, pallets, weight, volume in VEHICLES
        }
        seed_customers(cur, vehicle_ids, "MAGNIT", MAGNIT_DCS)
        seed_customers(cur, vehicle_ids, "X5", X5_DCS)
        counts = verify_counts(cur)
        if counts != (12, 20, 32, 32, 32, 32, 0):
            raise RuntimeError(f"Unexpected verification counts: {counts}")
        connection.commit()
        print("Retail customer demo seed applied:", counts)


if __name__ == "__main__":
    main()
