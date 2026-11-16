import React from 'react';
import { cn } from '@/lib/format';

type BadgeTone = 'blue' | 'green' | 'yellow' | 'red' | 'gray';

const tones: Record<BadgeTone, string> = {
  blue: 'bg-blue-100 text-blue-900',
  green: 'bg-green-100 text-green-900',
  yellow: 'bg-yellow-100 text-yellow-900',
  red: 'bg-red-100 text-red-900',
  gray: 'bg-gray-100 text-gray-800',
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
        'inline-block px-3 py-1 rounded-full text-sm font-medium',
        tones[tone],
        className
      )}
    >
      {children}
    </span>
  );
});
