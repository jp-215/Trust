'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useStory } from '@/hooks/useStory';
import { StoryCard } from '@/components/story/StoryCard';
import { FactMatrix } from '@/components/story/FactMatrix';
import { ContradictionList } from '@/components/story/ContradictionList';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorBanner } from '@/components/ui/ErrorBanner';
import { errorDetail } from '@/services/api';
import { shortId } from '@/lib/format';

export default function StoryPage() {
  const params = useParams<{ id: string }>();
  const storyId = params?.id ? decodeURIComponent(params.id) : null;
  const { data: story, loading, error, notFound } = useStory(storyId);

  useEffect(() => {
    if (story) {
      document.title = `${story.story_title || shortId(story.story_id)} — Trust`;
    }
  }, [story]);

  return (
    <main className="max-w-7xl mx-auto px-4 py-8">
      <nav className="mb-6 text-sm" aria-label="Breadcrumb">
        <Link href="/" className="text-blue-600 hover:text-blue-800">
          ← Back to dashboard
        </Link>
      </nav>

      {loading && <Spinner label="Querying Databricks gold table…" />}

      {notFound && (
        <ErrorBanner>
          This story no longer exists — the ingestion pipeline re-ran and story
          IDs changed. The story list cache has been cleared.{' '}
          <Link href="/" className="underline font-medium">
            Pick a story from the refreshed dashboard.
          </Link>
        </ErrorBanner>
      )}

      {!!error && !notFound && (
        <ErrorBanner>{errorDetail(error, 'Failed to load story.')}</ErrorBanner>
      )}

      {story && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <StoryCard
              storyId={story.story_id}
              title={story.story_title}
              outletsCovering={story.outlets_covering}
              numArticles={story.num_articles}
              synthesizedTruth={
                story.synthesized_truth ?? 'No synthesis available yet.'
              }
              confidence={story.confidence ?? undefined}
              createdAt={story.created_at}
            />
            <FactMatrix
              claims={story.claim_matrix ?? []}
              outlets={story.outlets_covering}
            />
            <ContradictionList pairs={story.contradiction_pairs ?? []} />
          </div>
          <div className="lg:col-span-1 h-[600px] lg:sticky lg:top-6">
            <ChatPanel storyId={story.story_id} />
          </div>
        </div>
      )}
    </main>
  );
}
