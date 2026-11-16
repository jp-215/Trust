import React from 'react';
import { Badge } from '@/components/ui/Badge';

interface OutletChipsProps {
  outlets: string[];
}

export const OutletChips = React.memo(function OutletChips({
  outlets,
}: OutletChipsProps) {
  if (!outlets.length) {
    return <span className="text-sm text-ink-muted">No outlets recorded</span>;
  }
  return (
    <div className="flex flex-wrap gap-2">
      {outlets.map((outlet) => (
        <Badge key={outlet} tone="accent">
          {outlet}
        </Badge>
      ))}
    </div>
  );
});
