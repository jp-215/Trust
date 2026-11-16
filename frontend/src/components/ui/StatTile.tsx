import React from 'react';

interface StatTileProps {
  label: string;
  value: string | number;
  icon?: string;
}

export const StatTile = React.memo(function StatTile({
  label,
  value,
  icon,
}: StatTileProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <p className="text-xs uppercase tracking-wide text-gray-500">
        {icon && <span aria-hidden="true">{icon} </span>}
        {label}
      </p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
});
