'use client';

import { useEffect, useState } from 'react';
import { useCachedFetch } from './useCachedFetch';
import { getStory } from '@/services/storyService';
import { cacheInvalidate } from '@/services/cache';
import { isNotFound } from '@/services/api';
import type { StoryDetail } from '@/types';

/**
 * Story detail by id, cached with TTL.
 *
 * Pipeline re-runs regenerate story UUIDs, so a story URL can go stale.
 * On a 404 we invalidate both this story's cache and the story list cache
 * so the dashboard refetches a fresh list.
 */
export function useStory(storyId: string | null) {
  const state = useCachedFetch<StoryDetail>(
    storyId ? `story:${storyId}` : null,
    () => getStory(storyId as string)
  );
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    if (state.error && isNotFound(state.error)) {
      setNotFound(true);
      if (storyId) cacheInvalidate(`story:${storyId}`);
      cacheInvalidate('stories:');
    } else {
      setNotFound(false);
    }
  }, [state.error, storyId]);

  return { ...state, notFound };
}
