import { useEffect, useState } from "react";
import { HelpProvider } from "./help/HelpContext";
import { useStoreSession } from "./useStoreSession";
import { useStoreNavigation } from "./useStoreNavigation";
import { DeliveryScanner } from "./components/DeliveryScanner";
import { useStoreDeliveries } from "./useStoreDeliveries";
import { LoginScreen } from "./components/LoginScreen";
import { StoreSelector } from "./components/StoreSelector";
import { DeliveriesList } from "./components/DeliveriesList";
import { DeliveryDetail } from "./components/DeliveryDetail";
import type { StoreCredentials, StoreSession } from "./contracts";
import "./styles.css";

function StoreWorkspace({ credentials, session, onLogout }: { credentials: StoreCredentials; session: StoreSession; onLogout: () => void }) {
 const route = useStoreNavigation(session.stores);
 const [scanning, setScanning] = useState(false), [scanned, setScanned] = useState<{ load: string; code: string } | null>(null);
 const deliveries = useStoreDeliveries(route.storeId ?? "", credentials, onLogout);
 useEffect(() => { if (route.storeId && !route.load) void deliveries.load(); }, [route.storeId, route.load]);
 if (!route.storeId) return <StoreSelector stores={session.stores} hasMore={session.has_more} onSelect={id => route.navigate(id)} onLogout={onLogout} />;
 const store = session.stores.find(item => item.store_id === route.storeId);
 if (!store) return null;
 if (route.load) return <DeliveryDetail key={route.storeId + ":" + route.load} storeId={route.storeId} credentials={credentials} loadOperationId={route.load}
  initialScan={scanned?.load === route.load ? scanned.code : ""} onBack={() => route.navigate(route.storeId)} onAuthError={onLogout} />;
 return <>
  <DeliveriesList storeAddress={store.address} items={deliveries.items} busy={deliveries.busy} message={deliveries.message}
   hasMore={deliveries.hasMore} onOpen={load => route.navigate(route.storeId, load)} onRefresh={() => void deliveries.load()} onLoadMore={() => void deliveries.loadMore()}
   onScan={() => setScanning(true)} onBack={session.stores.length > 1 ? () => route.navigate(null) : null} onLogout={onLogout} />
  {scanning && <DeliveryScanner key={route.storeId} storeId={route.storeId} credentials={credentials} onClose={() => setScanning(false)} onAuthError={onLogout}
   onOpen={(load, code) => { setScanned({ load, code }); setScanning(false); route.navigate(route.storeId, load); }} />}
 </>;
}

export function StoreReceivingApp() {
 const sessionState = useStoreSession();
 return <HelpProvider key={sessionState.credentials?.username ?? "signed-out"} credentials={sessionState.credentials}>
  <div className="store-app-root">
   {!sessionState.credentials || !sessionState.session
    ? <LoginScreen busy={sessionState.busy} error={sessionState.error} onLogin={sessionState.login} />
    : <StoreWorkspace credentials={sessionState.credentials} session={sessionState.session} onLogout={sessionState.logout} />}
  </div>
 </HelpProvider>;
}
