import type { StoreMarkControl } from "../contracts";

export function MarkedGoodsSummary({ control }: { control: StoreMarkControl }) {
 const groups = new Map<string, { article: string; units: number; profiles: string[] }>();
 for (const unit of control.units || []) {
  if (!unit.lot_uid) continue;
  const group = groups.get(unit.lot_uid) || { article: unit.article || unit.lot_uid, units: 0, profiles: [] };
  group.units += 1;
  for (const profile of unit.profiles || []) {
   const label = profile.system_code + " / " + profile.profile_code + " · " + profile.profile_version;
   if (!group.profiles.includes(label)) group.profiles.push(label);
  }
  groups.set(unit.lot_uid, group);
 }
 if (!groups.size && !control.ordinary_lots?.length) return null;
 return <div className="store-app-marked-summary">
  {[...groups].map(([lot, group]) => <p key={lot}>
   {group.article} · партия {lot}: {group.units} единиц с уникальными кодами.
   {" "}Обязательные профили: {group.profiles.join("; ")}.
  </p>)}
  {control.ordinary_lots?.map((lot) => <p key={lot}>Партия {lot}: обычный товар, сверка по штрихкоду товара.</p>)}
 </div>;
}
