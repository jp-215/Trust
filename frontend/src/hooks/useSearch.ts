'use client';

import { useEffect, useState } from 'react';
import { useDebounce } from './useDebounce';
import { searchStories } from '@/services/storyService';
import type { SearchResult } from '@/types';

/**
 * Debounced story search against POST /search (Databricks LIKE query).
 * Returns `results: null` when the query is too short to search —
 * callers treat that as "no filter active".
 */
export function useSearch(query: string, minLength = 2) {
  const debounced = useDebounce(query.trim(), 300);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    let cancelled = false;

    if (debounced.length < minLength) {
      setResults(null);
      setSearching(false);
      return;
    }

    setSearching(true);
    searchStories(debounced)
      .then((r) => {
        if (!cancelled) setResults(r);
      })
      .catch(() => {
        if (!cancelled) setResults([]);
      })
      .finally(() => {
        if (!cancelled) setSearching(false);
      });

    return () => {
      cancelled = true;
    };
  }, [debounced, minLength]);

  return { results, searching };
}
