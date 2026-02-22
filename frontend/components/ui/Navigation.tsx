'use client';

import Link from 'next/link';
import { useSelectedLayoutSegment } from 'next/navigation';
import { cn } from '@/lib/utils';

const navLinks = [
  { href: '/sitzungen', label: 'Sitzungen', segment: 'sitzungen' },
  { href: '/vorlagen', label: 'Vorlagen', segment: 'vorlagen' },
  { href: '/personen', label: 'Personen', segment: 'personen' },
  { href: '/gremien', label: 'Gremien', segment: 'gremien' },
  { href: '/kalender', label: 'Kalender', segment: 'kalender' },
];

export function Navigation() {
  const activeSegment = useSelectedLayoutSegment();

  return (
    <nav className="hidden md:flex items-center gap-2">
      {navLinks.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className={cn(
            'px-3 py-2 rounded-md text-sm font-medium transition-colors',
            'text-slate-300 hover:text-white hover:bg-white/10',
            activeSegment === link.segment && 'bg-white/10 text-white'
          )}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
