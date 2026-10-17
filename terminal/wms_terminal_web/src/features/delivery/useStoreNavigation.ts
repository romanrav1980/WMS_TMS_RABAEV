import { useEffect, useState } from "react";
import type { StoreSummary } from "./contracts";

function readRoute(stores: StoreSummary[]) {
 const match = location.hash.match(/^#\/store\/([^/]+)(?:\/delivery\/(.+))?$/);
 try {
  const requested = match ? decodeURIComponent(match[1]) : "";
  const storeId = stores.some(store => store.store_id === requested) ? requested : stores.length === 1 ? stores[0].store_id : null;
  return { storeId, load: match && storeId === requested && match[2] ? decodeURIComponent(match[2]) : null };
 } catch { return { storeId: null, load: null }; }
}
export function useStoreNavigation(stores: StoreSummary[]) {
 const [route, setRoute] = useState(() => readRoute(stores));
 useEffect(() => {
  const changed = () => setRoute(readRoute(stores));
  window.addEventListener("hashchange", changed);
  return () => window.removeEventListener("hashchange", changed);
 }, [stores]);
 function navigate(storeId: string | null, load: string | null = null) {
  location.hash = storeId ? "/store/" + encodeURIComponent(storeId) + (load ? "/delivery/" + encodeURIComponent(load) : "") : "";
  setRoute({ storeId, load });
 }
 return { ...route, navigate };
}
