'use client';

import React from 'react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  searching?: boolean;
}

export const SearchBar = React.memo(function SearchBar({
  value,
  onChange,
  searching,
}: SearchBarProps) {
  return (
    <div className="relative">
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search stories by title…"
        aria-label="Search stories"
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
      />
      {searching && (
        <span
          className="absolute right-3 top-1/2 -translate-y-1/2 inline-block w-4 h-4 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"
          aria-hidden="true"
        />
      )}
    </div>
  );
});
