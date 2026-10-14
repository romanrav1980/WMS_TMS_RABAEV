from pathlib import Path
import json
out={}
p=Path("wiki/index.md");s=p.read_text(encoding="utf-8-sig");s="- [Тара погруженного места](database/retailcase_ni063_booked_handover_20261010.md):102 APPLIED, exact actual root load/booked claim/driver accept, warehouse0 vehicle1, goods not repeated.\n"+s;out["wiki/index.updated.tmp"]=s
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\n2026-10-10:102 actual cargo tare handover joins existing Root loading, no ST duplication; dedicated driver accept/replay TRANSFERRED, warehouse0 vehicle1/no goods event. Warehouse selection UI and source manifest updated. Obsolete direct ST writer assertion removed after successful business case.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_3.md");out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nTicket102: [передача закреплённой тары](../../../../database/retailcase_ni063_booked_handover_20261010.md), exact existing root loading/immutable offer association/current driver accept. Standalone FULLPAL/repack/shortage remain open.\n"
p=Path("задания на проведения тестов/NI06.3/102_передача_закрепленной_тары.md")
out[str(p)]="""# Qwen — NI06.3,102
Проверить текущие исходники102, прежние101/098, фактическую нагрузку существующего TT. Не запускать повторно одноразовый author-case и не очищать общие данные.
Новый собственный fixture: верхний HU с двумя вложенными товарными местами; один BOOK, фактическая штатная погрузка, OFFER с выбранным claim, иной текущий водитель ACCEPT. Должно быть warehouse-1/vehicle+1, claim TRANSFERRED, original load FK, один outbox и отсутствие второго goods event.
Непогруженный/дочерний/чужой склад/тип/рейс/автомобиль, quantity меньше claims, повтор claim другой передачей, два конкурирующих ACCEPT: отказ без частичного эффекта. Exact replay возвращает оригинал; новый payload того же ID отказ.
UI: после смены склада/типа/рейса прежний выбор исчезает; неясный ответ повторяется исходным intent. Старый OFFER без booking IDs сохраняет canonical replay.
Проанализировать самый длинный SQL этого ограниченного случая и оформить решение. Не объявлять всё NI06.3 принятым по одному случаю.
"""
print(json.dumps(out,ensure_ascii=True))
