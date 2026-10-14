def normalize_incoming_sscc(value: object) -> object:
    if not isinstance(value, str):
        return value
    if value.startswith("]C1"):
        value = value[3:]
    if value.startswith("(00)") and len(value) == 22 and value[4:].isdigit():
        return value[4:]
    if value.startswith("00") and len(value) == 20 and value[2:].isdigit():
        return value[2:]
    return value



def normalize_receipt_identifier(value: object) -> str:
    from .regulatory_pallet import sscc_value
    value=normalize_incoming_sscc(value)
    if not isinstance(value,str) or not value or len(value)>50 or len(value.encode("utf-8"))>150:
        raise ValueError("Pallet identifier must fit 50 characters and 150 UTF-8 bytes")
    if not value.isprintable() or any(character.isspace() for character in value):
        raise ValueError("Pallet identifier must contain visible non-space characters")
    if len(value)==18 and value.isascii() and value.isdigit() and sscc_value(value) is None:
        raise ValueError("Invalid SSCC check digit")
    return value
