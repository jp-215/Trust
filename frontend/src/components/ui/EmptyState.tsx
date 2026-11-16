import React from 'react';

interface EmptyStateProps {
  title: string;
  hint?: string;
}

export function EmptyState({ title, hint }: EmptyStateProps) {
  return (
    <div className="text-center text-gray-400 py-8">
      <p>{title}</p>
      {hint && <p className="text-sm mt-1">{hint}</p>}
    </div>
  );
}
