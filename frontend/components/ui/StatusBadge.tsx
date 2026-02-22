import { cn } from '@/lib/utils';
import React from 'react';

type StatusBadgeProps = {
  status: 'active' | 'inactive' | string;
  className?: string;
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-2 text-sm font-semibold',
        status === 'active' ? 'text-emerald-400' : 'text-slate-400',
        className
      )}
    >
      <span
        className={cn(
          'h-2 w-2 rounded-full',
          status === 'active' ? 'bg-emerald-500 pulse-glow' : 'bg-slate-500'
        )}
      />
      <span>{status === 'active' ? 'Aktiv' : 'Inaktiv'}</span>
    </div>
  );
}
