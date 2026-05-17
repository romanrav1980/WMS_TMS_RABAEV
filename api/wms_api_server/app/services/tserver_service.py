from datetime import datetime
import re
from typing import Any

from ..db import scalar_to_text
from ..legacy_protocol import LegacyBlock, encode_legacy_blocks, fault, parse_legacy_payload, zero
from ..oracle_gateway import OracleGateway
from ..schemas import (
    CallSpfRequest,
    LotCheckRequest,
    OrderCheckRequest,
    PlaceCheckRequest,
)


UID_KEY = "\u0423\u0418\u0414"
QTY_KEY = "\u041a\u041e\u041b"
TYPE_KEY = "\u0422\u0418\u041f"
EAN_KEY = "\u0428\u0422\u0420\u0418\u0425\u041a\u041e\u0414"
PLAN_QTY_KEY = "\u041f\u041b\u0410\u041d_\u041a\u041e\u041b"
PICK_ZONE = "\u0417\u041e\u041d\u0410_\u042d\u041a\u0421\u041f\u0415\u0414\u0418\u0426\u0418\u0418"
ERROR_ZONE = "\u0417\u041e\u041d\u0410_\u041e\u0428\u0418\u0411\u041e\u041a"
MATCHED = "\u0421\u041e\u0412\u041f\u0410\u041b\u041e"
EXCESS = "\u0418\u0417\u041b\u0418\u0428\u041a\u0418"
SHORTAGE = "\u041d\u0415\u0414\u041e\u0421\u0422\u0410\u0427\u0410"


def normalize_pallet_identifier(value: str) -> str:
    raw = (value or "").strip()
    candidate = raw
    if candidate.startswith("]C1") or candidate.startswith("]d2"):
        candidate = candidate[3:]

    compact = re.sub(r"[\s-]", "", candidate)

    match = re.fullmatch(r"\(00\)(\d{18})", compact)
    if match:
        return match.group(1)

    match = re.fullmatch(r"00(\d{18})", compact)
    if match:
        return match.group(1)

    if re.fullmatch(r"\d{18}", compact):
        return compact

    return raw


CALL_SPF_ALLOWLIST = {
    "RABAEV.RRL_GIVE_DESTINATION_CELL2",
    "RABAEV.RRL_GIVE_POPOLNENIE2",
    "RABAEV.RRL_GET_PAL_INFOTEXT",
    "RABAEV.RRL_INTERNAL_MOVE3",
    "RABAEV.RRL_INV_CREATE_LINE4",
    "RABAEV.RRL_GIVE_NEXT_CELL",
    "RABAEV.RRL_GIVE_PREVIOUS_CELL",
    "RABAEV.RRL_SET_SBORKA_ZONE",
    "RABAEV.RRL_GIVE_KARSH_STAT_INFO",
    "RABAEV.RRL_REVIZION_CELL_KOR",
    "COMPL.SBORKA_FULL_PALL_PICK3",
}


class TserverService:
    def __init__(self, gateway: OracleGateway | None = None) -> None:
        self.gateway = gateway or OracleGateway()

    def execute_legacy_payload(self, payload: str) -> tuple[str, list[LegacyBlock]]:
        blocks = parse_legacy_payload(payload)
        if not blocks:
            response = [fault("Empty legacy payload.")]
            return encode_legacy_blocks(response), response

        try:
            response = self._dispatch(blocks)
        except Exception as exc:
            response = [fault(str(exc))]

        return encode_legacy_blocks(response), response

    def _dispatch(self, blocks: list[LegacyBlock]) -> list[LegacyBlock]:
        head = blocks[0]
        name = head.function_name

        if name == "GET_RUSER":
            return self.get_ruser(head.get("USERID"))
        if name == "GET_PRODUCT_INFO":
            return self.get_product_info(head.get("\u0428\u0422\u0420\u0418\u0425\u041a\u041e\u0414"))
        if name == "GET_LOT_ITEMS":
            return self.get_lot_items(head.get("USSCC"))
        if name == "GET_PLACE_ITEMS":
            return self.get_place_items(head.get("PLACEID"))
        if name == "LOT_CHECK_PASSED":
            request = self._lot_check_from_legacy(blocks)
            self.confirm_lot_check(head.get("USSCC"), request)
            return [LegacyBlock("END_LOT_CHECK_PASSED", {"USSCC": head.get("USSCC")})]
        if name == "PLACE_CHECK_PASSED":
            request = self._place_check_from_legacy(blocks)
            self.confirm_place_check(request)
            return [LegacyBlock("END_PALLET_CHECK_PASSED", {"PALLETID": request.pallet_id})]
        if name == "ORDER_CHECK_PASSED":
            request = self._order_check_from_legacy(blocks)
            self.confirm_order_check(request)
            return [LegacyBlock("END_ORDER_CHECK_PASSED", {"ORDER": request.order})]
        if name == "CALL_SPF":
            result = self.call_spf(CallSpfRequest(spf_name=head.get("SPF_NAME"), params=head.values))
            return [LegacyBlock("CALL_SP_INFO", {"ok": result})]

        return [zero()]

    def get_ruser(self, user_id: str) -> list[LegacyBlock]:
        rows = self.gateway.fetch_all(
            """
            select ID,
                   NAME,
                   PRAVO_INVENTORY_EDIT,
                   PRAVO_CHECK_ORDER,
                   PRAVO_LIGHT_INVENTORY_CHECK,
                   PRAVO_RAZVOZ_ZAYAVOK,
                   PRAVO_EAN_PRODUCT_CHANGE,
                   PRAVO_KARSHIK,
                   WARE_ID,
                   to_char(systimestamp, 'dd.mm.yyyy HH24:MI:ss') SYSTIMESTAMP
              from RABAEV.RUSERS
             where ID = :user_id
               and DELETED = 0
            """,
            {"user_id": user_id},
        )
        return [
            LegacyBlock(
                "USER_INFO",
                {
                    "ID": scalar_to_text(row.get("id")),
                    "NAME": scalar_to_text(row.get("name")),
                    "PRAVO_INVENTORY_EDIT": scalar_to_text(row.get("pravo_inventory_edit")),
                    "PRAVO_CHECK_ORDER": scalar_to_text(row.get("pravo_check_order")),
                    "PRAVO_LIGHT_INVENTORY_CHECK": scalar_to_text(row.get("pravo_light_inventory_check")),
                    "PRAVO_RAZVOZ_ZAYAVOK": scalar_to_text(row.get("pravo_razvoz_zayavok")),
                    "PRAVO_EAN_PRODUCT_CHANGE": scalar_to_text(row.get("pravo_ean_product_change")),
                    "PRAVO_KARSHIK": scalar_to_text(row.get("pravo_karshik")),
                    "ware_id": scalar_to_text(row.get("ware_id")),
                    "systimestamp": scalar_to_text(row.get("systimestamp")),
                },
            )
            for row in rows
        ]

    def get_product_info(self, barcode: str) -> list[LegacyBlock]:
        trimmed = barcode.strip("0")
        try:
            rows = self.gateway.fetch_all(
                """
                select distinct
                       substr(UE_ADRUMS, length(UE_ADRUMS)-1, 1) PIC_LEVEL,
                       UL_CPROIN,
                       UE_ADRUMS,
                       TB_ART.AR_LIBPRO,
                       TB_ART.AR_PDSUVC,
                       AR_PDSCAR,
                       AR_PDSSPC,
                       AR_PDSPAL,
                       sfera_ean.EAN_SHT,
                       sfera_ean.EAN_BL,
                       sfera_ean.EAN_KOR,
                       sfera_ean.SHT_IN_BL,
                       sfera_ean.BL_IN_KOR
                  from refstock.TB_LCUMS
                  left join refstock.TB_EUMS on ue_usscc = ul_usscc and UE_DEPOT = 01 and UE_PROPRI = 'RM'
                  left join refstock.TB_ART on AR_CPROIN = UL_CPROIN and AR_donord = 'RM'
                  left join RABAEV.SFERA_EAN sfera_ean on UL_CPROIN = sfera_ean.TMC_UID
                 where ul_donord = 'RM'
                   and sfera_ean.TMC_UID is not null
                   and UE_ADRUMS is not null
                   and (
                        EAN_SHT = :barcode or EAN_BL = :barcode or EAN_KOR = :barcode
                        or EAN_SHT = :trimmed or EAN_BL = :trimmed or EAN_KOR = :trimmed
                   )
                   and length(UE_ADRUMS) >= 1
                   and substr(UE_ADRUMS, length(UE_ADRUMS)-1, 1) in ('1','2')
                """,
                {"barcode": barcode, "trimmed": trimmed},
            )
        except Exception as exc:
            if "ORA-00942" not in str(exc):
                raise
            rows = self.gateway.fetch_all(
                """
                select distinct *
                  from (
                        select e.TMC_UID as UL_CPROIN,
                               a.CELL as UE_ADRUMS,
                               coalesce(e.NAME, a.NAME) as AR_LIBPRO,
                               a.COUNT_SHT_IN_BL as AR_PDSUVC,
                               a.COUNT_SHT_IN_KOR as AR_PDSCAR,
                               null as AR_PDSSPC,
                               null as AR_PDSPAL,
                               e.EAN_SHT,
                               e.EAN_BL,
                               e.EAN_KOR,
                               e.SHT_IN_BL,
                               e.BL_IN_KOR
                          from RABAEV.SFERA_EAN e
                          left join RABAEV.RRL_ARTICULS a on a.ACTICUL = e.TMC_UID
                         where e.TMC_UID is not null
                           and (
                                e.EAN_SHT = :barcode or e.EAN_BL = :barcode or e.EAN_KOR = :barcode
                                or e.EAN_SHT = :trimmed or e.EAN_BL = :trimmed or e.EAN_KOR = :trimmed
                           )
                        union all
                        select a.ACTICUL as UL_CPROIN,
                               a.CELL as UE_ADRUMS,
                               a.NAME as AR_LIBPRO,
                               a.COUNT_SHT_IN_BL as AR_PDSUVC,
                               a.COUNT_SHT_IN_KOR as AR_PDSCAR,
                               null as AR_PDSSPC,
                               null as AR_PDSPAL,
                               a.BARCODE_SHT as EAN_SHT,
                               a.BARCODE_BL as EAN_BL,
                               a.BARCODE_KOR as EAN_KOR,
                               a.COUNT_SHT_IN_BL as SHT_IN_BL,
                               round(a.COUNT_SHT_IN_KOR / nullif(a.COUNT_SHT_IN_BL, 0), 0) as BL_IN_KOR
                          from RABAEV.RRL_ARTICULS a
                         where a.ACTICUL is not null
                           and (
                                a.BARCODE_SHT = :barcode or a.BARCODE_BL = :barcode or a.BARCODE_KOR = :barcode
                                or a.BARCODE_SHT = :trimmed or a.BARCODE_BL = :trimmed or a.BARCODE_KOR = :trimmed
                           )
                       )
                """,
                {"barcode": barcode, "trimmed": trimmed},
            )

        return [
            LegacyBlock(
                "END_GET_PRODUCT_INFO",
                {
                    "\u0410\u0414\u0420\u0415\u0421": scalar_to_text(row.get("ue_adrums")),
                    UID_KEY: scalar_to_text(row.get("ul_cproin")),
                    "\u0418\u041c\u042f": scalar_to_text(row.get("ar_libpro")),
                    "\u0412\u0411_\u0428\u0422": scalar_to_text(row.get("ar_pdsuvc")),
                    "\u0412\u0411_\u041a\u041e\u0420": scalar_to_text(row.get("ar_pdscar")),
                    "\u0412\u0411_\u0411\u041b": scalar_to_text(row.get("ar_pdsspc")),
                    "\u0412\u0411_\u041f\u0410\u041b\u0415\u0422\u042b": scalar_to_text(row.get("ar_pdspal")),
                    "\u0428\u041a_\u0428\u0422\u0423\u041a\u0418": scalar_to_text(row.get("ean_sht")),
                    "\u0428\u041a_\u0411\u041b\u041e\u041a\u0410": scalar_to_text(row.get("ean_bl")),
                    "\u0428\u041a_\u041a\u041e\u0420\u041e\u0411": scalar_to_text(row.get("ean_kor")),
                    "\u0428\u0422\u0412\u0411\u041b": scalar_to_text(row.get("sht_in_bl")),
                    "\u0411\u041b\u0412\u041a\u041e\u0420": scalar_to_text(row.get("bl_in_kor")),
                },
            )
            for row in rows
        ]

    def get_lot_items(self, usscc: str) -> list[LegacyBlock]:
        usscc = normalize_pallet_identifier(usscc)
        rows = self.gateway.fetch_all(
            """
            select p.PALLET_UID,
                   r.ARTICUL,
                   r.QUANTITY,
                   r.SHORTNAME,
                   r.PATH,
                   a.COUNT_SHT_IN_BL,
                   round(a.COUNT_SHT_IN_KOR / nullif(a.COUNT_SHT_IN_BL, 0), 0) BL_IN_KOR,
                   a.BARCODE_SHT,
                   a.BARCODE_BL,
                   a.BARCODE_KOR,
                   p.ST_NUMBER
              from RRL_SBORKA_PALLETS p,
                   RRL_SBORKA_PALLET_ROWS r,
                   RRL_ARTICULS a
             where r.PALLET_UID = p.PALLET_UID
               and p.PALLET_UID = :usscc
               and r.ARTICUL = a.ACTICUL(+)
             order by SORTFIELD
            """,
            {"usscc": usscc},
        )
        blocks = [
            LegacyBlock(
                "LOT_LINES",
                {
                    "lines_count_must_be": str(len(rows)),
                    "order_number": scalar_to_text(rows[0].get("st_number")) if rows else "",
                },
            )
        ]
        for pos, row in enumerate(rows, start=1):
            blocks.append(
                LegacyBlock(
                    "LOT_LINE",
                    {
                        "\u041f\u041f": str(pos),
                        UID_KEY: scalar_to_text(row.get("articul")),
                        QTY_KEY: scalar_to_text(row.get("quantity")),
                        "\u041d\u0410\u0418\u041c": scalar_to_text(row.get("shortname")),
                        "\u0421\u041b\u0423\u0416_\u0410\u0414\u0420": scalar_to_text(row.get("path")),
                        "\u0421\u041b\u0423\u0416_\u0428\u0422\u0412\u0411\u041b": scalar_to_text(row.get("count_sht_in_bl")),
                        "\u0421\u041b\u0423\u0416_\u0411\u041b\u0412\u041a\u041e\u0420": scalar_to_text(row.get("bl_in_kor")),
                        "\u0421\u041b\u0423\u0416_\u0428\u041a_\u0428\u0422\u0423\u041a\u0418": scalar_to_text(row.get("barcode_sht")),
                        "\u0421\u041b\u0423\u0416_\u0428\u041a_\u0411\u041b\u041e\u041a\u0410": scalar_to_text(row.get("barcode_bl")),
                        "\u0421\u041b\u0423\u0416_\u0428\u041a_\u041a\u041e\u0420\u041e\u0411": scalar_to_text(row.get("barcode_kor")),
                    },
                )
            )
        blocks.append(LegacyBlock("END", {"lines_count_must_be": str(len(rows))}))
        return blocks

    def get_place_items(self, place_id: str) -> list[LegacyBlock]:
        try:
            rows = self.gateway.fetch_all(
                """
                select UL_CPROIN UID1,
                       sum(UL_NQTUVC) QTY1,
                       AR_LIBPRO NAME1,
                       UE_ADRUMS ADDRESS1,
                       sfera_ean.SHT_IN_BL,
                       sfera_ean.BL_IN_KOR,
                       sfera_ean.EAN_SHT,
                       sfera_ean.EAN_BL,
                       sfera_ean.EAN_KOR
                  from refstock.TB_LCUMS
                  left join refstock.TB_EUMS on ue_usscc = ul_usscc and UE_DEPOT = 01 and UE_PROPRI = 'RM'
                  left join refstock.TB_ART on AR_CPROIN = UL_CPROIN and AR_donord = 'RM'
                  left join refstock.tb_traums on ue_usscc = ut_usscc and ul_numlig = ut_numlig
                  left join RABAEV.SFERA_EAN sfera_ean on UL_CPROIN = sfera_ean.TMC_UID and manualenter = 'N'
                 where ul_donord = 'RM'
                   and ul_numorl is null
                   and UE_ADRUMS = :place_id
                   and ul_nqtuvc <> 0
                 group by UL_CPROIN,
                          AR_LIBPRO,
                          UE_ADRUMS,
                          sfera_ean.EAN_SHT,
                          sfera_ean.EAN_BL,
                          sfera_ean.EAN_KOR,
                          sfera_ean.SHT_IN_BL,
                          sfera_ean.BL_IN_KOR
                """,
                {"place_id": place_id},
            )
        except Exception as exc:
            if "ORA-00942" not in str(exc):
                raise
            rows = self.gateway.fetch_all(
                """
                select ACTICUL UID1,
                       NORMA_UKLADKI QTY1,
                       NAME NAME1,
                       CELL ADDRESS1,
                       COUNT_SHT_IN_BL SHT_IN_BL,
                       round(COUNT_SHT_IN_KOR / nullif(COUNT_SHT_IN_BL, 0), 0) BL_IN_KOR,
                       BARCODE_SHT EAN_SHT,
                       BARCODE_BL EAN_BL,
                       BARCODE_KOR EAN_KOR
                  from RABAEV.RRL_ARTICULS
                 where CELL = :place_id
                 order by ACTICUL
                """,
                {"place_id": place_id},
            )
        blocks = [LegacyBlock("PLACE_LINES", {"lines_count_must_be": str(len(rows))})]
        for pos, row in enumerate(rows, start=1):
            blocks.append(
                LegacyBlock(
                    "PL",
                    {
                        "\u041f\u041f": str(pos),
                        UID_KEY: scalar_to_text(row.get("uid1")),
                        QTY_KEY: scalar_to_text(row.get("qty1")),
                        "\u041d\u0410\u0418\u041c": scalar_to_text(row.get("name1")),
                        "\u0421\u041b\u0423\u0416_\u0410\u0414\u0420": scalar_to_text(row.get("address1")),
                        "\u0421\u041b\u0423\u0416_\u0428\u0422\u0412\u0411\u041b": scalar_to_text(row.get("sht_in_bl")),
                        "\u0421\u041b\u0423\u0416_\u0411\u041b\u0412\u041a\u041e\u0420": scalar_to_text(row.get("bl_in_kor")),
                        "\u0421\u041b\u0423\u0416_\u0428\u041a_\u0428\u0422\u0423\u041a\u0418": scalar_to_text(row.get("ean_sht")),
                        "\u0421\u041b\u0423\u0416_\u0428\u041a_\u0411\u041b\u041e\u041a\u0410": scalar_to_text(row.get("ean_bl")),
                        "\u0421\u041b\u0423\u0416_\u0428\u041a_\u041a\u041e\u0420\u041e\u0411": scalar_to_text(row.get("ean_kor")),
                    },
                )
            )
        blocks.append(LegacyBlock("END", {"lines_count_must_be": str(len(rows))}))
        return blocks

    def confirm_lot_check(self, usscc: str, request: LotCheckRequest) -> None:
        usscc = normalize_pallet_identifier(usscc)
        statements: list[tuple[str, dict[str, Any]]] = [
            ("delete from LOT_AUDIT where SSCC = :usscc", {"usscc": usscc}),
            ("delete from LOT_AUDIT_ERROR_LINES where SSCC = :usscc", {"usscc": usscc}),
        ]
        condition = PICK_ZONE

        if request.error_count == 0:
            statements.append(
                (
                    """
                    declare
                      v_ret varchar2(50);
                    begin
                      v_ret := RABAEV.RRL_SET_SCAN_PROOVE2(
                        PALLET_UID1 => :usscc,
                        count_of_errors1 => :error_count,
                        prim1 => '',
                        SBORSHIK1 => :user_id,
                        KLADOVSHIK1 => ''
                      );
                    end;
                    """,
                    {"usscc": usscc, "error_count": request.error_count, "user_id": request.user_id},
                )
            )

        for item in request.errors:
            if item.condition == SHORTAGE:
                condition = ERROR_ZONE
            statements.append(
                (
                    """
                    update RABAEV.RRL_SBORKA_PALLET_ROWS
                       set SOBRANO = :qty
                     where PALLET_UID = :usscc
                       and ARTICUL = :uid
                    """,
                    {"qty": item.qty, "usscc": item.usscc or usscc, "uid": item.uid},
                )
            )

        for item in request.vp_lines:
            statements.append(
                (
                    """
                    update RABAEV.RRL_SBORKA_PALLET_ROWS
                       set TIME_OF_CHECKING = to_date(:checked_at, 'dd.mm.yyyy HH24:MI:ss')
                     where PALLET_UID = :pallet_uid
                       and ARTICUL = :uid
                    """,
                    {"checked_at": str(item.checked_at), "pallet_uid": item.pallet_uid, "uid": item.uid},
                )
            )

        statements.append(
            (
                "insert into LOT_AUDIT (SSCC, CONDITION) values (:usscc, :condition)",
                {"usscc": usscc, "condition": condition},
            )
        )
        self.gateway.execute_many(statements)

    def confirm_place_check(self, request: PlaceCheckRequest) -> None:
        statements: list[tuple[str, dict[str, Any]]] = [
            ("delete from RABAEV.PLACE_AUDIT where PALLETID = :pallet_id", {"pallet_id": request.pallet_id}),
            (
                "delete from RABAEV.PLACE_AUDIT_ERROR_LINES where PALLETID = :pallet_id",
                {"pallet_id": request.pallet_id},
            ),
            (
                "delete from RABAEV.INVENTORY_LINE_PALLET_AUDIT where PALLETID = :pallet_id",
                {"pallet_id": request.pallet_id},
            ),
        ]
        condition = MATCHED
        for item in request.errors:
            if item.condition == EXCESS:
                condition = EXCESS
            statements.append(
                (
                    """
                    insert into RABAEV.PLACE_AUDIT_ERROR_LINES
                      (PALLETID, CONDITION, unit_count, UID1, EAN)
                    values
                      (:pallet_id, :condition, :qty, :uid, :ean)
                    """,
                    {
                        "pallet_id": request.pallet_id,
                        "condition": item.condition,
                        "qty": item.qty,
                        "uid": item.uid,
                        "ean": item.ean,
                    },
                )
            )
        for item in request.inventory_lines:
            statements.append(
                (
                    f"""
                    insert into RABAEV.INVENTORY_LINE_PALLET_AUDIT
                      ({UID_KEY}, {QTY_KEY}, PALLETID, USER_ID, \u0414\u0410\u0422\u0410\u0421\u041e\u0417\u0414\u0410\u041d\u0418\u042f)
                    values
                      (:uid, :qty, :pallet_id, :user_id, sysdate)
                    """,
                    {"uid": item.uid, "qty": item.qty, "pallet_id": item.pallet_id, "user_id": item.user_id},
                )
            )
        statements.append(
            (
                "insert into RABAEV.PLACE_AUDIT (PALLETID, CONDITION) values (:pallet_id, :condition)",
                {"pallet_id": request.pallet_id, "condition": condition},
            )
        )
        self.gateway.execute_many(statements)

    def confirm_order_check(self, request: OrderCheckRequest) -> dict[str, str]:
        statements: list[tuple[str, dict[str, Any]]] = [
            ("delete from RABAEV.ORDER_AUDIT where ORDER_NUMBER = :order_no", {"order_no": request.order}),
            (
                "delete from RABAEV.ORDER_AUDIT_ERROR_LINES where ORDER_NUMBER = :order_no",
                {"order_no": request.order},
            ),
        ]
        condition = PICK_ZONE
        for item in request.errors:
            if item.condition == SHORTAGE:
                condition = ERROR_ZONE
            statements.append(
                (
                    """
                    insert into RABAEV.ORDER_AUDIT_ERROR_LINES
                      (ORDER_NUMBER, CONDITION, unit_count, UID1, EAN)
                    values
                      (:order_no, :condition, :qty, :uid, :ean)
                    """,
                    {
                        "order_no": request.order,
                        "condition": item.condition,
                        "qty": item.qty,
                        "uid": item.uid,
                        "ean": item.ean,
                    },
                )
            )
        statements.append(
            (
                "insert into RABAEV.ORDER_AUDIT (ORDER_NUMBER, CONDITION) values (:order_no, :condition)",
                {"order_no": request.order, "condition": condition},
            )
        )
        self.gateway.execute_many(statements)
        return {"oracle_status": "ok", "access_mdb_status": "not_implemented"}

    def call_spf(self, request: CallSpfRequest) -> str:
        name = request.spf_name.strip()
        name_upper = name.upper()
        if name_upper not in CALL_SPF_ALLOWLIST:
            raise ValueError(f"Stored procedure is not allowlisted: {name}")

        params = {key: value for key, value in request.params.items() if key != "SPF_NAME"}
        return self.gateway.call_varchar_function(name_upper, params)

    def _lot_check_from_legacy(self, blocks: list[LegacyBlock]) -> LotCheckRequest:
        head = blocks[0]
        errors = []
        vp_lines = []
        for block in blocks[1:]:
            if block.function_name == "ERROR_LOT_LINE":
                errors.append(
                    {
                        "usscc": block.get("USSCC"),
                        "uid": block.get(UID_KEY),
                        "qty": float(block.get(QTY_KEY, "0") or 0),
                        "plan_qty": float(block.get(PLAN_QTY_KEY, "0") or 0),
                        "condition": block.get(TYPE_KEY),
                        "ean": block.get(EAN_KEY),
                    }
                )
            if block.function_name == "VP":
                vp_lines.append(
                    {
                        "pallet_uid": block.get("PALLET_UID"),
                        "uid": block.get(UID_KEY),
                        "checked_at": block.get("TIME"),
                    }
                )
        return LotCheckRequest(
            user_id=head.get("USER_ID"),
            error_count=int(head.get("error_count", "0") or 0),
            errors=errors,
            vp_lines=vp_lines,
        )

    def _place_check_from_legacy(self, blocks: list[LegacyBlock]) -> PlaceCheckRequest:
        head = blocks[0]
        errors = []
        inventory_lines = []
        for block in blocks[1:]:
            if block.function_name == "ERROR_PALLET_CHECK_LINE":
                errors.append(
                    {
                        "uid": block.get(UID_KEY),
                        "qty": float(block.get(QTY_KEY, "0") or 0),
                        "condition": block.get(TYPE_KEY),
                        "ean": block.get(EAN_KEY),
                    }
                )
            if block.function_name == "INVENTORY_LINE_PALLET_AUDIT":
                inventory_lines.append(
                    {
                        "uid": block.get(UID_KEY),
                        "qty": float(block.get(QTY_KEY, "0") or 0),
                        "pallet_id": block.get("PALLETID"),
                        "user_id": block.get("USER_ID"),
                    }
                )
        return PlaceCheckRequest(pallet_id=head.get("PALLETID"), errors=errors, inventory_lines=inventory_lines)

    def _order_check_from_legacy(self, blocks: list[LegacyBlock]) -> OrderCheckRequest:
        head = blocks[0]
        errors = []
        for block in blocks[1:]:
            if block.function_name == "ERROR_LOT_LINE":
                errors.append(
                    {
                        "usscc": block.get("USSCC"),
                        "uid": block.get(UID_KEY),
                        "qty": float(block.get(QTY_KEY, "0") or 0),
                        "plan_qty": float(block.get(PLAN_QTY_KEY, "0") or 0),
                        "condition": block.get(TYPE_KEY),
                        "ean": block.get(EAN_KEY),
                    }
                )
        return OrderCheckRequest(order=head.get("ORDER"), errors=errors)
