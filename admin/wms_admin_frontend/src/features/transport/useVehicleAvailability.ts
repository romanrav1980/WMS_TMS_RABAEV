import { useEffect, useRef, useState } from "react";
import { apiFetch } from "../../api";

export type VehicleAvail = {
  vehicle_id: number;
  vehicle_num: string;
  vehicle_type: string;
  marka: string;
  max_pallets: number;
  gidrobort: boolean;
  free_at: string | null;
  delay_min: number;
  status: "green" | "yellow" | "red";
  detail: string;
};

/** Доступность машин на дату/время; игнорирует запоздалые ответы от прежних даты/времени. */
export function useVehicleAvailability(shipDate: string | null, shipTime: string, pallets: number): {
  avail: VehicleAvail[];
  availLoading: boolean;
  availError: string | null;
} {
  const [avail, setAvail] = useState<VehicleAvail[]>([]);
  const [availLoading, setAvailLoading] = useState(false);
  const [availError, setAvailError] = useState<string | null>(null);
  const reqRef = useRef(0);

  useEffect(() => {
    if (!shipDate || !shipTime) { setAvail([]); setAvailError(null); return; }
    const req = ++reqRef.current;
    setAvailLoading(true);
    setAvailError(null);
    apiFetch<VehicleAvail[]>(
      `/api/admin/transport/vehicles/available?shipment_time=${shipDate}+${shipTime}&pallets=${pallets}`
    )
      .then(list => { if (req === reqRef.current) { setAvail(list); setAvailError(null); } })
      .catch(() => { if (req === reqRef.current) { setAvail([]); setAvailError("Доступность машин не загружена. Проверьте соединение и повторите."); } })
      .finally(() => { if (req === reqRef.current) setAvailLoading(false); });
    return () => { if (req === reqRef.current) reqRef.current++; };
  }, [shipDate, shipTime, pallets]);

  return { avail, availLoading, availError };
}
