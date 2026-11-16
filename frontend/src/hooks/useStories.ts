'use client';

import { useCachedFetch } from './useCachedFetch';
import { getStories } from '@/services/storyService';
import type { StoryListItem } from '@/types';

export function useStories(limit = 50) {
  return useCachedFetch<StoryListItem[]>(`stories:${limit}`, () =>
    getStories(limit)
  );
}
