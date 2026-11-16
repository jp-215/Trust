'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useStory } from '@/hooks/useStory';
import { StoryCard } from '@/components/story/StoryCard';
import { FactMatrix } from '@/components/story/FactMatrix';
import { ContradictionList } from '@/components/story/ContradictionList';
import { SourceClaims } from '@/components/story/SourceClaims';
import { AssistantWidget } from '@/components/chat/AssistantWidget';
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
    <main className="max-w-5xl mx-auto px-6 py-8">
      <nav className="mb-6 text-sm" aria-label="Breadcrumb">
        <Link
          href="/"
          className="font-semibold text-accent-deep hover:underline"
        >
          ← Back to trending
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
        <>
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
            hasContradictions={(story.contradiction_pairs?.length ?? 0) > 0}
          />
          <FactMatrix
            claims={story.claim_matrix ?? []}
            outlets={story.outlets_covering}
          />
          <ContradictionList pairs={story.contradiction_pairs ?? []} />
          <SourceClaims storyId={story.story_id} />
        </>
      )}

      <AssistantWidget storyId={story?.story_id ?? null} />
    </main>
  );
}
