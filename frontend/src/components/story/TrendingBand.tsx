import React from 'react';
import Link from 'next/link';
import { Badge } from '@/components/ui/Badge';
import { coverageTone } from './StoryListCard';
import { formatDate, shortId } from '@/lib/format';
import type { StoryListItem } from '@/types';

interface TrendingBandProps {
  /** Stories already sorted newest first. */
  stories: StoryListItem[];
  latestIngest: string | null;
}

export const TrendingBand = React.memo(function TrendingBand({
  stories,
  latestIngest,
}: TrendingBandProps) {
  if (!stories.length) return null;

  const [lead, ...rest] = stories;
  const ranked = rest.slice(0, 5);
  const leadTitle = lead.story_title || shortId(lead.story_id);
  const leadBadge = coverageTone(lead.outlets_covering?.length ?? 0);

  return (
    <section aria-label="Trending now" className="mb-9">
      <div className="flex flex-wrap items-baseline gap-3 mb-4">
        <h2 className="font-display text-2xl font-bold tracking-tight">
          Trending now
        </h2>
        {latestIngest && (
          <span className="text-[13px] text-ink-muted">
            Latest ingest · {formatDate(latestIngest)}
          </span>
        )}
      </div>

      <div className="flex flex-wrap gap-6">
        {/* Lead story */}
        <article className="flex-[2_1_480px] min-w-0 bg-white border border-line rounded-2xl p-7 flex flex-col gap-3.5">
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone={leadBadge.tone}>{leadBadge.label}</Badge>
            <span className="text-xs text-ink-muted">
              {lead.outlets_covering?.length ?? 0} outlet
              {(lead.outlets_covering?.length ?? 0) === 1 ? '' : 's'} ·{' '}
              {lead.num_articles} article{lead.num_articles === 1 ? '' : 's'}
            </span>
          </div>
          <h3 className="font-display text-3xl font-semibold leading-tight tracking-tight break-words">
            {leadTitle}
          </h3>
          <div className="flex flex-wrap gap-2">
            {lead.outlets_covering?.map((outlet) => (
              <Badge key={outlet} tone="accent">
                {outlet}
              </Badge>
            ))}
          </div>
          <Link
            href={`/story/${encodeURIComponent(lead.story_id)}`}
            className="self-start mt-1 bg-accent text-white text-sm font-semibold px-5 py-2.5 rounded-xl hover:bg-accent-deep transition-colors"
          >
            Compare the claims →
          </Link>
        </article>

        {/* Ranked latest list */}
        <div className="flex-[1_1_320px] min-w-0 bg-white border border-line rounded-2xl px-5 py-1.5 flex flex-col">
          {ranked.map((story, idx) => (
            <Link
              key={story.story_id}
              href={`/story/${encodeURIComponent(story.story_id)}`}
              className="flex items-center gap-3 py-3 border-b border-line-faint last:border-b-0 group"
            >
              <span className="font-display text-xl font-bold text-accent w-6 shrink-0">
                {idx + 2}
              </span>
              <span className="min-w-0">
                <span className="block text-sm font-semibold leading-snug group-hover:text-accent-deep">
                  {story.story_title || shortId(story.story_id)}
                </span>
                <span className="block text-xs text-ink-muted mt-0.5">
                  {story.outlets_covering?.join(', ') || 'Unknown'}
                  {story.created_at && <> · {formatDate(story.created_at)}</>}
                </span>
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
});
