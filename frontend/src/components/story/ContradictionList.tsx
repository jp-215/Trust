import React from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import type { ContradictionPair } from '@/types';

interface ContradictionListProps {
  pairs: ContradictionPair[];
}

export const ContradictionList = React.memo(function ContradictionList({
  pairs,
}: ContradictionListProps) {
  return (
    <Card className="mb-6">
      <h2 className="font-display text-xl font-bold tracking-tight mb-4">
        Contradictions between outlets
      </h2>

      {pairs.length === 0 ? (
        <p className="text-sm text-ink-muted">
          No contradictions detected between outlets for this story.
        </p>
      ) : (
        <ul className="space-y-4">
          {pairs.map((pair, idx) => (
            <li
              key={idx}
              className="grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              <div className="border border-warn-line bg-warn-card rounded-xl p-5">
                <Badge tone="warn">{pair.outlet_a}</Badge>
                <p className="text-sm leading-relaxed mt-3">
                  &ldquo;{pair.claim_a}&rdquo;
                </p>
              </div>
              <div className="border border-warn-line bg-warn-card rounded-xl p-5">
                <Badge tone="warn">{pair.outlet_b}</Badge>
                <p className="text-sm leading-relaxed mt-3">
                  &ldquo;{pair.claim_b}&rdquo;
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
});
