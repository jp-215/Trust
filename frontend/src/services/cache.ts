/**
 * Persistent client-side cache with TTL, backed by localStorage.
 *
 * Databricks SQL warehouse queries take seconds; caching responses for a
 * short window makes navigation instant while staying reasonably fresh.
 * Every access is wrapped in try/catch so private windows / blocked storage
 * degrade gracefully to plain fetching.
 */

export const CACHE_TTL_MS = 7 * 60 * 1000; // 7 minutes

const PREFIX = 'trust:v1:';

interface CacheEntry<T> {
  data: T;
  expiresAt: number;
}

function storageAvailable(): boolean {
  return typeof window !== 'undefined' && !!window.localStorage;
}

export function cacheGet<T>(key: string): T | null {
  if (!storageAvailable()) return null;
  try {
    const raw = window.localStorage.getItem(PREFIX + key);
    if (!raw) return null;
    const entry = JSON.parse(raw) as CacheEntry<T>;
    if (!entry || typeof entry.expiresAt !== 'number') return null;
    if (Date.now() > entry.expiresAt) {
      window.localStorage.removeItem(PREFIX + key);
      return null;
    }
    return entry.data;
  } catch {
    return null;
  }
}

export function cacheSet<T>(key: string, data: T, ttlMs: number = CACHE_TTL_MS): void {
  if (!storageAvailable()) return;
  try {
    const entry: CacheEntry<T> = { data, expiresAt: Date.now() + ttlMs };
    window.localStorage.setItem(PREFIX + key, JSON.stringify(entry));
  } catch {
    // Quota exceeded or storage blocked — cache is best-effort.
  }
}

/** Remove one key, or every key starting with the given prefix. */
export function cacheInvalidate(keyOrPrefix: string): void {
  if (!storageAvailable()) return;
  try {
    const full = PREFIX + keyOrPrefix;
    const doomed: string[] = [];
    for (let i = 0; i < window.localStorage.length; i++) {
      const k = window.localStorage.key(i);
      if (k && k.startsWith(full)) doomed.push(k);
    }
    doomed.forEach((k) => window.localStorage.removeItem(k));
  } catch {
    // ignore
  }
}
