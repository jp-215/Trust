import React from 'react';

interface ConfidenceBarProps {
  /** 0..1 */
  value: number;
}

export const ConfidenceBar = React.memo(function ConfidenceBar({
  value,
}: ConfidenceBarProps) {
  const pct = Math.round(Math.min(Math.max(value, 0), 1) * 100);
  return (
    <div className="flex items-center gap-2">
      <div
        className="w-32 h-2 bg-gray-300 rounded-full overflow-hidden"
        role="meter"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={pct}
        aria-label="Confidence level"
      >
        <div className="h-full bg-green-500" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-bold">{pct}%</span>
    </div>
  );
});
