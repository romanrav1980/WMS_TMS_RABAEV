import { useEffect, useRef, useState } from "react";
import { initialDiscrepancyRows, initialPaperCountRows, paperCountComplete } from "./components/DiscrepancyFields";
import type { StorePreview, StoreDisposition, StoreUnitScan, StoreAggregateScan, UnloadingDetails } from "./contracts";
import { matchedPlaceScan } from "./placeScan";
import type { WeightSource } from "./manualWeight";

export function useReceiptForm(preview: StorePreview | null, initialScan = "") {
 const [step, setStep] = useState(0), [scanPlace, setScanPlace] = useState(initialScan), [beforeCameras, setBeforeCameras] = useState(false);
 const [unloading, setUnloading] = useState<UnloadingDetails>(), [unloadPending, setUnloadPending] = useState(false);
 const [scans, setScans] = useState<StoreUnitScan[]>([]), [aggregates, setAggregates] = useState<StoreAggregateScan[]>([]), [scanValid, setScanValid] = useState(true);
 const [captureKey, setCaptureKey] = useState(""), [photoIds, setPhotoIds] = useState<string[]>([]), [act, setAct] = useState(false);
 const [weightSource, setWeightSource] = useState<WeightSource>("MANUAL"), [manualKg, setManualKg] = useState<string | null>(null);
 const [paperReference, setPaperReference] = useState(""), [enabled, setEnabled] = useState(false), [note, setNote] = useState("");
 const [rows, setRows] = useState<StoreDisposition[]>([]), previous = useRef("");
 useEffect(() => {
  if (!preview) return;
  const key = preview.load_operation_id + ":" + preview.composition_signature;
  if (previous.current === key) return;
  previous.current = key;
  setStep(0); setScanPlace(initialScan); setBeforeCameras(false);
  if (!preview.requires_marked_recipient_flow) { setScans([]); setAggregates([]); setScanValid(true); }
  setCaptureKey(""); setManualKg(null); setWeightSource("MANUAL"); setPhotoIds([]); setAct(false); setPaperReference(""); setEnabled(false); setNote("");
  const leaves = preview.snapshot.nodes.filter(node => node.kind === "STOCK");
  setRows(preview.mode === "PAPER_COUNT" ? initialPaperCountRows(leaves) : initialDiscrepancyRows(leaves));
 }, [preview?.load_operation_id, preview?.composition_signature, initialScan]);
 const control = preview?.marked_unit_control;
 const marked = !preview?.requires_marked_recipient_flow || (!!control?.supported && scanValid
  && (aggregates.length > 0 || (!!preview.marked_partial_control ? scans.length <= (control.expected_scan_count ?? 0) : scans.length === control.expected_scan_count)));
 // Ровно один источник веса: введённый пользователем или измерение электронных весов (C0116).
 const weightValue = weightSource === "MANUAL" ? !!manualKg && !captureKey : !!captureKey && !manualKg;
 const weight = preview?.mode !== "WEIGHT_PHOTO" || (weightValue && photoIds.length >= 3 && !!preview.shipping_weight_tolerance_kg);
 const paper = preview?.mode !== "PAPER_COUNT" || (!!paperReference.trim() && paperCountComplete(rows, preview?.snapshot.nodes.filter(node => node.kind === "STOCK")));
 const commandScanPlace = preview ? matchedPlaceScan(scanPlace, [preview.root_scan_identifier, ...(preview.snapshot.nodes[0]?.kind !== "CASE" && preview.root_sscc ? [preview.root_sscc] : [])]) : null;
 const placeMatches = commandScanPlace !== null;
 const placeReady = placeMatches && beforeCameras && !unloadPending && (preview?.unloading?.status !== "STARTED" || !!unloading);
 const forceCounts = preview?.mode === "PAPER_COUNT" || (preview?.mode === "WEIGHT_PHOTO" && act);
 const hasDifferences = rows.some(row => [row.missing, row.refused, row.damaged, row.extra].some(value => /[1-9]/.test(value)));
 const countsReady = !(enabled || forceCounts) || (paperCountComplete(rows, preview?.snapshot.nodes.filter(node => node.kind === "STOCK")) && (!hasDifferences || !!note.trim()));
 return { step, setStep, scanPlace, setScanPlace, beforeCameras, setBeforeCameras, unloading, setUnloading, unloadPending, setUnloadPending,
  scans, setScans, aggregates, setAggregates, scanValid, setScanValid, captureKey, setCaptureKey, photoIds, setPhotoIds, act, setAct,
  weightSource, setWeightSource, manualKg, setManualKg,
  paperReference, setPaperReference, enabled, setEnabled, note, setNote, rows, setRows, commandScanPlace, placeMatches, placeReady, evidenceReady: marked && weight && paper && countsReady, forceCounts };
}

export type ReceiptForm = ReturnType<typeof useReceiptForm>;
