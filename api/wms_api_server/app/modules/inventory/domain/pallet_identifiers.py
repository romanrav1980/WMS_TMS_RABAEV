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
