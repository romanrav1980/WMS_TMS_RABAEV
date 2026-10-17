import type { AssemblyContext, AssemblySession, AssemblyStation, FinalCaptureCandidate } from "./contracts";
const KEY_PATTERN = /^[A-F0-9]{64}$/;
export function extractFinalCandidates(data: unknown, session: AssemblySession, station: AssemblyStation | undefined, context: AssemblyContext): FinalCaptureCandidate[] {
  const list = Array.isArray(data) ? data : Array.isArray((data as {items?: unknown[]})?.items) ? (data as {items: unknown[]}).items : Array.isArray((data as {readings?: unknown[]})?.readings) ? (data as {readings: unknown[]}).readings : [];
  return list.filter((value): value is FinalCaptureCandidate => !!value && typeof value === "object" && typeof value.capture_key === "string" && KEY_PATTERN.test(value.capture_key))
    .filter(c => c.purpose === "FINAL_GROSS" && c.case_task_id === session.task_id && c.scan_container === session.scan_container
      && c.case_content_version === session.content_version && c.device_id === session.device_id && c.tare_capture_key === session.tare_capture_key
      && c.post_cell === session.post_cell && c.basis === "GROSS" && c.status === "ARCHIVED" && c.stock_posted === false
      && c.signature_domain === "ASM_FINAL" && c.composition_signature_version === 3 && context.final_signature_domain === "ASM_FINAL" && context.final_signature_version === 3
      && !!context.final_composition_signature && c.composition_signature === context.final_composition_signature
      && !!station && c.device_policy_version === station.device_policy_version && c.calibration_ref === station.calibration_ref && c.device_mode === station.device_mode
      && Number.isFinite(Date.parse(c.measured_at)) && Date.parse(c.measured_at) >= Date.now() - 120000 && Date.parse(c.measured_at) <= Date.now() + 2000);
}

