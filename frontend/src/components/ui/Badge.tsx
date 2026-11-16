import React from 'react';
import { cn } from '@/lib/format';

type BadgeTone = 'accent' | 'warn' | 'gray' | 'danger';

const tones: Record<BadgeTone, string> = {
  accent: 'bg-accent-tint text-accent-deep',
  warn: 'bg-warn-tint text-warn',
  gray: 'bg-line-faint text-ink-soft',
  danger: 'bg-red-50 text-danger',
};

interface BadgeProps {
  tone?: BadgeTone;
  className?: string;
  children: React.ReactNode;
}

export const Badge = React.memo(function Badge({
  tone = 'gray',
  className,
  children,
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-block px-2.5 py-1 rounded-full text-xs font-semibold',
        tones[tone],
        className
      )}
    >
      {children}
    </span>
  );
});
