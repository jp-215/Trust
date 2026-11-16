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
    <div className="flex items-center gap-3">
      <div
        className="w-40 max-w-full h-2 bg-accent-edge rounded-full overflow-hidden"
        role="meter"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={pct}
        aria-label="Confidence level"
      >
        <div
          className="h-full bg-accent rounded-full"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-sm font-bold">{pct}%</span>
    </div>
  );
});
