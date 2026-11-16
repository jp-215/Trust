/** Small formatting/utility helpers. */

/** Join conditional class names: cn('a', cond && 'b') */
export function cn(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(' ');
}

export function formatDate(iso?: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function truncate(text: string, max = 120): string {
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

/** Shorten pipeline UUID ids like "article-7bbd5bcd-…" for display. */
export function shortId(id: string): string {
  const m = id.match(/^(.*?-[0-9a-f]{8})/);
  return m ? `${m[1]}…` : truncate(id, 24);
}
