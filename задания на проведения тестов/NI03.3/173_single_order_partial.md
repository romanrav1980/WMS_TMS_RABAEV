#173: одна исходная строка4 → shipped3 + pending1

Source tmp/ni033_mixed173_fixture.json: wave404/order1931/row3416/plan1908/line1909/FULL1913/task840/CASE1039/PT1914/ST641322/FF83. source metadata synthetically prepared; actual native effects proven.

Не сбрасывать DONE/SHIPPED/CANCELLED ради повторения. scripts/ni033_single_order_mixed_case.py повторяет saved receipts. Проверить исходный ORDER_QTY4 и current line requested_base4/picked3/hard0/quantity1. FF83 SHIPPED3/MIXED173.SHIP сохраняется; root mixed finish не пишет повторную qty. CASE samePL/differentPT отменён, FULL done остаётся done.

Fresh first-time native rollback/concurrency подтверждены автором; для нового прогона создать изолированный source аналогичного состава с actual native stock, а не clone terminal fact rows. Explicit marked/nested/multiUOM variants остаются отдельными tests. Не считать local synthetic QC scans/weights аппаратным/государственным подтверждением.
