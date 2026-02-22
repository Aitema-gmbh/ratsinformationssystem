'use client';
import React from 'react';
import { cn } from '@/lib/utils';

interface AnimatedCounterProps {
  to: number;
  className?: string;
}

export function AnimatedCounter({ to, className }: AnimatedCounterProps) {
  return (
    <span
      className={cn('counter', className)}
      style={{ '--num': to } as React.CSSProperties}
    />
  );
}
