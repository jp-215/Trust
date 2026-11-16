'use client';

import React, { useCallback, useMemo, useState } from 'react';
import { useStories } from '@/hooks/useStories';
import { useOutlets } from '@/hooks/useOutlets';
import { useSearch } from '@/hooks/useSearch';
import { SearchBar } from '@/components/search/SearchBar';
import { StoryListCard } from '@/components/story/StoryListCard';
import { TrendingBand } from '@/components/story/TrendingBand';
import { AssistantWidget } from '@/components/chat/AssistantWidget';
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

  // Newest first — drives both the trending band and the grid order.
  const sortedStories = useMemo(() => {
    const list = [...(stories ?? [])];
    list.sort((a, b) => (b.created_at ?? '').localeCompare(a.created_at ?? ''));
    return list;
  }, [stories]);

  const stats = useMemo(() => {
    const totalArticles = sortedStories.reduce(
      (sum, s) => sum + (s.num_articles ?? 0),
      0
    );
    return {
      totalStories: sortedStories.length,
      totalArticles,
      totalOutlets: outlets?.length ?? 0,
      latestIngest: sortedStories[0]?.created_at ?? null,
    };
  }, [sortedStories, outlets]);

  const visibleStories = useMemo(() => {
    let list = sortedStories;
    if (searchResults !== null) {
      const ids = new Set(searchResults.map((r) => r.story_id));
      list = list.filter((s) => ids.has(s.story_id));
    }
    if (outletFilter) {
      list = list.filter((s) => s.outlets_covering?.includes(outletFilter));
    }
    return list;
  }, [sortedStories, searchResults, outletFilter]);

  const toggleOutlet = useCallback((outlet: string) => {
    setOutletFilter((current) => (current === outlet ? null : outlet));
  }, []);

  const filtering = query.trim().length >= 2 || !!outletFilter;

  return (
    <main className="max-w-7xl mx-auto px-6 py-8">
      {error ? (
        <ErrorBanner>
          {errorDetail(error, 'Failed to load stories.')}{' '}
          <button className="underline font-medium" onClick={() => refresh()}>
            Retry
          </button>
        </ErrorBanner>
      ) : null}

      {!filtering && (
        <TrendingBand stories={sortedStories} latestIngest={stats.latestIngest} />
      )}

      {/* Databricks aggregate stats */}
      <section
        aria-label="Pipeline statistics"
        className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-9"
      >
        <StatTile label="Stories" value={stats.totalStories} />
        <StatTile label="Articles" value={stats.totalArticles} />
        <StatTile label="Outlets" value={stats.totalOutlets} />
        <StatTile label="Latest ingest" value={formatDate(stats.latestIngest)} />
      </section>

      {/* Search + outlet filter */}
      <section aria-label="Filters" className="mb-6 space-y-3" id="stories">
        <SearchBar value={query} onChange={setQuery} searching={searching} />
        {!!outlets?.length && (
          <div className="flex flex-wrap gap-2 items-center" id="outlets">
            <span className="text-sm text-ink-muted">Filter by outlet:</span>
            {outlets.map((outlet) => (
              <button
                key={outlet}
                type="button"
                onClick={() => toggleOutlet(outlet)}
                aria-pressed={outletFilter === outlet}
              >
                <Badge tone={outletFilter === outlet ? 'accent' : 'gray'}>
                  {outlet}
                </Badge>
              </button>
            ))}
          </div>
        )}
      </section>

      {/* Story grid */}
      <section aria-label="Latest stories">
        <h2 className="font-display text-xl font-bold tracking-tight mb-4">
          Latest stories
        </h2>
        {loading && !stories ? (
          <Spinner label="Querying Databricks gold table…" />
        ) : visibleStories.length === 0 ? (
          <EmptyState
            title="No stories match."
            hint={
              filtering
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

      <AssistantWidget />
    </main>
  );
}
