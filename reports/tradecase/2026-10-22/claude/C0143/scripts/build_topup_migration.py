"""Build the shared-object patches of 2026-10-22_trade_topup_proposal from exact current USER_SOURCE dumps.

usage: python build_topup_migration.py <dump_dir>
Writes before_*.sql (rollback sources) and 005..008 patched objects into the migration folder. Each patch is a
single exact-match insertion; a missing anchor aborts the build (drift must be reviewed, not guessed).
"""
import pathlib
import sys

MIGRATION = pathlib.Path(r"C:\projects\TMS\db\migrations\2026-10-22_trade_topup_proposal")
dump = pathlib.Path(sys.argv[1])
KINDS = "('TRADE_TOPUP_CONFIRM','TRADE_TOPUP_RELEASE')"


def source(name: str, kind: str) -> str:
    text = (dump / f"{name}.{kind}.sql").read_text(encoding="utf-8")
    return text.rstrip() + "\n"


def ddl(text: str) -> str:
    return "create or replace " + text.lstrip() + "/\n"


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        sys.exit(f"anchor not unique/absent ({text.count(old)}): {old[:90]!r}")
    return text.replace(old, new)


def insert(text: str, anchor: str, addition: str, before: bool = True) -> str:
    return replace_once(text, anchor, addition + anchor if before else anchor + addition)


objects = {
    "005_posting_api.sql": ("RRL_STOCK_POSTING_API", "PACKAGE_BODY", [
        ("   elsif g_kind in('RESERVATION_CREATE',",
         f"   elsif g_kind in{KINDS} then RRL_TRADE_TOPUP_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n"),
        ("  elsif g_kind='RESERVATION_ALLOCATE_POOL' then RRL_STOCK_POOL_CMD.execute_command(",
         f"  elsif g_kind in{KINDS} then RRL_TRADE_TOPUP_CMD.execute_command(g_request,g_actor,p_result);\n"),
    ]),
    "006_trade_guard.sql": ("RRL_TRADE_STOCK_GUARD", "PACKAGE_BODY", [
        ("'WAVE_CANCEL','WAVE_RELEASE')then", None),
    ]),
    "007_pick_context.sql": ("RRL_TRADE_PICK_CONTEXT", "PACKAGE_BODY", [
        ("  if not g_valid or p_ware<>g_ware then return 'TRADE_ORDER_BINDING_STALE';end if;\n",
         "  -- A SAP top-up order whose boxes are still held by its proposal must be taken over atomically, not reserved twice.\n"
         "  select count(*)into n from RRL_TRADE_ORDER_LINK tl join RRL_TRADE_TOPUP_PROPOSAL tp on tp.WARE_ID=tl.WARE_ID and tp.SAP_ORDER_ID=tl.EXTERNAL_ID\n"
         "   join RRL_TRADE_TOPUP_HOLD th on th.PROPOSAL_ID=tp.PROPOSAL_ID and th.STATUS='ACTIVE'where tl.CUSTOMER_ORDER_ID=g_line.CUSTOMER_ORDER_ID;\n"
         "  if n>0 then return 'TRADE_TOPUP_HOLD_ADOPTION_REQUIRED';end if;\n"),
    ]),
    "008_core_access.sql": None,
}

# 005-007: body patches
for file, spec in objects.items():
    if spec is None:
        continue
    name, kind, edits = spec
    text = source(name, kind)
    (MIGRATION / f"before_{name.lower()}.sql").write_text(ddl(text), encoding="utf-8", newline="")
    for anchor, addition in edits:
        if name == "RRL_TRADE_STOCK_GUARD":
            # The command checks owner/eligibility itself; the guard's owner-write loop still runs for every touched pallet.
            text = replace_once(text, anchor, "'WAVE_CANCEL','WAVE_RELEASE','TRADE_TOPUP_CONFIRM','TRADE_TOPUP_RELEASE')then")
        else:
            text = insert(text, anchor, addition, before=name != "RRL_TRADE_PICK_CONTEXT")
    (MIGRATION / file).write_text(ddl(text), encoding="utf-8", newline="")

# 008: ACCESSIBLE BY of the two native owners of quantity and physical units gains RRL_TRADE_TOPUP_CMD only.
parts = []
for name, anchor in (("RRL_STOCK_RESERVE_CORE", " accessible by(package RRL_STOCK_UNLOAD_CMD,"),
                     ("RRL_STOCK_UNIT_CORE", " accessible by(package RRL_STOCK_IW_RECOVERY_REC,")):
    text = source(name, "PACKAGE")
    (MIGRATION / f"before_{name.lower()}_spec.sql").write_text(ddl(text), encoding="utf-8", newline="")
    parts.append(ddl(replace_once(text, anchor, anchor.replace("accessible by(", "accessible by(package RRL_TRADE_TOPUP_CMD,"))))
(MIGRATION / "008_core_access.sql").write_text("".join(parts), encoding="utf-8", newline="")
print("built", sorted(p.name for p in MIGRATION.iterdir()))
