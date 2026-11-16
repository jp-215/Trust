import React from 'react';
import Link from 'next/link';
import { Badge } from '@/components/ui/Badge';
import { formatDate, shortId } from '@/lib/format';
import type { StoryListItem } from '@/types';

export function coverageTone(numOutlets: number): {
  label: string;
  tone: 'accent' | 'gray';
} {
  if (numOutlets >= 4) return { label: 'STRONG', tone: 'accent' };
  if (numOutlets >= 2) return { label: 'REPORTED', tone: 'accent' };
  return { label: 'LIMITED', tone: 'gray' };
}

interface StoryListCardProps {
  story: StoryListItem;
}

export const StoryListCard = React.memo(function StoryListCard({
  story,
}: StoryListCardProps) {
  const title = story.story_title || shortId(story.story_id);
  const outletCount = story.outlets_covering?.length ?? 0;
  const badge = coverageTone(outletCount);

  return (
    <Link
      href={`/story/${encodeURIComponent(story.story_id)}`}
      className="flex flex-col gap-2.5 bg-white border border-line rounded-xl p-5 hover:border-accent hover:shadow-sm transition-all"
    >
      <Badge tone={badge.tone} className="self-start">
        {badge.label}
      </Badge>
      <span className="text-[15px] font-semibold leading-snug break-words">
        {title}
      </span>
      <span className="text-xs text-ink-muted">
        {story.outlets_covering?.join(', ') || 'Unknown outlet'} ·{' '}
        {story.num_articles} article{story.num_articles === 1 ? '' : 's'}
        {story.created_at && <> · {formatDate(story.created_at)}</>}
      </span>
    </Link>
  );
});
