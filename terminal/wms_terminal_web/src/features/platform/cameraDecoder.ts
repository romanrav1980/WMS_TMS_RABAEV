import { BrowserMultiFormatReader, type IScannerControls } from "@zxing/browser";
import { BarcodeFormat, DecodeHintType } from "@zxing/library";

export function createCameraReader() {
 const formats = [BarcodeFormat.CODE_128, BarcodeFormat.EAN_13, BarcodeFormat.EAN_8,
  BarcodeFormat.QR_CODE, BarcodeFormat.DATA_MATRIX, BarcodeFormat.ITF, BarcodeFormat.CODE_39];
 return new BrowserMultiFormatReader(new Map([[DecodeHintType.POSSIBLE_FORMATS, formats]]),
  { delayBetweenScanAttempts: 180, delayBetweenScanSuccess: 800 });
}

export async function decodePhoto(file: File): Promise<string> {
 if (!file.type.startsWith("image/") || file.size > 12 * 1024 * 1024) throw new Error("Выберите фотографию кода до 12 МБ.");
 const url = URL.createObjectURL(file);
 try { return (await createCameraReader().decodeFromImageUrl(url)).getText(); }
 catch { throw new Error("Код не распознан. Снимите этикетку крупнее, без бликов, либо используйте сканер."); }
 finally { URL.revokeObjectURL(url); }
}

export type CameraControls = IScannerControls;
