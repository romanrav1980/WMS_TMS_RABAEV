export type NormalizedIdentifier = {
  raw: string;
  value: string;
  kind: "sscc" | "legacy";
  changed: boolean;
};

export function normalizePalletIdentifier(input: string): NormalizedIdentifier {
  const raw = input.trim();
  let value = raw;

  if (value.startsWith("]C1") || value.startsWith("]d2")) {
    value = value.slice(3);
  }

  const compact = value.replace(/[\s-]/g, "");
  const withParenthesizedAi = compact.match(/^\(00\)(\d{18})$/);
  if (withParenthesizedAi) {
    return { raw, value: withParenthesizedAi[1], kind: "sscc", changed: raw !== withParenthesizedAi[1] };
  }

  const withAi = compact.match(/^00(\d{18})$/);
  if (withAi) {
    return { raw, value: withAi[1], kind: "sscc", changed: raw !== withAi[1] };
  }

  if (/^\d{18}$/.test(compact)) {
    return { raw, value: compact, kind: "sscc", changed: raw !== compact };
  }

  return { raw, value: raw, kind: "legacy", changed: false };
}

export function getPalletIdentifierLabel(identifier: NormalizedIdentifier): string {
  if (identifier.kind === "sscc") return `SSCC ${identifier.value}`;
  return identifier.value;
}
