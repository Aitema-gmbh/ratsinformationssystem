type StatusType = 'aktiv' | 'abgeschlossen' | 'geplant' | 'verschoben';

const STATUS_CONFIG: Record<StatusType, { label: string; color: string; bg: string; pulse: boolean }> = {
  aktiv: { label: 'Aktiv', color: '#059669', bg: '#dcfce7', pulse: true },
  abgeschlossen: { label: 'Abgeschlossen', color: '#64748b', bg: '#f1f5f9', pulse: false },
  geplant: { label: 'Geplant', color: '#2563eb', bg: '#dbeafe', pulse: false },
  verschoben: { label: 'Verschoben', color: '#d97706', bg: '#fef3c7', pulse: false },
};

export function StatusBadge({ status }: { status: StatusType }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.geplant;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '0.375rem',
      padding: '0.25rem 0.75rem', borderRadius: '9999px',
      fontSize: '0.75rem', fontWeight: 600,
      color: config.color, background: config.bg,
    }}>
      {config.pulse && (
        <span style={{
          width: 6, height: 6, borderRadius: '50%',
          background: config.color, animation: 'pulse-glow 2s infinite',
          display: 'inline-block'
        }} />
      )}
      {config.label}
    </span>
  );
}
