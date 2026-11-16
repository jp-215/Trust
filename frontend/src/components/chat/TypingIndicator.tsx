import React from 'react';

export function TypingIndicator() {
  return (
    <div className="flex justify-start" aria-label="Assistant is typing">
      <div className="bg-gray-200 text-gray-900 px-4 py-2 rounded-lg rounded-bl-none">
        <div className="flex space-x-2">
          <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce delay-100" />
          <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce delay-200" />
        </div>
      </div>
    </div>
  );
}
