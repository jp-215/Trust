'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useChat } from '@/hooks/useChat';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';

const SUGGESTIONS = [
  "What's the consensus?",
  'Which outlets disagree?',
  'Show source articles',
];

function SparkIcon({ size = 26 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1" />
      <circle cx="12" cy="12" r="3.5" />
    </svg>
  );
}

function AssistantChat({ storyId }: { storyId: string }) {
  const { messages, sending, send } = useChat(storyId);
  const [input, setInput] = useState('');
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const handleSend = useCallback(() => {
    if (!input.trim() || sending) return;
    send(input);
    setInput('');
  }, [input, sending, send]);

  return (
    <>
      {/* Messages */}
      <div className="h-72 overflow-y-auto p-4 flex flex-col gap-2.5 bg-paper">
        {messages.length === 0 && !sending && (
          <p className="text-center text-xs text-ink-muted mt-8 leading-relaxed">
            Ask anything about this coverage.
            <br />
            Try a suggestion below.
          </p>
        )}
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}
        {sending && <TypingIndicator />}
        <div ref={endRef} />
      </div>

      {/* Suggestion chips */}
      <div className="px-3.5 py-2.5 flex flex-wrap gap-1.5 border-t border-line-faint bg-white">
        {SUGGESTIONS.map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => !sending && send(q)}
            disabled={sending}
            className="bg-accent-tint text-accent-deep text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-accent-edge disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="p-3.5 border-t border-line-faint flex gap-2 bg-white">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about this coverage…"
          aria-label="Ask the assistant"
          disabled={sending}
          className="flex-1 min-w-0 px-3.5 py-2.5 border border-line rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-accent disabled:bg-line-faint"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={sending || !input.trim()}
          className="bg-accent text-white text-sm font-semibold px-4 py-2.5 rounded-xl hover:bg-accent-deep disabled:bg-ink-muted"
        >
          Send
        </button>
      </div>
    </>
  );
}

interface AssistantWidgetProps {
  /** When set, the assistant answers about this story; otherwise it
   * prompts the user to open a story first. */
  storyId?: string | null;
}

/**
 * Floating Gemini assistant: a button fixed bottom-right; clicking it
 * opens the chat popover above it.
 */
export function AssistantWidget({ storyId }: AssistantWidgetProps) {
  const [open, setOpen] = useState(false);
  const toggle = useCallback(() => setOpen((o) => !o), []);

  return (
    <>
      {open && (
        <div className="fixed right-6 bottom-24 z-40 w-[380px] max-w-[calc(100vw-48px)] bg-white border border-line rounded-2xl shadow-[0_16px_48px_rgba(22,24,29,0.16)] flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-accent text-white px-5 py-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <SparkIcon size={18} />
              <div>
                <p className="text-sm font-bold leading-tight">
                  Gemini Assistant
                </p>
                <p className="text-[11px] opacity-85 leading-tight">
                  Grounded in the claims table
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={toggle}
              aria-label="Close assistant"
              className="text-white text-lg leading-none px-2 py-1 hover:opacity-80"
            >
              ✕
            </button>
          </div>

          {storyId ? (
            <AssistantChat storyId={storyId} />
          ) : (
            <div className="p-6 bg-paper text-center">
              <p className="text-sm text-ink-soft leading-relaxed">
                Open a story to ask the assistant about its coverage, claims,
                and contradictions.
              </p>
              <Link
                href="/#stories"
                onClick={toggle}
                className="inline-block mt-4 text-sm font-semibold text-accent-deep underline"
              >
                Browse stories
              </Link>
            </div>
          )}
        </div>
      )}

      <button
        type="button"
        onClick={toggle}
        aria-label={open ? 'Close Gemini assistant' : 'Open Gemini assistant'}
        aria-expanded={open}
        className="fixed right-6 bottom-6 z-50 w-14 h-14 rounded-full bg-accent text-white flex items-center justify-center shadow-[0_8px_24px_rgba(14,124,102,0.4)] hover:bg-accent-deep transition-colors"
      >
        <SparkIcon />
      </button>
    </>
  );
}
