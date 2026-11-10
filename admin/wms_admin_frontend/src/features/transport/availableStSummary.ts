export type AvailableStSummaryItem = {
  ST_NUMBER: string;
  PALLETS_COUNT: number;
  WEIGHT_KG: number;
  VOLUME_M3: number | null;
};

export type AvailableStSummary<T extends AvailableStSummaryItem> = {
  rows: T[];
  pallets: number;
  weight: number;
  volume: number;
};

export function summarizeAvailableSts<T extends AvailableStSummaryItem>(
  rows: T[],
  selected?: ReadonlySet<string>,
): AvailableStSummary<T> {
  let pallets = 0, weight = 0, volume = 0;
  const selectedRows: T[] = [];
  for (const row of rows) {
    if (selected && !selected.has(row.ST_NUMBER)) continue;
    selectedRows.push(row);
    pallets += row.PALLETS_COUNT || 0;
    weight += row.WEIGHT_KG || 0;
    volume += row.VOLUME_M3 || 0;
  }
  return { rows: selectedRows, pallets, weight, volume };
}
