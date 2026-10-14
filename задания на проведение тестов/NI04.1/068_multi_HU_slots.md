# Qwen068: несколько HU в ячейке
Отдельные business warehouse/fixtures; не менять общие stock/историю.
1. scripts/ni041_multi_hu_slot_case.py: real tasks, planned50+51 exceeds100, same planned slot denied, distinct50+50 equality succeeds; P10/H2/claims100kg3m3/exact replay; own root cleanup.
2. Два соединения одновременно планируют разные slots при нехватке общей capacity: нельзя превысить CELL/topology mass/volume. Duplicate target slot одним победителем.
3. Occupied claim/version stale, unknown SI, orphan stock, other ordinary receipt claim, unmeasured arrival — explicit refusal/P/H unchanged.
4. Blocks/temp/height SI/current published topology and stale slot version after replanning.
5. Move out frees only own claim, others retained; cancellation releases only own incoming load; immutable measurements reject direct DML.
6. Same-cell transfer/slotted unpack остаются pending; не ставить весь NI04.1 DONE.
7. API/ARM distinct free slot visible, actual server gate handles capacity/coverage. Longest SQL and explicit batching/index/cache/backlog decision.
