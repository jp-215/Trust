'use client';

import React from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { useStoryClaims } from '@/hooks/useStoryClaims';
import { formatDate } from '@/lib/format';
import type { SourceClaim } from '@/types';

const ClaimItem = React.memo(function ClaimItem({
  claim,
}: {
  claim: SourceClaim;
}) {
  return (
    <li className="border border-gray-200 rounded-lg p-4 bg-gray-50">
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <Badge tone="blue">{claim.outlet}</Badge>
        {claim.claim_type && <Badge tone="yellow">{claim.claim_type}</Badge>}
        {claim.entities?.map((e) => (
          <Badge key={`${e.type}:${e.name}`} tone="gray">
            {e.name}
            <span className="opacity-60"> · {e.type}</span>
          </Badge>
        ))}
      </div>

      <p className="text-sm text-gray-800">{claim.claim_text}</p>

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500">
        {claim.article_url ? (
          <a
            href={claim.article_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline"
          >
            {claim.article_title || claim.article_url} ↗
          </a>
        ) : (
          claim.article_title && <span>{claim.article_title}</span>
        )}
        {claim.extracted_at && (
          <span>Extracted {formatDate(claim.extracted_at)}</span>
        )}
        {claim.extraction_model && <span>Model: {claim.extraction_model}</span>}
        {typeof claim.confidence === 'number' && (
          <span>Confidence: {(claim.confidence * 100).toFixed(0)}%</span>
        )}
      </div>
    </li>
  );
});

interface SourceClaimsProps {
  storyId: string;
}

/**
 * Per-claim provenance from workspace.trust_dev.claims: which outlet said
 * what, in which article (with link), plus extraction metadata.
 */
export function SourceClaims({ storyId }: SourceClaimsProps) {
  const { data: claims, loading } = useStoryClaims(storyId);

  return (
    <Card className="mb-6">
      <h2 className="text-xl font-bold mb-4">📎 SOURCE CLAIMS & ARTICLES</h2>

      {loading && !claims ? (
        <Spinner label="Querying claims table…" />
      ) : !claims?.length ? (
        <p className="text-sm text-gray-400">
          No extracted claims recorded for this story.
        </p>
      ) : (
        <ul className="space-y-3">
          {claims.map((claim) => (
            <ClaimItem key={claim.claim_id} claim={claim} />
          ))}
        </ul>
      )}

      <p className="text-xs text-gray-500 mt-4">
        Source: workspace.trust_dev.claims
      </p>
    </Card>
  );
}
