'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { cacheGet, cacheSet } from '@/services/cache';

interface CachedFetchState<T> {
  data: T | null;
  loading: boolean;
  error: unknown;
  /** Bypass the cache, refetch, and rewrite the cache. */
  refresh: () => Promise<void>;
}

/**
 * Generic fetch hook backed by the 7-minute TTL localStorage cache.
 *
 * Cache reads happen in an effect (not initial state) so server-rendered
 * HTML and the client's first paint match — no hydration mismatches.
 * Pass `key: null` to disable fetching (e.g., while a route param loads).
 */
export function useCachedFetch<T>(
  key: string | null,
  fetcher: () => Promise<T>
): CachedFetchState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(key !== null);
  const [error, setError] = useState<unknown>(null);

  // Keep the latest fetcher without making it a dependency —
  // callers may pass inline closures.
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const load = useCallback(
    async (force: boolean) => {
      if (key === null) return;
      if (!force) {
        const cached = cacheGet<T>(key);
        if (cached !== null) {
          setData(cached);
          setLoading(false);
          setError(null);
          return;
        }
      }
      setLoading(true);
      setError(null);
      try {
        const fresh = await fetcherRef.current();
        cacheSet(key, fresh);
        setData(fresh);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    },
    [key]
  );

  useEffect(() => {
    setData(null);
    load(false);
  }, [load]);

  const refresh = useCallback(() => load(true), [load]);

  return { data, loading, error, refresh };
}
