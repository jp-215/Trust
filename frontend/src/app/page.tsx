'use client';

import React, { useCallback, useMemo, useState } from 'react';
import { useStories } from '@/hooks/useStories';
import { useOutlets } from '@/hooks/useOutlets';
import { useSearch } from '@/hooks/useSearch';
import { SearchBar } from '@/components/search/SearchBar';
import { StoryListCard } from '@/components/story/StoryListCard';
import { StatTile } from '@/components/ui/StatTile';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { ErrorBanner } from '@/components/ui/ErrorBanner';
import { EmptyState } from '@/components/ui/EmptyState';
import { errorDetail } from '@/services/api';
import { formatDate } from '@/lib/format';

export default function DashboardPage() {
  const { data: stories, loading, error, refresh } = useStories();
  const { data: outlets } = useOutlets();
  const [query, setQuery] = useState('');
  const [outletFilter, setOutletFilter] = useState<string | null>(null);
  const { results: searchResults, searching } = useSearch(query);

  // Aggregate stats derived from the Databricks gold/raw tables.
  const stats = useMemo(() => {
    const list = stories ?? [];
    const totalArticles = list.reduce((sum, s) => sum + (s.num_articles ?? 0), 0);
    const latest = list.reduce<string | null>((acc, s) => {
      if (!s.created_at) return acc;
      return !acc || s.created_at > acc ? s.created_at : acc;
    }, null);
    return {
      totalStories: list.length,
      totalArticles,
      totalOutlets: outlets?.length ?? 0,
      latestIngest: latest,
    };
  }, [stories, outlets]);

  // Search results ∩ outlet filter, memoized so the grid only
  // re-renders when its inputs actually change.
  const visibleStories = useMemo(() => {
    let list = stories ?? [];
    if (searchResults !== null) {
      const ids = new Set(searchResults.map((r) => r.story_id));
      list = list.filter((s) => ids.has(s.story_id));
    }
    if (outletFilter) {
      list = list.filter((s) => s.outlets_covering?.includes(outletFilter));
    }
    return list;
  }, [stories, searchResults, outletFilter]);

  const toggleOutlet = useCallback((outlet: string) => {
    setOutletFilter((current) => (current === outlet ? null : outlet));
  }, []);

  return (
    <main className="max-w-7xl mx-auto px-4 py-8">
      {error ? (
        <ErrorBanner>
          {errorDetail(error, 'Failed to load stories.')}{' '}
          <button className="underline font-medium" onClick={() => refresh()}>
            Retry
          </button>
        </ErrorBanner>
      ) : null}

      {/* Databricks aggregate stats */}
      <section
        aria-label="Pipeline statistics"
        className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
      >
        <StatTile icon="📚" label="Stories" value={stats.totalStories} />
        <StatTile icon="📄" label="Articles" value={stats.totalArticles} />
        <StatTile icon="📰" label="Outlets" value={stats.totalOutlets} />
        <StatTile
          icon="⏱"
          label="Latest ingest"
          value={formatDate(stats.latestIngest)}
        />
      </section>

      {/* Search + outlet filter */}
      <section aria-label="Filters" className="mb-6 space-y-3">
        <SearchBar value={query} onChange={setQuery} searching={searching} />
        {!!outlets?.length && (
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-sm text-gray-500">Filter by outlet:</span>
            {outlets.map((outlet) => (
              <button
                key={outlet}
                type="button"
                onClick={() => toggleOutlet(outlet)}
                aria-pressed={outletFilter === outlet}
              >
                <Badge tone={outletFilter === outlet ? 'blue' : 'gray'}>
                  {outlet}
                </Badge>
              </button>
            ))}
          </div>
        )}
      </section>

      {/* Story grid */}
      <section aria-label="Stories">
        {loading && !stories ? (
          <Spinner label="Querying Databricks gold table…" />
        ) : visibleStories.length === 0 ? (
          <EmptyState
            title="No stories match."
            hint={
              query || outletFilter
                ? 'Try clearing the search or outlet filter.'
                : 'Run the ingestion pipeline to populate story_records.'
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {visibleStories.map((story) => (
              <StoryListCard key={story.story_id} story={story} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
