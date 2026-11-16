import React from 'react';
import { cn } from '@/lib/format';

interface CardProps {
  className?: string;
  children: React.ReactNode;
}

export function Card({ className, children }: CardProps) {
  return (
    <div
      className={cn(
        'bg-white border border-line rounded-2xl p-7',
        className
      )}
    >
      {children}
    </div>
  );
}
