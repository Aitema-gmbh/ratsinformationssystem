import { cn } from '@/lib/utils';
import React from 'react';

type GlassCardProps = {
  children: React.ReactNode;
  className?: string;
};

export function GlassCard({ children, className }: GlassCardProps) {
  return (
    <div
      className={cn(
        'rounded-2xl border border-white/10 bg-white/5 p-8 shadow-lg backdrop-blur-lg',
        className
      )}
    >
      {children}
    </div>
  );
}
