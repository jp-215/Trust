import React from 'react';

export function ErrorBanner({ children }: { children: React.ReactNode }) {
  return (
    <div
      role="alert"
      className="mb-6 p-4 bg-red-50 border border-red-300 text-red-800 rounded-lg text-sm"
    >
      {children}
    </div>
  );
}
