import React from 'react';

interface SkeletonProps {
  className?: string;
  width?: string;
  height?: string;
  rounded?: 'sm' | 'md' | 'lg' | 'full';
  variant?: 'text' | 'circle' | 'rect';
}

const roundedStyles = {
  sm: 'rounded',
  md: 'rounded-md',
  lg: 'rounded-xl',
  full: 'rounded-full',
};

export function Skeleton({
  className = '',
  width,
  height,
  rounded = 'md',
  variant = 'rect',
}: SkeletonProps) {
  const baseStyles = [
    'block',
    'bg-gradient-to-r from-slate-100 via-slate-200 to-slate-100',
    'bg-[length:200%_100%]',
    'animate-[skeleton-shimmer_1.6s_ease-in-out_infinite]',
    variant === 'circle' ? 'rounded-full' : roundedStyles[rounded],
    className,
  ].join(' ');

  return (
    <span
      className={baseStyles}
      style={{
        width: variant === 'circle' ? (height || '2.5rem') : width,
        height: variant === 'text' ? '0.875rem' : height,
        display: 'block',
      }}
      aria-hidden="true"
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-[0_1px_3px_rgba(0,0,0,0.05)]">
      <div className="flex items-start gap-4">
        <Skeleton variant="circle" height="3rem" className="flex-shrink-0" />
        <div className="flex-1 space-y-2.5">
          <Skeleton width="60%" height="1rem" />
          <Skeleton width="40%" height="0.75rem" />
          <Skeleton width="80%" height="0.75rem" />
        </div>
      </div>
    </div>
  );
}

export function SkeletonText({ lines = 3 }: { lines?: number }) {
  const widths = ['100%', '85%', '70%', '90%', '60%'];
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          width={widths[i % widths.length]}
          height="0.875rem"
        />
      ))}
    </div>
  );
}
