# Qwen073 — физический состав и контроль
Проверять только собственный fixture через root, без прямого изменения P/H.
1. P5/H2/release: comp epoch сохраняется при H-only;6→5 даёт две новые версии.
2. CASE12/H12: PLAN, scan, weight, correction13→12; WAIT_CONTROL, обе stamps null, два CONTROL_REVOKED; старый scan не принимается, новый полный контроль разрешён.
3. Целый UID и верхний HU между ячейками, смена слота: QC неизменённого состава сохраняется; упаковка/вскрытие снимают QC.
4. Маркированный состав при том же количестве: замена physical member снимает QC; дополнительные regulatory profiles той же единицы не удваивают запас.
5. Две сессии QC/count: полный ресурсный closure, нет lost update/частично очищенных stamps. Exact replay не повышает epoch.
6. Проверить live VALID/долгие SQL/свои P=H=0. 073 rollback отказывает без удаления history.
Авторские scripts/ni042_composition_epoch_case.py и scripts/ni051_composition_epoch_case.py — исходный сценарий, не независимый результат.
