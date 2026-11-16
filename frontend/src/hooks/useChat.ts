'use client';

import { useCallback, useState } from 'react';
import { sendChat } from '@/services/chatService';
import { errorDetail } from '@/services/api';
import type { ChatMessage } from '@/types';

export function useChat(storyId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sending, setSending] = useState(false);

  const send = useCallback(
    async (question: string) => {
      const trimmed = question.trim();
      if (!trimmed || sending) return;

      setMessages((prev) => [...prev, { role: 'user', content: trimmed }]);
      setSending(true);
      try {
        const res = await sendChat(storyId, trimmed);
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: res.answer,
            citations: res.citations ?? [],
            confidence: res.confidence,
          },
        ]);
      } catch (err) {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `❌ ${errorDetail(err, 'Could not get response from agent.')}`,
          },
        ]);
      } finally {
        setSending(false);
      }
    },
    [storyId, sending]
  );

  return { messages, sending, send };
}
