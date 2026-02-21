import React from 'react';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
type Size = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  asChild?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

const variantStyles: Record<Variant, string> = {
  primary: [
    'inline-flex items-center justify-center gap-2',
    'bg-gradient-to-br from-aitema-accent to-aitema-accent-hover',
    'text-white font-semibold',
    'border-none rounded-btn',
    'shadow-[0_4px_14px_rgba(59,130,246,0.35)]',
    'transition-all duration-150',
    'hover:-translate-y-px hover:shadow-[0_6px_20px_rgba(59,130,246,0.45)]',
    'focus-visible:outline-2 focus-visible:outline-amber-400 focus-visible:outline-offset-2',
    'active:translate-y-0 active:scale-[0.98]',
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0',
    'cursor-pointer font-[inherit] tracking-tight',
  ].join(' '),
  secondary: [
    'inline-flex items-center justify-center gap-2',
    'bg-slate-100 text-slate-800',
    'border border-slate-200 rounded-btn',
    'font-medium',
    'transition-all duration-150',
    'hover:bg-slate-200 hover:border-slate-300',
    'focus-visible:outline-2 focus-visible:outline-amber-400 focus-visible:outline-offset-2',
    'active:scale-[0.98]',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'cursor-pointer font-[inherit]',
  ].join(' '),
  ghost: [
    'inline-flex items-center justify-center gap-2',
    'bg-transparent text-slate-600',
    'border border-transparent rounded-btn',
    'font-medium',
    'transition-all duration-150',
    'hover:bg-slate-100 hover:text-slate-900',
    'focus-visible:outline-2 focus-visible:outline-amber-400 focus-visible:outline-offset-2',
    'active:scale-[0.98]',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'cursor-pointer font-[inherit]',
  ].join(' '),
  danger: [
    'inline-flex items-center justify-center gap-2',
    'bg-red-600 text-white font-semibold',
    'border-none rounded-btn',
    'transition-all duration-150',
    'hover:bg-red-700 hover:-translate-y-px',
    'focus-visible:outline-2 focus-visible:outline-amber-400 focus-visible:outline-offset-2',
    'active:scale-[0.98]',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'cursor-pointer font-[inherit]',
  ].join(' '),
};

const sizeStyles: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-sm min-h-[36px]',
  md: 'px-5 py-2.5 text-[0.9375rem] min-h-[44px]',
  lg: 'px-7 py-3.5 text-base min-h-[52px]',
};

export function Button({
  variant = 'primary',
  size = 'md',
  icon,
  iconPosition = 'left',
  className = '',
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {icon && iconPosition === 'left' && <span aria-hidden="true">{icon}</span>}
      {children}
      {icon && iconPosition === 'right' && <span aria-hidden="true">{icon}</span>}
    </button>
  );
}
