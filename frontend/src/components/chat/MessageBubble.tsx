import React from 'react';
import type { ChatMessage } from '@/types';

export const MessageBubble = React.memo(function MessageBubble({
  message,
}: {
  message: ChatMessage;
}) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={
          isUser
            ? 'max-w-[85%] bg-accent text-white px-3.5 py-2 rounded-xl rounded-br-sm text-[13px] leading-relaxed'
            : 'max-w-[90%] bg-white border border-line px-3.5 py-2 rounded-xl rounded-bl-sm text-[13px] leading-relaxed text-ink'
        }
      >
        <p className="whitespace-pre-line">{message.content}</p>

        {!isUser && !!message.citations?.length && (
          <p className="mt-2 pt-1.5 border-t border-line-faint text-[11px] text-ink-muted">
            <span className="font-bold">Sources:</span>{' '}
            {message.citations.join(' · ')}
          </p>
        )}

        {!isUser && typeof message.confidence === 'number' && (
          <p className="mt-1 text-[11px] text-ink-muted">
            Confidence: {(message.confidence * 100).toFixed(0)}%
          </p>
        )}
      </div>
    </div>
  );
});
