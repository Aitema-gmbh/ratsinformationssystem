'use client';
import { usePathname } from 'next/navigation';
import Link from 'next/link';

const navItems = [
  { href: '/admin', label: 'Uebersicht', icon: '📊', exact: true },
  { href: '/admin/gremien', label: 'Gremien / Tenants', icon: '🏛️' },
  { href: '/admin/personen', label: 'Personen', icon: '👥' },
  { href: '/admin/sitzungen', label: 'Sitzungen', icon: '📅' },
  { href: '/admin/vorlagen', label: 'Vorlagen', icon: '📄' },
  { href: '/admin/einstellungen', label: 'Einstellungen', icon: '⚙️' },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: '#f8fafc' }}>
      {/* Sidebar */}
      <aside style={{
        width: '240px',
        background: '#0f172a',
        color: 'white',
        flexShrink: 0,
        padding: '1.5rem 0',
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        zIndex: 10,
        overflowY: 'auto',
      }}>
        <div style={{ padding: '0 1.5rem 1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.1em', opacity: 0.5, textTransform: 'uppercase' }}>
            aitema
          </div>
          <div style={{ fontSize: '1.125rem', fontWeight: 700, marginTop: '0.25rem' }}>
            RIS Admin
          </div>
        </div>
        <nav style={{ marginTop: '1rem' }}>
          {navItems.map((item) => {
            const isActive = item.exact
              ? pathname === item.href
              : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.625rem',
                  padding: '0.625rem 1.5rem',
                  fontSize: '0.875rem',
                  color: isActive ? 'white' : 'rgba(255,255,255,0.6)',
                  background: isActive ? 'rgba(59,130,246,0.3)' : 'transparent',
                  borderLeft: isActive ? '3px solid #3b82f6' : '3px solid transparent',
                  textDecoration: 'none',
                  transition: 'all 0.15s',
                }}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div style={{ position: 'absolute', bottom: '1.5rem', left: 0, right: 0, padding: '0 1.5rem' }}>
          <Link
            href="/"
            style={{
              display: 'block',
              fontSize: '0.75rem',
              color: 'rgba(255,255,255,0.4)',
              textDecoration: 'none',
            }}
          >
            ← Zur oefentlichen Seite
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, marginLeft: '240px', padding: '2rem', overflow: 'auto' }}>
        {children}
      </main>
    </div>
  );
}
