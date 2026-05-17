import axios from "axios";
import { API_BASE_URL } from "../config";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: {
    "Content-Type": "application/json"
  }
});

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object") return JSON.stringify(detail);
    return error.message;
  }
  if (error instanceof Error) return error.message;
  return String(error);
}
