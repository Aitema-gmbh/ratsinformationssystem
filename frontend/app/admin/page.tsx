import Link from 'next/link';

interface SystemStatus {
  status: string;
  active_tenants: number;
  schemas: string[];
}

async function getSystemStatus(): Promise<SystemStatus | null> {
  const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${backendUrl}/api/v1/admin/status`, {
      cache: 'no-store',
      headers: { 'Content-Type': 'application/json' },
    });
    if (res.ok) return res.json();
    return null;
  } catch {
    return null;
  }
}

export default async function AdminDashboard() {
  const status = await getSystemStatus();

  const cards = [
    {
      label: 'System-Status',
      value: status?.status === 'operational' ? 'Online' : 'Unbekannt',
      icon: '✅',
      href: '/admin/einstellungen',
      color: '#059669',
      subtitle: 'Backend-Verbindung',
    },
    {
      label: 'Aktive Tenants',
      value: status?.active_tenants ?? '–',
      icon: '🏛️',
      href: '/admin/gremien',
      color: '#1e3a5f',
      subtitle: 'Mandanten verwalten',
    },
    {
      label: 'DB-Schemas',
      value: status?.schemas?.length ?? '–',
      icon: '🗄️',
      href: '/admin/einstellungen',
      color: '#7c3aed',
      subtitle: 'Tenant-Schemas',
    },
    {
      label: 'OParl API',
      value: 'v1.1',
      icon: '📡',
      href: '/oparl/v1/system',
      color: '#3b82f6',
      subtitle: 'API-Endpunkt',
    },
  ];

  const quickLinks = [
    { href: '/admin/gremien', label: 'Tenant erstellen', icon: '+ Tenant' },
    { href: '/sitzungen', label: 'Sitzungen anzeigen', icon: '→ Sitzungen' },
    { href: '/vorlagen', label: 'Vorlagen anzeigen', icon: '→ Vorlagen' },
    { href: '/personen', label: 'Personen anzeigen', icon: '→ Personen' },
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
          Systemuebersicht
        </h1>
        <p style={{ color: '#64748b', fontSize: '0.875rem' }}>
          aitema|RIS Administration — OParl 1.1 konformes Ratsinformationssystem
        </p>
      </div>

      {/* Stats Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem',
      }}>
        {cards.map((card) => (
          <Link key={card.href} href={card.href} style={{ textDecoration: 'none' }}>
            <div style={{
              background: 'white',
              borderRadius: '0.5rem',
              padding: '1.5rem',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              borderTop: `4px solid ${card.color}`,
              cursor: 'pointer',
              transition: 'box-shadow 0.2s',
            }}>
              <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>{card.icon}</div>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: card.color }}>
                {card.value}
              </div>
              <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0f172a', marginTop: '0.25rem' }}>
                {card.label}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.125rem' }}>
                {card.subtitle}
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div style={{
        background: 'white',
        borderRadius: '0.5rem',
        padding: '1.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '1.5rem',
      }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: '1rem' }}>
          Schnellzugriff
        </h2>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          {quickLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '0.5rem 1rem',
                background: '#f1f5f9',
                color: '#1e293b',
                borderRadius: '0.375rem',
                fontSize: '0.875rem',
                fontWeight: 500,
                textDecoration: 'none',
                transition: 'background 0.15s',
              }}
            >
              {link.icon}
            </Link>
          ))}
        </div>
      </div>

      {/* System Info */}
      {status?.schemas && status.schemas.length > 0 && (
        <div style={{
          background: 'white',
          borderRadius: '0.5rem',
          padding: '1.5rem',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: '1rem' }}>
            Aktive DB-Schemas ({status.schemas.length})
          </h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {status.schemas.map((schema) => (
              <span
                key={schema}
                style={{
                  background: '#eff6ff',
                  color: '#1d4ed8',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '9999px',
                  fontSize: '0.8125rem',
                  fontWeight: 500,
                }}
              >
                {schema}
              </span>
            ))}
          </div>
        </div>
      )}

      {!status && (
        <div style={{
          background: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '0.5rem',
          padding: '1rem 1.5rem',
          color: '#991b1b',
          fontSize: '0.875rem',
        }}>
          ⚠️ Backend nicht erreichbar. Bitte Backend-Service pruefen.
        </div>
      )}
    </div>
  );
}
