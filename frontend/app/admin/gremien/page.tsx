'use client';
import { useState, useEffect, useCallback } from 'react';

interface Tenant {
  id: string;
  slug: string;
  name: string;
  ags: string | null;
  domain: string | null;
  is_active: boolean;
  is_trial: boolean;
  schema_created: boolean;
  contact_email: string | null;
  contact_name: string | null;
}

interface FormData {
  slug: string;
  name: string;
  ags: string;
  domain: string;
  contact_email: string;
  contact_name: string;
}

const emptyForm: FormData = {
  slug: '',
  name: '',
  ags: '',
  domain: '',
  contact_email: '',
  contact_name: '',
};

export default function GremienAdmin() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<FormData>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTenants = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/admin/tenants');
      if (res.ok) {
        setTenants(await res.json());
      } else {
        setError(`Fehler ${res.status}: Tenants konnten nicht geladen werden`);
      }
    } catch {
      setError('Verbindungsfehler zum Backend');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadTenants(); }, [loadTenants]);

  async function createTenant() {
    if (!form.slug || !form.name) {
      setError('Slug und Name sind Pflichtfelder');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const payload: Record<string, string | undefined> = {
        slug: form.slug,
        name: form.name,
      };
      if (form.ags) payload.ags = form.ags;
      if (form.domain) payload.domain = form.domain;
      if (form.contact_email) payload.contact_email = form.contact_email;
      if (form.contact_name) payload.contact_name = form.contact_name;

      const res = await fetch('/api/admin/tenants', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        setShowForm(false);
        setForm(emptyForm);
        loadTenants();
      } else {
        const data = await res.json();
        setError(data.detail || `Fehler ${res.status}`);
      }
    } catch {
      setError('Verbindungsfehler');
    } finally {
      setSaving(false);
    }
  }

  async function toggleActive(tenant: Tenant) {
    try {
      const res = await fetch(`/api/admin/tenants/${tenant.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !tenant.is_active }),
      });
      if (res.ok) loadTenants();
    } catch {
      setError('Aktion fehlgeschlagen');
    }
  }

  const inputStyle: React.CSSProperties = {
    width: '100%',
    border: '1px solid #e2e8f0',
    borderRadius: '0.375rem',
    padding: '0.5rem 0.75rem',
    fontSize: '0.875rem',
    boxSizing: 'border-box',
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    fontSize: '0.8125rem',
    fontWeight: 500,
    marginBottom: '0.25rem',
    color: '#374151',
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>Gremien / Tenants</h1>
          <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            Mandantenverwaltung — jeder Tenant hat ein eigenes DB-Schema
          </p>
        </div>
        <button
          onClick={() => { setShowForm(true); setError(null); }}
          style={{
            background: '#3b82f6', color: 'white', border: 'none',
            padding: '0.5rem 1rem', borderRadius: '0.375rem',
            cursor: 'pointer', fontWeight: 500, fontSize: '0.875rem',
          }}
        >
          + Neuer Tenant
        </button>
      </div>

      {/* Error */}
      {error && (
        <div style={{
          background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '0.375rem',
          padding: '0.75rem 1rem', color: '#991b1b', fontSize: '0.875rem', marginBottom: '1rem',
        }}>
          {error}
        </div>
      )}

      {/* Create Form */}
      {showForm && (
        <div style={{
          background: 'white', borderRadius: '0.5rem', padding: '1.5rem',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)', marginBottom: '1.5rem',
          border: '1px solid #e2e8f0',
        }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1.25rem', color: '#0f172a' }}>
            Neuen Tenant erstellen
          </h2>
          <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: '1fr 1fr' }}>
            <div>
              <label style={labelStyle}>Slug * <span style={{ color: '#94a3b8', fontWeight: 400 }}>(URL-kompatibel, z.B. "musterstadt")</span></label>
              <input
                value={form.slug}
                onChange={(e) => setForm({ ...form, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') })}
                placeholder="musterstadt"
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>Name *</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Stadt Musterstadt"
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>AGS <span style={{ color: '#94a3b8', fontWeight: 400 }}>(Amtlicher Gemeindeschluessel)</span></label>
              <input
                value={form.ags}
                onChange={(e) => setForm({ ...form, ags: e.target.value })}
                placeholder="09162000"
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>Domain</label>
              <input
                value={form.domain}
                onChange={(e) => setForm({ ...form, domain: e.target.value })}
                placeholder="ris.musterstadt.de"
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>Kontakt Name</label>
              <input
                value={form.contact_name}
                onChange={(e) => setForm({ ...form, contact_name: e.target.value })}
                placeholder="Max Mustermann"
                style={inputStyle}
              />
            </div>
            <div>
              <label style={labelStyle}>Kontakt E-Mail</label>
              <input
                type="email"
                value={form.contact_email}
                onChange={(e) => setForm({ ...form, contact_email: e.target.value })}
                placeholder="admin@musterstadt.de"
                style={inputStyle}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.25rem' }}>
            <button
              onClick={createTenant}
              disabled={saving}
              style={{
                background: saving ? '#93c5fd' : '#3b82f6', color: 'white',
                border: 'none', padding: '0.5rem 1.25rem', borderRadius: '0.375rem',
                cursor: saving ? 'not-allowed' : 'pointer', fontWeight: 500, fontSize: '0.875rem',
              }}
            >
              {saving ? 'Erstelle...' : 'Tenant erstellen'}
            </button>
            <button
              onClick={() => { setShowForm(false); setForm(emptyForm); setError(null); }}
              style={{
                background: '#f1f5f9', border: '1px solid #e2e8f0', color: '#374151',
                padding: '0.5rem 1.25rem', borderRadius: '0.375rem',
                cursor: 'pointer', fontSize: '0.875rem',
              }}
            >
              Abbrechen
            </button>
          </div>
        </div>
      )}

      {/* Table */}
      <div style={{ background: 'white', borderRadius: '0.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f8fafc' }}>
              {['Name / Slug', 'AGS', 'Domain', 'Schema', 'Status', 'Aktionen'].map((h) => (
                <th key={h} style={{
                  padding: '0.75rem 1rem', textAlign: 'left',
                  fontSize: '0.75rem', fontWeight: 600, color: '#64748b',
                  textTransform: 'uppercase', letterSpacing: '0.05em',
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
                  Lade...
                </td>
              </tr>
            ) : tenants.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>
                  Keine Tenants vorhanden. Erstellen Sie den ersten Tenant.
                </td>
              </tr>
            ) : (
              tenants.map((tenant, i) => (
                <tr key={tenant.id} style={{ borderTop: i > 0 ? '1px solid #f1f5f9' : undefined }}>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <div style={{ fontWeight: 600, color: '#0f172a' }}>{tenant.name}</div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', fontFamily: 'monospace' }}>
                      {tenant.slug}
                    </div>
                  </td>
                  <td style={{ padding: '0.875rem 1rem', color: '#64748b', fontSize: '0.875rem' }}>
                    {tenant.ags || '–'}
                  </td>
                  <td style={{ padding: '0.875rem 1rem', color: '#64748b', fontSize: '0.875rem' }}>
                    {tenant.domain || '–'}
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <span style={{
                      background: tenant.schema_created ? '#dcfce7' : '#fef3c7',
                      color: tenant.schema_created ? '#166534' : '#92400e',
                      padding: '0.125rem 0.5rem', borderRadius: '9999px',
                      fontSize: '0.75rem', fontWeight: 500,
                    }}>
                      {tenant.schema_created ? 'Erstellt' : 'Ausstehend'}
                    </span>
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <span style={{
                      background: tenant.is_active ? '#dcfce7' : '#fee2e2',
                      color: tenant.is_active ? '#166534' : '#991b1b',
                      padding: '0.125rem 0.5rem', borderRadius: '9999px',
                      fontSize: '0.75rem', fontWeight: 500,
                    }}>
                      {tenant.is_active ? 'Aktiv' : 'Inaktiv'}
                    </span>
                    {tenant.is_trial && (
                      <span style={{
                        marginLeft: '0.375rem',
                        background: '#fef3c7', color: '#92400e',
                        padding: '0.125rem 0.5rem', borderRadius: '9999px',
                        fontSize: '0.75rem', fontWeight: 500,
                      }}>
                        Trial
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '0.875rem 1rem' }}>
                    <button
                      onClick={() => toggleActive(tenant)}
                      style={{
                        background: 'none', border: '1px solid #e2e8f0',
                        color: '#374151', cursor: 'pointer', fontSize: '0.75rem',
                        padding: '0.25rem 0.625rem', borderRadius: '0.25rem',
                      }}
                    >
                      {tenant.is_active ? 'Deaktivieren' : 'Aktivieren'}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
