import { api } from './api';
import type {
  SearchResult,
  SourceClaim,
  StoryDetail,
  StoryListItem,
} from '@/types';

export async function getStories(limit = 50): Promise<StoryListItem[]> {
  const res = await api.get<StoryListItem[]>('/stories', { params: { limit } });
  return res.data ?? [];
}

export async function getStory(storyId: string): Promise<StoryDetail> {
  const res = await api.post<StoryDetail>(
    `/story/${encodeURIComponent(storyId)}`
  );
  return res.data;
}

export async function getStoryClaims(storyId: string): Promise<SourceClaim[]> {
  const res = await api.get<SourceClaim[]>(
    `/story/${encodeURIComponent(storyId)}/claims`
  );
  return res.data ?? [];
}

export async function getOutlets(): Promise<string[]> {
  const res = await api.get<string[]>('/outlets');
  return res.data ?? [];
}

export async function searchStories(
  query: string,
  limit = 20
): Promise<SearchResult[]> {
  const res = await api.post<SearchResult[]>('/search', null, {
    params: { query, limit },
  });
  return res.data ?? [];
}
