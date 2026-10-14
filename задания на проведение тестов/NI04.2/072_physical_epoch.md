# Qwen072: physical stock epoch
Own private business warehouse, P/H changes only root.
1. scripts/ni042_physical_epoch_case.py: birth physical1, HARD/release same physical epoch, P6→P5 newer2→3, protected direct epoch rewrite, cleanup0.
2. Two sessions sameUID count/reserve/move: exact stock optimistic version, no lost delta; independent UID parallel. Counter change follows actual P exactly once per existing balance row update.
3. Marked replacement at sameP: physical unit signature changes; additional regulatory profiles do not multiply quantity.
4. Root rollback leaves counter/P/H/units/journal/outbox unchanged. Exact replay does not advance counter again.
5. Old rows0 only starting version, no historical assertion. Dependent073/active measured claims forbid rollback. No full NI04.2 acceptance yet.
6. Longest SQL keyed bounded access; no changing-counter index without evidence.
