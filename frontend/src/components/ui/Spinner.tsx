import React from 'react';

export function Spinner({ label }: { label?: string }) {
  return (
    <div
      className="flex items-center gap-3 text-gray-500"
      role="status"
      aria-live="polite"
    >
      <span className="inline-block w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin" />
      <span className="text-sm">{label ?? 'Loading…'}</span>
    </div>
  );
}
