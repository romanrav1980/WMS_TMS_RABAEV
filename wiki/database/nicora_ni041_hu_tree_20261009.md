# NI04.1: первые складские связи вложенности

050 APPLIED в RABAEV/orcl. RRL_STOCK_HU_READ/HU_CMD, balance/closure/eligibility/root и новые guards VALID. [[nicora_ni041_hu_design_20261009]].

RRL_PALLETS получает HU_KIND/TYPE/CONTENT_VERSION/CURRENT_CELL/TARE_WEIGHT_KG. Container identity использует прежний UID, ARTICUL=NULL, UNIT_COUNT=0 и не имеет количественного остатка. Optional SSCC проверяется по GS1 checksum; internal UID допустим. RRL_WMS_HU_LINK — current single parent плюс immutable unlink history/root operation. FK защищают existing pallet/CASE identities, unique active parent indexes не допускают двойного владельца.

HU_CREATE/ATTACH/DETACH через единое ядро: физический scan, одинаковый фактический адрес, expected parent/child versions, полный parent/child/ancestor snapshot и ordered anchors. Циклы/глубина>16/>200nodes отвергаются. Attach/unpack не изменяют P/H. Изменение subtree повышает версии родителей/ancestors; stock leaf сохраняет свой физический запас и BASE.

Общий stock closure теперь включает HU ancestors/link rows. Eligibility исключает nested source до unpack. Balance core запрещает отдельное изменение P вложенного листа; HARD освобождается через прежнюю команду. Root HU_MOVE зарезервирован для полного переноса дерева; на050 ещё не установлен. Regulatory CRPT aggregation и CASE→lot не переписываются.

Адресный реальный case: leaf P/H5/2 → BOX → TOP, parent quantitative rows0, leaf counted once, exact create/attach replay; встречный attach cycle и другой parent denied; inventory alteration nested5→4 denied unchanged. Explicit unpack, release/count собственного stock выполнены через root, link/operation history сохранена.

SQL snapshot3uwrpkb9x39z1 ~3.52ms/12: решение inventory — bounded200nodes/16depth, existing UID and new parent/active indexes; масштаб не утверждён. CASE attachment и складское движение/slot limits ещё открыты; полный NI04.1 не завершён.
