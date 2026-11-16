import React from 'react';

interface Claim {
  claim_text: string;
  outlets_reporting: string[];
  outlets_silent: string[];
  agreement_status: 'STRONG' | 'MEDIUM' | 'WEAK' | 'CONFLICTING';
}

interface FactMatrixProps {
  claims: Claim[];
  outlets: string[];
}

const agreementColors = {
  STRONG: 'bg-green-100 border-green-300',
  MEDIUM: 'bg-yellow-100 border-yellow-300',
  WEAK: 'bg-orange-100 border-orange-300',
  CONFLICTING: 'bg-red-100 border-red-300',
};

const getStatusIcon = (reporting: boolean, silent: boolean) => {
  if (reporting) return <span className="text-green-600 font-bold">✓</span>;
  if (silent) return <span className="text-gray-400">○</span>;
  return <span className="text-red-600 font-bold">✗</span>;
};

export const FactMatrix: React.FC<FactMatrixProps> = ({ claims, outlets }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-xl font-bold mb-4">📊 FACT DETECTION MATRIX</h2>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100 border-b-2 border-gray-300">
              <th className="text-left p-3 font-bold">Claim</th>
              {outlets.map((outlet) => (
                <th key={outlet} className="text-center p-3 font-bold text-sm">
                  {outlet.slice(0, 3)}
                </th>
              ))}
              <th className="text-center p-3 font-bold">Consensus</th>
            </tr>
          </thead>
          <tbody>
            {claims.map((claim, idx) => (
              <tr
                key={idx}
                className={`border-b ${
                  agreementColors[
                    claim.agreement_status?.toUpperCase() as keyof typeof agreementColors
                  ] ?? 'bg-gray-50 border-gray-200'
                }`}
              >
                <td className="p-3 text-sm">{claim.claim_text}</td>
                {outlets.map((outlet) => (
                  <td key={outlet} className="text-center p-3">
                    {getStatusIcon(
                      claim.outlets_reporting.includes(outlet),
                      claim.outlets_silent.includes(outlet)
                    )}
                  </td>
                ))}
                <td className="text-center p-3 font-bold text-sm">
                  {claim.agreement_status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 text-xs text-gray-600">
        <p>Legend: <span className="text-green-600">✓</span> Reported •
        <span className="text-red-600"> ✗</span> Contradicted •
        <span className="text-gray-400"> ○</span> Silent/Unclear</p>
      </div>
    </div>
  );
};
