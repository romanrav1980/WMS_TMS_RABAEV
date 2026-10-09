"""Versioned physical identities; full scans remain separate from canonical keys."""
import re


def canonical_mark(system: str, profile: str, raw: str, expected_gtin: str | None = None) -> dict[str, str | None]:
    value = raw
    for prefix in ("]d2", "]d1", "]Q3", "]Q1", "]C1", "]C0", "]L0", "]L1", "]L2"):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    if system == "CRPT":
        tobacco = profile.upper() in {"TOBACCO", "CRPT_TOBACCO", "TOBACCO_PACK"}
        if tobacco and len(value) >= 21 and value[:14].isdigit() and (value[:14]==expected_gtin or not (value.startswith("01") and value[16:18] == "21")):
            gtin, serial = value[:14], value[14:21]
            identity = gtin + serial
        else:
            human = re.fullmatch(r"\(01\)([0-9]{14})\(21\)([^()\x00-\x20]{1,20})(?:\((?:91|92|93)\).*)?", value)
            if human:
                gtin, serial = human.group(1), human.group(2)
            elif value.startswith("01") and value[2:16].isdigit() and value[16:18] == "21":
                gtin = value[2:16]
                serial = value[18:].split("\x1d", 1)[0]
                if tobacco:
                    serial = serial[:7]
            else:
                raise ValueError("CRPT scan must contain GTIN and unique serial, not a product barcode")
            identity = gtin + serial if tobacco else "01" + gtin + "21" + serial
        if not 1 <= len(serial) <= 20 or (tobacco and len(serial) != 7) or any(not 33 <= ord(c) <= 126 for c in serial):
            raise ValueError("Invalid or ambiguous CRPT serial; scanner must preserve GS separators")
        if re.fullmatch(r"[0-9]{14}", gtin) is None:
            raise ValueError("GTIN must contain 14 ASCII digits")
        check = (10 - sum(int(n) * (3 if i % 2 == 0 else 1) for i, n in enumerate(reversed(gtin[:-1]))) % 10) % 10
        if check != int(gtin[-1]):
            raise ValueError("CRPT GTIN check digit is invalid")
        return {"identity": identity, "gtin": gtin, "serial": serial}
    if system == "EGAIS" and (len(value) not in {68, 150} or any(not 33 <= ord(c) <= 126 for c in value)):
        raise ValueError("EGAIS profile expects a complete 68/150-character unique excise code")
    if not value or len(value.encode()) > 4000 or "\x00" in value:
        raise ValueError("Invalid unique marking code")
    return {"identity": value, "gtin": None, "serial": None}
