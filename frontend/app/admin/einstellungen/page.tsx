import Link from 'next/link';

async function getStatus() {
  const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${backendUrl}/api/v1/admin/status`, { cache: 'no-store' });
    if (res.ok) return res.json();
    return null;
  } catch {
    return null;
  }
}

export default async function EinstellungenPage() {
  const status = await getStatus();

  const envInfo = [
    { label: 'BACKEND_URL', value: process.env.BACKEND_URL || '(nicht gesetzt)' },
    { label: 'NEXT_PUBLIC_API_URL', value: process.env.NEXT_PUBLIC_API_URL || '(nicht gesetzt)' },
    { label: 'NEXT_PUBLIC_OPARL_URL', value: process.env.NEXT_PUBLIC_OPARL_URL || '(nicht gesetzt)' },
  ];

  return (
    <div>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a', marginBottom: '1.5rem' }}>
        Einstellungen
      </h1>

      {/* System Status */}
      <div style={{
        background: 'white', borderRadius: '0.5rem', padding: '1.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '1.5rem',
      }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: '1rem' }}>
          System-Status
        </h2>
        {status ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
              <span style={{
                display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%',
                background: status.status === 'operational' ? '#22c55e' : '#ef4444',
              }} />
              <span style={{ fontWeight: 500, color: '#0f172a' }}>
                {status.status === 'operational' ? 'Backend operativ' : 'Backend-Fehler'}
              </span>
            </div>
            <div style={{ display: 'grid', gap: '0.5rem', gridTemplateColumns: '200px 1fr' }}>
              <span style={{ fontSize: '0.875rem', color: '#64748b' }}>Aktive Tenants:</span>
              <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>{status.active_tenants}</span>
              <span style={{ fontSize: '0.875rem', color: '#64748b' }}>DB-Schemas:</span>
              <span style={{ fontSize: '0.875rem', fontFamily: 'monospace' }}>
                {status.schemas?.join(', ') || '–'}
              </span>
            </div>
          </div>
        ) : (
          <div style={{ color: '#991b1b', fontSize: '0.875rem' }}>
            Backend nicht erreichbar
          </div>
        )}
      </div>

      {/* Umgebungsvariablen */}
      <div style={{
        background: 'white', borderRadius: '0.5rem', padding: '1.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '1.5rem',
      }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: '1rem' }}>
          Konfiguration
        </h2>
        <div style={{ display: 'grid', gap: '0.75rem' }}>
          {envInfo.map((env) => (
            <div key={env.label} style={{
              display: 'grid', gridTemplateColumns: '260px 1fr', gap: '1rem',
              padding: '0.75rem', background: '#f8fafc', borderRadius: '0.375rem',
            }}>
              <code style={{ fontSize: '0.8125rem', color: '#7c3aed', fontWeight: 600 }}>
                {env.label}
              </code>
              <code style={{ fontSize: '0.8125rem', color: '#374151' }}>
                {env.value}
              </code>
            </div>
          ))}
        </div>
      </div>

      {/* API-Links */}
      <div style={{
        background: 'white', borderRadius: '0.5rem', padding: '1.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: '1rem' }}>
          API-Endpunkte
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {[
            { label: 'OParl 1.1 System', href: '/oparl/v1/system' },
            { label: 'Admin API Status', href: '/api/v1/admin/status' },
            { label: 'API Docs (Swagger)', href: '/docs' },
            { label: 'API Docs (ReDoc)', href: '/redoc' },
          ].map((link) => (
            <Link
              key={link.href}
              href={link.href}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
                color: '#3b82f6', textDecoration: 'none', fontSize: '0.875rem',
              }}
            >
              → {link.label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
