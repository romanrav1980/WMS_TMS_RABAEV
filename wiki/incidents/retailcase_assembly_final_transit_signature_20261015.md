# Финальный вес сборки в служебной ячейке

15.10.2026, обнаружено в настоящем DEV сценарии1136 после1EA APPLIED и canonical close/bind. Состояние: WAIT_CONTROL/content3, boundST641520, child1/H1 в CPT_13583852; исходныйUID23/H0. Все количества согласованы, аппаратная приёмка не заявлена.

`RRL_STOCK_QC_GATE.status_json` возвращает SHIPMENT_OWN_PICKED_RESERVATION_INSUFFICIENT и не даёт composition_signature: shipping compiler исключает blocked-for-remains/replenishment cells, а CPT — штатная system cell с обоими флагами1. На момент обнаружения отбор/закрытие/привязка прошли, FINAL ещё не отправлялся. Предварительная проверка не доказала этот участок: private shipping/return compilers ACCESSIBLEBY owner не обходились.

Перемещение CASE меняет content version и не заменяет финальную проверку на исходном сборочном посту. Принятое решение (теперь APPLIED): отдельная версия ASM_FINAL content identity3 для собственного OPEN ASM session, текущего закрытого CASE/состава/резерва/привязки. Ordinary shipping QC/signature2 и запреты служебной ячейки сохраняются. Native finish должен сверять текущую ASM identity с captured identity; такая квитанция не является shipping QC approval. Owner integrations/inventory, исполнитель scale_protocol, root review/apply отдельно. Queue-owner ZERO делает rebase после этого forward, не перезаписывает тело.

[Фактический снимок](../../reports/retailcase/2026-10-15/assembly-scale/final-signature-blocker.json), [план компенсации](../../reports/retailcase/2026-10-15/assembly-scale/one-ea-commit-plan.json). До завершения/компенсации не объявлять весь весовой спринт закрытым. Direct quantity/state repairs не разрешены; возврат/снятие резервов только canonical owners.


Обновление: blocker устранён отдельным [[retailcase_assembly_final_snapshot_20261015|ASM_FINAL snapshot]]; root APPLIED10/0, независимый readback6 EXACT/errors0/INVALID0. Actual encrypted TEST OPC FINAL zero→1.5 принят с domain ASM_FINAL/version3/rawMATCHED, root native HTTP finish и exactrepeat FINALIZED. [FINAL](../../reports/retailcase/2026-10-15/warehouse-weigh-request/opc-final-native-http.json), [finish](../../reports/retailcase/2026-10-15/assembly-scale/finish-native-http.json). Ordinary shipping admission не расширялся; существующая SMALL_HU version3 сохранена, запрещён только explicit domain ASM_FINAL. Реальные весы/пилот не заявлены. OPEN policy mutation negatives не выполнены до финализации; прямого reset нет. Quantity scope остаётся ONE1EA, canonical компенсация и итоговые P24/H0 доказываются отдельно.

