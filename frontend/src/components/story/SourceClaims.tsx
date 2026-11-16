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
    <li className="border border-line-faint bg-paper rounded-xl px-5 py-4">
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <Badge tone="accent">{claim.outlet}</Badge>
        {claim.claim_type && <Badge tone="warn">{claim.claim_type}</Badge>}
        {claim.entities?.map((e) => (
          <Badge key={`${e.type}:${e.name}`} tone="gray">
            {e.name}
            <span className="opacity-60"> · {e.type}</span>
          </Badge>
        ))}
        {claim.article_url ? (
          <a
            href={claim.article_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[13px] font-semibold text-accent-deep hover:underline"
          >
            {claim.article_title || claim.article_url} ↗
          </a>
        ) : (
          claim.article_title && (
            <span className="text-[13px] font-semibold">
              {claim.article_title}
            </span>
          )
        )}
      </div>

      <p className="text-[13px] text-ink-soft leading-relaxed">
        {claim.claim_text}
      </p>

      <p className="mt-2 text-[11px] text-ink-muted">
        {claim.extracted_at && <>Extracted {formatDate(claim.extracted_at)}</>}
        {claim.extraction_model && <> · Model: {claim.extraction_model}</>}
        {typeof claim.confidence === 'number' && (
          <> · Confidence: {(claim.confidence * 100).toFixed(0)}%</>
        )}
      </p>
    </li>
  );
});

interface SourceClaimsProps {
  storyId: string;
}

export function SourceClaims({ storyId }: SourceClaimsProps) {
  const { data: claims, loading } = useStoryClaims(storyId);

  return (
    <Card className="mb-6">
      <h2 className="font-display text-xl font-bold tracking-tight mb-4">
        Source claims &amp; articles
      </h2>

      {loading && !claims ? (
        <Spinner label="Querying claims table…" />
      ) : !claims?.length ? (
        <p className="text-sm text-ink-muted">
          No extracted claims recorded for this story.
        </p>
      ) : (
        <ul className="space-y-3">
          {claims.map((claim) => (
            <ClaimItem key={claim.claim_id} claim={claim} />
          ))}
        </ul>
      )}

      <p className="text-[11px] text-ink-muted mt-3.5">
        Source: workspace.trust_dev.claims
      </p>
    </Card>
  );
}
