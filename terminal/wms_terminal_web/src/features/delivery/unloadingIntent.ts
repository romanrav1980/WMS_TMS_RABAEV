import type { UnloadingStartBody } from "./contracts";

export type UnloadingControl = { operation_id: string; original: UnloadingStartBody; reason: string };
export type UnloadingPending = { body: UnloadingStartBody; confirmedRejection?: boolean; abandon?: UnloadingControl };

export function validUnloadingControl(value: UnloadingPending): boolean {
 if (value.abandon === undefined) return true;
 const control = value.abandon;
 return !!control && typeof control.operation_id === "string" && /^[A-Za-z0-9_.:-]{1,100}$/.test(control.operation_id)
  && control.operation_id !== value.body.operation_id && typeof control.reason === "string" && control.reason.trim().length >= 8
  && control.reason.length <= 500 && JSON.stringify(control.original) === JSON.stringify(value.body)
  && Object.keys(control).sort().join(",") === "operation_id,original,reason";
}
