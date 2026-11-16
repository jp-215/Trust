import { api } from './api';
import type { ChatResponse } from '@/types';

export async function sendChat(
  storyId: string,
  question: string
): Promise<ChatResponse> {
  const res = await api.post<ChatResponse>('/chat', {
    story_id: storyId,
    question,
  });
  return res.data;
}
