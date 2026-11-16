import React from 'react';
import { cn } from '@/lib/format';

interface CardProps {
  className?: string;
  children: React.ReactNode;
}

export function Card({ className, children }: CardProps) {
  return (
    <div className={cn('bg-white rounded-lg shadow p-6', className)}>
      {children}
    </div>
  );
}
