import React, { useMemo } from 'react';
import { Card } from '@/components/ui/Card';
import type { Claim } from '@/types';

interface FactMatrixProps {
  claims: Claim[];
  outlets: string[];
}

const agreementColors: Record<string, string> = {
  STRONG: 'bg-green-100 border-green-300',
  MEDIUM: 'bg-yellow-100 border-yellow-300',
  WEAK: 'bg-orange-100 border-orange-300',
  CONFLICTING: 'bg-red-100 border-red-300',
};

const rowColor = (status: string) =>
  agreementColors[status?.toUpperCase()] ?? 'bg-gray-50 border-gray-200';

const StatusIcon = React.memo(function StatusIcon({
  reporting,
  silent,
}: {
  reporting: boolean;
  silent: boolean;
}) {
  if (reporting) return <span className="text-green-600 font-bold">✓</span>;
  if (silent) return <span className="text-gray-400">○</span>;
  return <span className="text-red-600 font-bold">✗</span>;
});

interface ClaimRowModel {
  claim: Claim;
  color: string;
  cells: { outlet: string; reporting: boolean; silent: boolean }[];
}

const ClaimRow = React.memo(function ClaimRow({ row }: { row: ClaimRowModel }) {
  return (
    <tr className={`border-b ${row.color}`}>
      <td className="p-3 text-sm">{row.claim.claim_text}</td>
      {row.cells.map((cell) => (
        <td key={cell.outlet} className="text-center p-3">
          <StatusIcon reporting={cell.reporting} silent={cell.silent} />
        </td>
      ))}
      <td className="text-center p-3 font-bold text-sm">
        {row.claim.agreement_status}
      </td>
    </tr>
  );
});

export const FactMatrix = React.memo(function FactMatrix({
  claims,
  outlets,
}: FactMatrixProps) {
  // Precompute row models once per data change instead of per render.
  const rows = useMemo<ClaimRowModel[]>(
    () =>
      claims.map((claim) => ({
        claim,
        color: rowColor(claim.agreement_status),
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
      <h2 className="text-xl font-bold mb-4">📊 FACT DETECTION MATRIX</h2>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100 border-b-2 border-gray-300">
              <th scope="col" className="text-left p-3 font-bold">
                Claim
              </th>
              {outlets.map((outlet) => (
                <th
                  key={outlet}
                  scope="col"
                  className="text-center p-3 font-bold text-sm"
                  title={outlet}
                >
                  {outlet.slice(0, 3)}
                </th>
              ))}
              <th scope="col" className="text-center p-3 font-bold">
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

      <div className="mt-4 text-xs text-gray-600">
        <p>
          Legend: <span className="text-green-600">✓</span> Reported •
          <span className="text-red-600"> ✗</span> Contradicted •
          <span className="text-gray-400"> ○</span> Silent/Unclear
        </p>
      </div>
    </Card>
  );
});
