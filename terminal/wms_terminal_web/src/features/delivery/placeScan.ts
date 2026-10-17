/** Only a matched current preview can supply a canonical identifier for a NEW intent. */
export function matchedPlaceScan(raw: string, identifiers: readonly string[]): string | null {
 if (identifiers.includes(raw)) return raw;
 let value = raw.startsWith("]C1") ? raw.slice(3) : raw;
 if (/^\(00\)[0-9]{18}$/.test(value)) value = value.slice(4);
 else if (/^00[0-9]{18}$/.test(value)) value = value.slice(2);
 return identifiers.includes(value) ? value : null;
}
