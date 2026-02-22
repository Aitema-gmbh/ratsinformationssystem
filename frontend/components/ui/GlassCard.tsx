import { ReactNode } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  href?: string;
}

export function GlassCard({ children, className = '', href }: GlassCardProps) {
  const style = {
    background: 'rgba(255, 255, 255, 0.08)',
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
    border: '1px solid rgba(255, 255, 255, 0.15)',
    borderRadius: '1rem',
    padding: '1.5rem',
    transition: 'all 0.2s ease',
  };

  if (href) {
    return (
      <a href={href} style={style} className={className}>
        {children}
      </a>
    );
  }
  return (
    <div style={style} className={className}>
      {children}
    </div>
  );
}
