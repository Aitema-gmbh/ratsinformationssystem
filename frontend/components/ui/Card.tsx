import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
  padding?: 'sm' | 'md' | 'lg' | 'none';
  as?: React.ElementType;
  href?: string;
  onClick?: () => void;
}

const paddingStyles = {
  none: '',
  sm: 'p-4',
  md: 'p-5',
  lg: 'p-6 md:p-8',
};

export function Card({
  children,
  className = '',
  hoverable = false,
  padding = 'md',
  as: Tag = 'div',
  ...props
}: CardProps) {
  return (
    <Tag
      className={[
        'bg-white',
        'border border-slate-200',
        'rounded-[0.75rem]',
        'shadow-[0_1px_3px_rgba(0,0,0,0.05),0_1px_2px_rgba(0,0,0,0.04)]',
        paddingStyles[padding],
        hoverable ? [
          'transition-all duration-200',
          'cursor-pointer',
          'hover:border-blue-200',
          'hover:shadow-[0_4px_16px_rgba(59,130,246,0.10),0_2px_6px_rgba(0,0,0,0.05)]',
          'hover:-translate-y-px',
        ].join(' ') : '',
        className,
      ].join(' ')}
      {...props}
    >
      {children}
    </Tag>
  );
}

export function CardHeader({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`mb-4 pb-4 border-b border-slate-100 ${className}`}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <h3 className={`text-base font-semibold text-aitema-navy tracking-tight leading-snug ${className}`}>
      {children}
    </h3>
  );
}

export function CardBody({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={className}>
      {children}
    </div>
  );
}

export function CardFooter({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`mt-4 pt-4 border-t border-slate-100 flex items-center justify-between gap-3 ${className}`}>
      {children}
    </div>
  );
}
