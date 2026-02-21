import React from 'react';

type BadgeVariant = 'blue' | 'green' | 'amber' | 'red' | 'purple' | 'slate' | 'indigo';

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  icon?: React.ReactNode;
  dot?: boolean;
  dotColor?: string;
  className?: string;
}

const variantStyles: Record<BadgeVariant, { bg: string; text: string; border: string }> = {
  blue:   { bg: 'bg-blue-50',   text: 'text-blue-700',   border: 'border-blue-100' },
  green:  { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-100' },
  amber:  { bg: 'bg-amber-50',  text: 'text-amber-700',  border: 'border-amber-100' },
  red:    { bg: 'bg-red-50',    text: 'text-red-700',    border: 'border-red-100' },
  purple: { bg: 'bg-violet-50', text: 'text-violet-700', border: 'border-violet-100' },
  slate:  { bg: 'bg-slate-100', text: 'text-slate-600',  border: 'border-slate-200' },
  indigo: { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-100' },
};

export function Badge({
  variant = 'blue',
  children,
  icon,
  dot,
  dotColor,
  className = '',
}: BadgeProps) {
  const { bg, text, border } = variantStyles[variant];
  return (
    <span
      className={[
        'inline-flex items-center gap-1.5',
        'px-2.5 py-0.5',
        'rounded-full',
        'text-xs font-semibold',
        'border',
        bg, text, border,
        className,
      ].join(' ')}
    >
      {dot && (
        <span
          className="w-1.5 h-1.5 rounded-full flex-shrink-0"
          style={{ background: dotColor || 'currentColor' }}
          aria-hidden="true"
        />
      )}
      {icon && <span aria-hidden="true" className="flex-shrink-0">{icon}</span>}
      {children}
    </span>
  );
}
