"""Frozen physical BOX identities, including measured small CASE containers."""
from decimal import Decimal


def physical_box_count(tree: dict, proofs: list[dict]) -> int:
    nodes = tree.get("nodes", [])
    if not 1 <= len(nodes) <= 200:
        raise ValueError("Состав грузового места превышает предел физических коробок")
    expected = {}
    for node in nodes:
        small = node.get("scale_qc") if node.get("kind") == "CASE" else None
        if node.get("kind") == "CONTAINER" and node.get("type") == "BOX" or small:
            if node["uid"] in expected:
                raise ValueError("Физическая коробка повторяется в составе")
            expected[node["uid"]] = node
    actual = {proof["box_uid"]: proof for proof in proofs}
    if len(actual) != len(proofs) or not expected or actual.keys() != expected.keys():
        raise ValueError("Нужен полный подтверждённый состав физических коробок")
    for uid, node in expected.items():
        proof = actual[uid]
        if proof["box_content_version"] != node["version"]:
            raise ValueError("Версия измеренной коробки не совпадает с архивом погрузки")
        small = node.get("scale_qc")
        if small:
            expected_origin = "MANUAL_CONFIRMED" if small.get("origin") == "MANUAL_CONFIRMED" else "WAREHOUSE_SCALE_QC"
            if proof["case_box_task_id"] != node["case_task_id"] or proof["measurement_origin"] != expected_origin or proof["coverage_complete"] != 1:
                raise ValueError("Малой таре нужен полный исходный весовой контроль")
            if expected_origin == "MANUAL_CONFIRMED" and (proof["final_scale_capture"] is not None or proof.get("device_mode") is not None):
                raise ValueError("Ручной контроль не является электронным замером")
            for field, source in [("final_scale_capture", "capture_key"), ("warehouse_qc_operation", "qc_operation_id"),
                                  ("signature_version", "signature_version"), ("measured_content_version", "measured_content_version")]:
                if proof[field] != small[source]:
                    raise ValueError("Исходное измерение малой тары не совпадает с архивом")
            for field in ["gross_weight_kg", "tare_weight_kg", "net_weight_kg"]:
                if Decimal(str(proof[field])) != Decimal(small[field]):
                    raise ValueError("Масса малой тары не совпадает с архивом")
    return len(expected)
