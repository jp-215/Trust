import React from 'react';
import { cn } from '@/lib/format';

interface StatTileProps {
  label: string;
  value: string | number;
  accent?: boolean;
}

export const StatTile = React.memo(function StatTile({
  label,
  value,
  accent,
}: StatTileProps) {
  return (
    <div className="bg-white border border-line rounded-xl px-5 py-4">
      <p className="text-xs font-semibold uppercase tracking-wider text-ink-muted">
        {label}
      </p>
      <p
        className={cn(
          'font-display text-3xl font-bold mt-1',
          accent && 'text-warn'
        )}
      >
        {value}
      </p>
    </div>
  );
});
