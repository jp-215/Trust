import React from 'react';
import Link from 'next/link';
import { formatDate, shortId } from '@/lib/format';
import type { StoryListItem } from '@/types';

interface StoryListCardProps {
  story: StoryListItem;
}

export const StoryListCard = React.memo(function StoryListCard({
  story,
}: StoryListCardProps) {
  const title = story.story_title || shortId(story.story_id);
  return (
    <Link
      href={`/story/${encodeURIComponent(story.story_id)}`}
      className="block bg-white rounded-lg shadow p-4 hover:shadow-md hover:ring-2 hover:ring-blue-200 transition-shadow"
    >
      <h3 className="font-semibold text-gray-900 break-all">{title}</h3>
      <p className="text-sm text-gray-600 mt-1">
        {story.outlets_covering?.length ?? 0} outlet
        {(story.outlets_covering?.length ?? 0) === 1 ? '' : 's'} ·{' '}
        {story.num_articles} article{story.num_articles === 1 ? '' : 's'}
      </p>
      {story.created_at && (
        <p className="text-xs text-gray-400 mt-2">
          Ingested {formatDate(story.created_at)}
        </p>
      )}
    </Link>
  );
});
