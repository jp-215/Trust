'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { StoryCard } from '@/components/StoryCard';
import { FactMatrix } from '@/components/FactMatrix';
import { ChatPanel } from '@/components/ChatPanel';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface StoryListItem {
  story_id: string;
  story_title?: string | null;
  outlets_covering: string[];
  num_articles: number;
}

interface Claim {
  claim_text: string;
  outlets_reporting: string[];
  outlets_silent: string[];
  agreement_status: 'STRONG' | 'MEDIUM' | 'WEAK' | 'CONFLICTING';
}

interface StoryDetail {
  story_id: string;
  story_title?: string | null;
  outlets_covering: string[];
  num_articles: number;
  claim_matrix: Claim[];
  synthesized_truth: string | null;
  confidence: number | null;
}

export default function Home() {
  const [stories, setStories] = useState<StoryListItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [story, setStory] = useState<StoryDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStories = () =>
    axios
      .get(`${API_BASE_URL}/stories`)
      .then((res) => {
        setStories(res.data || []);
        setError(null);
      })
      .catch(() => {
        setError(
          `Could not reach backend at ${API_BASE_URL}. Is it running? (uvicorn main:app --reload)`
        );
      });

  useEffect(() => {
    fetchStories();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadStory = async (storyId: string) => {
    setSelectedId(storyId);
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API_BASE_URL}/story/${storyId}`);
      setStory(res.data);
    } catch (err: any) {
      if (err?.response?.status === 404) {
        // Story IDs change when the ingestion pipeline re-runs —
        // this list was stale, so refresh it automatically.
        setSelectedId(null);
        await fetchStories();
        setError(
          'That story no longer exists (the pipeline re-ran and story IDs changed). Story list refreshed — pick one again.'
        );
      } else {
        setError(`Failed to load story "${storyId}".`);
      }
      setStory(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold">🛡️ Trust</h1>
        <p className="text-gray-600">
          Cross-outlet fact checking — fact matrix, synthesis, and Gemini chat
        </p>
      </header>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-300 text-red-800 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Story picker */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">📚 Stories</h2>
        {stories.length === 0 ? (
          <p className="text-gray-400 text-sm">No stories loaded.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {stories.map((s) => (
              <button
                key={s.story_id}
                onClick={() => loadStory(s.story_id)}
                className={`px-4 py-2 rounded-lg text-sm border ${
                  selectedId === s.story_id
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-gray-50 text-gray-800 border-gray-300 hover:bg-gray-100'
                }`}
              >
                {s.story_title || s.story_id}
                <span className="ml-2 opacity-70">
                  ({s.outlets_covering?.length ?? 0} outlets)
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {loading && <p className="text-gray-500 mb-6">Loading story…</p>}

      {/* Story detail */}
      {story && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <StoryCard
              storyId={story.story_title || story.story_id}
              outletsCovering={story.outlets_covering}
              numArticles={story.num_articles}
              synthesizedTruth={
                story.synthesized_truth ?? 'No synthesis available yet.'
              }
              confidence={story.confidence ?? undefined}
            />
            <FactMatrix
              claims={story.claim_matrix ?? []}
              outlets={story.outlets_covering}
            />
          </div>
          <div className="lg:col-span-1 h-[600px]">
            <ChatPanel storyId={story.story_id} apiBaseUrl={API_BASE_URL} />
          </div>
        </div>
      )}
    </main>
  );
}
