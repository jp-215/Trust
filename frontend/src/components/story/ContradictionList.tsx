import React from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import type { ContradictionPair } from '@/types';

interface ContradictionListProps {
  pairs: ContradictionPair[];
}

/**
 * Renders contradiction_pairs from the gold table — outlet-vs-outlet
 * conflicting claims, the core cross-outlet fact-checking signal.
 */
export const ContradictionList = React.memo(function ContradictionList({
  pairs,
}: ContradictionListProps) {
  return (
    <Card className="mb-6">
      <h2 className="text-xl font-bold mb-4">⚔️ CONTRADICTIONS BETWEEN OUTLETS</h2>

      {pairs.length === 0 ? (
        <p className="text-sm text-gray-400">
          No contradictions detected between outlets for this story.
        </p>
      ) : (
        <ul className="space-y-4">
          {pairs.map((pair, idx) => (
            <li
              key={idx}
              className="border border-red-200 bg-red-50 rounded-lg p-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Badge tone="red">{pair.outlet_a}</Badge>
                  <p className="text-sm text-gray-800 mt-2">{pair.claim_a}</p>
                </div>
                <div>
                  <Badge tone="red">{pair.outlet_b}</Badge>
                  <p className="text-sm text-gray-800 mt-2">{pair.claim_b}</p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
});
