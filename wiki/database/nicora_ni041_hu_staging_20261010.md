# NI04.1: целый CASE-HU в существующую зону контроля/экспедиции

057 implementation. Продолжение [[nicora_ni041_hu_case_20261010]]. Existing CASE_CARRIER_MOVE допускает системную ячейку для закрытого физического CASE. Whole HU adapter должен применять ту же политику для дерева, содержащего только закрытые CASE-листья, без обычного складского товара. Это размещение, не отгрузка и не допуск выезда.

Сохраняются warehouse/blocking/temp/empty-cell/weight/height/slot проверки. Системная ячейка не становится доступной планировщику обычного stock HU. Current cell/version CASE и parent вместе с P/H/units обновляются в одной проводке. Широкий перерасчёт маршрутов и второй staging движок не создаются.

057 APPLIED, RRL_STOCK_HU_SLOT VALID, checkpoint324. Native closed CASE12+8 under one roll cage reached a real system target20/H20 with owner/version/replay and explicit unpack/own return cleanup. Ordinary stock cannot enter a system target through this adapter. P/H effect and unit closure are the previous transfer core. Slot list for system physical slots and actual shipping/exit remain NI05 work; this does not declare a gate/door planning engine.
