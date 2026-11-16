import React, { useMemo } from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import type { Claim } from '@/types';

interface FactMatrixProps {
  claims: Claim[];
  outlets: string[];
}

const rowTints: Record<string, string> = {
  STRONG: 'bg-accent-wash',
  MEDIUM: 'bg-warn-wash',
  WEAK: 'bg-warn-wash',
  CONFLICTING: 'bg-warn-wash',
};

function consensusBadge(status: string) {
  const upper = status?.toUpperCase() ?? '';
  if (upper === 'STRONG') return <Badge tone="accent">STRONG</Badge>;
  if (upper === 'CONFLICTING') return <Badge tone="warn">CONFLICTING</Badge>;
  if (upper === 'MEDIUM' || upper === 'WEAK')
    return <Badge tone="warn">{upper}</Badge>;
  return <Badge tone="gray">{status || '—'}</Badge>;
}

const StatusIcon = React.memo(function StatusIcon({
  reporting,
  silent,
}: {
  reporting: boolean;
  silent: boolean;
}) {
  if (reporting) return <span className="text-accent-deep font-bold">✓</span>;
  if (silent) return <span className="text-ink-muted">○</span>;
  return <span className="text-danger font-bold">✗</span>;
});

interface ClaimRowModel {
  claim: Claim;
  tint: string;
  cells: { outlet: string; reporting: boolean; silent: boolean }[];
}

const ClaimRow = React.memo(function ClaimRow({ row }: { row: ClaimRowModel }) {
  return (
    <tr className={`border-b border-line-faint ${row.tint}`}>
      <td className="p-3 text-sm leading-relaxed">{row.claim.claim_text}</td>
      {row.cells.map((cell) => (
        <td key={cell.outlet} className="text-center p-3">
          <StatusIcon reporting={cell.reporting} silent={cell.silent} />
        </td>
      ))}
      <td className="text-center p-3">
        {consensusBadge(row.claim.agreement_status)}
      </td>
    </tr>
  );
});

export const FactMatrix = React.memo(function FactMatrix({
  claims,
  outlets,
}: FactMatrixProps) {
  const rows = useMemo<ClaimRowModel[]>(
    () =>
      claims.map((claim) => ({
        claim,
        tint: rowTints[claim.agreement_status?.toUpperCase() ?? ''] ?? '',
        cells: outlets.map((outlet) => ({
          outlet,
          reporting: claim.outlets_reporting?.includes(outlet) ?? false,
          silent: claim.outlets_silent?.includes(outlet) ?? false,
        })),
      })),
    [claims, outlets]
  );

  return (
    <Card className="mb-6">
      <h2 className="font-display text-xl font-bold tracking-tight mb-4">
        Fact detection matrix
      </h2>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b-2 border-line text-left">
              <th
                scope="col"
                className="p-3 text-xs font-bold uppercase tracking-wider text-ink-muted"
              >
                Claim
              </th>
              {outlets.map((outlet) => (
                <th
                  key={outlet}
                  scope="col"
                  className="p-3 text-xs font-bold uppercase tracking-wider text-ink-muted text-center"
                  title={outlet}
                >
                  {outlet.slice(0, 3)}
                </th>
              ))}
              <th
                scope="col"
                className="p-3 text-xs font-bold uppercase tracking-wider text-ink-muted text-center"
              >
                Consensus
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <ClaimRow key={row.claim.canonical_claim_id ?? idx} row={row} />
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-3.5 text-xs text-ink-muted">
        Legend: <span className="text-accent-deep font-bold">✓</span> Reported ·{' '}
        <span className="text-danger font-bold">✗</span> Contradicted ·{' '}
        <span>○</span> Silent / unclear
      </p>
    </Card>
  );
});
