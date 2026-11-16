import axios from 'axios';

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/** Single shared axios instance for the Trust backend. */
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120_000, // Databricks warehouse queries + Gemini can be slow
});

export function isNotFound(err: unknown): boolean {
  return axios.isAxiosError(err) && err.response?.status === 404;
}

export function errorDetail(err: unknown, fallback: string): string {
  if (axios.isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: string } | undefined)?.detail;
    if (detail) return detail;
    if (!err.response) {
      return `Could not reach backend at ${API_BASE_URL}. Is it running? (uvicorn main:app --reload)`;
    }
  }
  return fallback;
}
