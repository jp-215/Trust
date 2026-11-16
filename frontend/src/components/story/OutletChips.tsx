import React from 'react';
import { Badge } from '@/components/ui/Badge';

interface OutletChipsProps {
  outlets: string[];
}

export const OutletChips = React.memo(function OutletChips({
  outlets,
}: OutletChipsProps) {
  if (!outlets.length) {
    return <span className="text-sm text-gray-400">No outlets recorded</span>;
  }
  return (
    <div className="flex flex-wrap gap-2">
      {outlets.map((outlet) => (
        <Badge key={outlet} tone="blue">
          {outlet}
        </Badge>
      ))}
    </div>
  );
});
