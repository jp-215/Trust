'use client';

import { useCachedFetch } from './useCachedFetch';
import { getOutlets } from '@/services/storyService';

export function useOutlets() {
  return useCachedFetch<string[]>('outlets', getOutlets);
}
