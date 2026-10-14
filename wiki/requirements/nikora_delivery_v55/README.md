Входная страница: [NICORA — описание, исходники и последние изменения](../../subprojects/nicora.md).

# NICORA: доработка существующих WMS/TMS

**Revision 54, 13.10.2026.** [8 направлений / 18 функциональных спринтов](implementation_plan.md), [состав JSON](implementation_plan.json). Текущий — [NI02.2](execution/active/ni02_2.md).

[Stock core переключён](../../database/nicora_stock_posting_cutover_20261009.md): RABAEV/orcl ACTIVE, B0, compatibility OFF, 25 ADAPTED / 6 RETIRED / 0 UNCONVERTED. Это закрытый технический этап, не закрытие всех бизнес-процессов NICORA.

[Каталог 68 NS](sprint_plan.md), [исполнение](execution/README.md), [363 сценария](execution/execution_plan.json) и [маркировка](track_trace_coverage.md) сохранены. [Общее ТЗ](../nikora_business_processes/README.md) остаётся редакцией 57; пересмотр уточняет реализацию, не отменяет требования.

Готовые проводка/приёмка/CASE/QC/назначение рейсов переиспользуются. Минимум 80% ресурсов на функционал; адресные проверки изменения, большие load/recovery/пилоты отдельно. Сроки не измерены. RABAEV и существующая среда сохраняются; ТМС-2 имеет отдельную очередь.

[Шаблон ticket](task_template.md). GitHub только по свежему поручению: эта редакция сохранена локально.

09.10.2026: NI03.1 реализован и подтверждён адресными случаями; [evidence](../../database/nicora_ni031_stock_eligibility_20261009.md). Осталось 17 из 18 спринтов; общий architecture debt и независимая приёмка не закрыты.

13.10.2026: самостоятельная автоподготовкаNI02.1 через прежние writers, physicalCASE→QC и UIпереход к existingassignment delivered dev/report30–32. Полная независимая приёмка/внешний ACK/все18спринтов не закрыты.
