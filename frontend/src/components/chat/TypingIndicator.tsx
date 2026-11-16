import React from 'react';

export function TypingIndicator() {
  return (
    <div className="flex justify-start" aria-label="Assistant is typing">
      <div className="bg-white border border-line px-3.5 py-2.5 rounded-xl rounded-bl-sm">
        <div className="flex space-x-1.5">
          <div className="w-2 h-2 bg-ink-muted rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-ink-muted rounded-full animate-bounce delay-100" />
          <div className="w-2 h-2 bg-ink-muted rounded-full animate-bounce delay-200" />
        </div>
      </div>
    </div>
  );
}
