'use client';
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

interface Meeting {
  id: string;
  name: string;
  start: string;
  end?: string;
  meeting_state: string;
  cancelled: boolean;
  organization?: string;
}

interface MeetingListResponse {
  data: Meeting[];
  pagination: {
    totalElements: number;
    currentPage: number;
    totalPages: number;
  };
}

const stateLabels: Record<string, { label: string; bg: string; color: string }> = {
  scheduled: { label: 'Geplant', bg: '#dbeafe', color: '#1d4ed8' },
  invited: { label: 'Eingeladen', bg: '#e0e7ff', color: '#4338ca' },
  running: { label: 'Laufend', bg: '#fef3c7', color: '#d97706' },
  completed: { label: 'Abgeschlossen', bg: '#dcfce7', color: '#166534' },
  cancelled: { label: 'Abgesagt', bg: '#fee2e2', color: '#991b1b' },
};

export default function SitzungenAdmin() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadMeetings = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/admin/meetings?page=${page}&per_page=20`);
      if (res.ok) {
        const data: MeetingListResponse = await res.json();
        setMeetings(data.data || []);
        setTotal(data.pagination?.totalElements || 0);
      } else {
        setError(`Fehler ${res.status}`);
      }
    } catch {
      setError('Verbindungsfehler');
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => { loadMeetings(); }, [loadMeetings]);

  function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString('de-DE', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>Sitzungen</h1>
          <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.25rem' }}>
            {total} Sitzungen gesamt
          </p>
        </div>
        <Link
          href="/sitzungen"
          style={{
            background: '#f1f5f9', color: '#374151', border: '1px solid #e2e8f0',
            padding: '0.5rem 1rem', borderRadius: '0.375rem',
            textDecoration: 'none', fontSize: '0.875rem', fontWeight: 500,
          }}
        >
          Oeffentliche Ansicht →
        </Link>
      </div>

      {error && (
        <div style={{
          background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '0.375rem',
          padding: '0.75rem 1rem', color: '#991b1b', fontSize: '0.875rem', marginBottom: '1rem',
        }}>
          {error}
        </div>
      )}

      <div style={{ background: 'white', borderRadius: '0.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f8fafc' }}>
              {['Name', 'Start', 'Ende', 'Status', 'Aktionen'].map((h) => (
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
              <tr><td colSpan={5} style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>Lade...</td></tr>
            ) : meetings.length === 0 ? (
              <tr><td colSpan={5} style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>Keine Sitzungen gefunden</td></tr>
            ) : (
              meetings.map((meeting, i) => {
                const state = stateLabels[meeting.meeting_state] || { label: meeting.meeting_state, bg: '#f1f5f9', color: '#374151' };
                return (
                  <tr key={meeting.id} style={{ borderTop: i > 0 ? '1px solid #f1f5f9' : undefined }}>
                    <td style={{ padding: '0.875rem 1rem' }}>
                      <div style={{ fontWeight: 500, color: '#0f172a' }}>{meeting.name}</div>
                      {meeting.cancelled && (
                        <span style={{ fontSize: '0.75rem', color: '#dc2626' }}>Abgesagt</span>
                      )}
                    </td>
                    <td style={{ padding: '0.875rem 1rem', fontSize: '0.875rem', color: '#374151' }}>
                      {meeting.start ? formatDate(meeting.start) : '–'}
                    </td>
                    <td style={{ padding: '0.875rem 1rem', fontSize: '0.875rem', color: '#64748b' }}>
                      {meeting.end ? formatDate(meeting.end) : '–'}
                    </td>
                    <td style={{ padding: '0.875rem 1rem' }}>
                      <span style={{
                        background: state.bg, color: state.color,
                        padding: '0.125rem 0.5rem', borderRadius: '9999px',
                        fontSize: '0.75rem', fontWeight: 500,
                      }}>
                        {state.label}
                      </span>
                    </td>
                    <td style={{ padding: '0.875rem 1rem' }}>
                      <Link
                        href={`/sitzungen/${meeting.id}`}
                        style={{ color: '#3b82f6', textDecoration: 'none', fontSize: '0.875rem' }}
                      >
                        Details →
                      </Link>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>

        {/* Pagination */}
        {total > 20 && (
          <div style={{
            padding: '1rem', borderTop: '1px solid #f1f5f9',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <span style={{ fontSize: '0.875rem', color: '#64748b' }}>
              Seite {page} von {Math.ceil(total / 20)}
            </span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                style={{
                  background: '#f1f5f9', border: '1px solid #e2e8f0',
                  padding: '0.375rem 0.75rem', borderRadius: '0.25rem',
                  cursor: page === 1 ? 'not-allowed' : 'pointer', fontSize: '0.875rem',
                  opacity: page === 1 ? 0.5 : 1,
                }}
              >
                Zurueck
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page >= Math.ceil(total / 20)}
                style={{
                  background: '#3b82f6', color: 'white', border: 'none',
                  padding: '0.375rem 0.75rem', borderRadius: '0.25rem',
                  cursor: page >= Math.ceil(total / 20) ? 'not-allowed' : 'pointer',
                  fontSize: '0.875rem', opacity: page >= Math.ceil(total / 20) ? 0.5 : 1,
                }}
              >
                Weiter
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
