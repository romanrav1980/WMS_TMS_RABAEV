from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/"admin/wms_admin_frontend/src/components/PlannerSchedule.tsx"
s=p.read_text(encoding="utf-8")
s+='''

export function transferPlannerStop(
  current: VrpRouteItem[], sourceRoute: number, sourceStop: number, destination: number,
): VrpRouteItem[] {
  const routes = current.map(route => ({ ...route, stops: [...route.stops] }));
  const [moved] = routes[sourceRoute].stops.splice(sourceStop, 1);
  routes[destination].stops.push(moved);
  for (const index of [sourceRoute, destination]) {
    const route = routes[index];
    invalidateSchedule(route);
    route.total_pallets = route.stops.reduce((sum, stop) => sum + stop.pallets, 0);
    route.total_kg = route.stops.reduce((sum, stop) => sum + stop.weight_kg, 0);
    route.utilization_pct = route.max_pallets > 0
      ? Math.round(route.total_pallets / route.max_pallets * 100) : 0;
  }
  return routes;
}
'''
p.write_text(s,encoding="utf-8")
p=root/"admin/wms_admin_frontend/src/components/TransportPlannerPage.tsx"
s=p.read_text(encoding="utf-8").replace('PlannerStopTime, invalidateSchedule,','PlannerStopTime, transferPlannerStop,')
a=s.index('    const routes = localRoutes.map(',s.index('  function handleDrop'))
b=s.index('    dragSrc.current = null;',a)
s=s[:a]+'    setLocalRoutes(transferPlannerStop(localRoutes, src.routeIdx, src.stopIdx, targetRouteIdx));\n'+s[b:]
p.write_text(s,encoding="utf-8")
