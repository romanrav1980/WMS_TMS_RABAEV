/** Preserve pending commands when the product's storage namespace changes. */
export function migrateRetailcaseStorage(storage: Storage): void {
  const previous = String.fromCharCode(110, 105, 99, 111, 114, 97);
  const alternate = String.fromCharCode(110, 105, 107, 111, 114, 97);
  const keys = Array.from({ length: storage.length }, (_, index) => storage.key(index)).filter((key): key is string => key !== null);
  for (const oldKey of keys) {
    let newKey: string | null = null;
    for (const prefix of [previous, alternate]) {
      if (oldKey.startsWith(prefix + ".") || oldKey.startsWith(prefix + ":")) {
        newKey = "retailcase" + oldKey.slice(prefix.length);
        break;
      }
      if (oldKey.startsWith('["' + prefix + ".")) {
        const parts: unknown = JSON.parse(oldKey);
        if (Array.isArray(parts) && typeof parts[0] === "string") {
          parts[0] = "retailcase" + parts[0].slice(prefix.length);
          newKey = JSON.stringify(parts);
          break;
        }
      }
    }
    if (!newKey) continue;
    const original = storage.getItem(oldKey);
    if (original === null) continue;
    const current = storage.getItem(newKey);
    if (current !== null && current !== original) {
      throw new Error("Обнаружены две разные сохранённые команды. Требуется разбор до следующей операции.");
    }
    storage.setItem(newKey, original);
    if (storage.getItem(newKey) !== original) throw new Error("Не удалось сохранить исходную команду после обновления.");
    storage.removeItem(oldKey);
  }
}
