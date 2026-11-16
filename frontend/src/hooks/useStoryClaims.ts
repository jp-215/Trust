'use client';

import { useCachedFetch } from './useCachedFetch';
import { getStoryClaims } from '@/services/storyService';
import type { SourceClaim } from '@/types';

/** Per-claim provenance (source articles, entities, extraction metadata). */
export function useStoryClaims(storyId: string | null) {
  return useCachedFetch<SourceClaim[]>(
    storyId ? `claims:${storyId}` : null,
    () => getStoryClaims(storyId as string)
  );
}
