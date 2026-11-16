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
        className={`max-w-xs px-4 py-2 rounded-lg ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-none'
            : 'bg-gray-200 text-gray-900 rounded-bl-none'
        }`}
      >
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>

        {!isUser && !!message.citations?.length && (
          <div className="mt-2 text-xs text-gray-600 border-t pt-2">
            <p className="font-bold">Sources:</p>
            <p>{message.citations.join(', ')}</p>
          </div>
        )}

        {!isUser && typeof message.confidence === 'number' && (
          <div className="mt-1 text-xs text-gray-600">
            Confidence: {(message.confidence * 100).toFixed(0)}%
          </div>
        )}
      </div>
    </div>
  );
});
