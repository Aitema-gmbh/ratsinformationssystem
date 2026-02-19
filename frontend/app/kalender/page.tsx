'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';

interface Meeting {
  id: string;
  name: string;
  start: string;
  end?: string;
  meeting_state: string;
  cancelled: boolean;
  organization?: string;
  organizationName?: string;
}

const WEEKDAYS = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
const MONTHS = [
  'Januar', 'Februar', 'Maerz', 'April', 'Mai', 'Juni',
  'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember',
];

const stateColors: Record<string, string> = {
  scheduled: '#3b82f6',
  invited: '#8b5cf6',
  running: '#f59e0b',
  completed: '#16a34a',
  cancelled: '#dc2626',
};

const stateLabels: Record<string, string> = {
  scheduled: 'Geplant',
  invited: 'Eingeladen',
  running: 'Laufend',
  completed: 'Abgeschlossen',
  cancelled: 'Abgesagt',
};

export default function KalenderPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    return { year: now.getFullYear(), month: now.getMonth() };
  });
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  useEffect(() => {
    setLoading(true);
    const startDate = new Date(currentMonth.year, currentMonth.month, 1);
    const endDate = new Date(currentMonth.year, currentMonth.month + 1, 0);

    const params = new URLSearchParams({
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0],
    });

    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/meetings?${params}`)
      .then(r => r.json())
      .then(data => {
        setMeetings(data.data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [currentMonth]);

  const meetingsByDate = useMemo(() => {
    const map: Record<string, Meeting[]> = {};
    meetings.forEach(m => {
      if (!m.start) return;
      const dateKey = m.start.split('T')[0];
      if (!map[dateKey]) map[dateKey] = [];
      map[dateKey].push(m);
    });
    return map;
  }, [meetings]);

  const calendarDays = useMemo(() => {
    const firstDay = new Date(currentMonth.year, currentMonth.month, 1);
    const lastDay = new Date(currentMonth.year, currentMonth.month + 1, 0);

    let startDow = firstDay.getDay();
    startDow = startDow === 0 ? 6 : startDow - 1;

    const days: Array<{ date: Date; isCurrentMonth: boolean }> = [];

    for (let i = startDow - 1; i >= 0; i--) {
      const d = new Date(currentMonth.year, currentMonth.month, -i);
      days.push({ date: d, isCurrentMonth: false });
    }

    for (let d = 1; d <= lastDay.getDate(); d++) {
      days.push({
        date: new Date(currentMonth.year, currentMonth.month, d),
        isCurrentMonth: true,
      });
    }

    const remaining = 7 - (days.length % 7);
    if (remaining < 7) {
      for (let d = 1; d <= remaining; d++) {
        days.push({
          date: new Date(currentMonth.year, currentMonth.month + 1, d),
          isCurrentMonth: false,
        });
      }
    }

    return days;
  }, [currentMonth]);

  const goToPrevMonth = useCallback(() => {
    setCurrentMonth(prev => {
      if (prev.month === 0) return { year: prev.year - 1, month: 11 };
      return { year: prev.year, month: prev.month - 1 };
    });
    setSelectedDate(null);
  }, []);

  const goToNextMonth = useCallback(() => {
    setCurrentMonth(prev => {
      if (prev.month === 11) return { year: prev.year + 1, month: 0 };
      return { year: prev.year, month: prev.month + 1 };
    });
    setSelectedDate(null);
  }, []);

  const goToToday = useCallback(() => {
    const now = new Date();
    setCurrentMonth({ year: now.getFullYear(), month: now.getMonth() });
    setSelectedDate(null);
  }, []);

  const formatTime = (iso: string) =>
    new Intl.DateTimeFormat('de-DE', { hour: '2-digit', minute: '2-digit' }).format(new Date(iso));

  const formatDateLong = (iso: string) =>
    new Intl.DateTimeFormat('de-DE', {
      weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
    }).format(new Date(iso));

  const todayStr = new Date().toISOString().split('T')[0];

  const selectedMeetings = selectedDate ? (meetingsByDate[selectedDate] || []) : [];

  const icalUrl = `${process.env.NEXT_PUBLIC_API_URL || ''}/export/calendar/default.ics`;

  if (isMobile) {
    const sortedDates = Object.keys(meetingsByDate).sort();
    return (
      <div>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Sitzungskalender</h1>
        <p style={{ color: '#6b7280', marginBottom: '1rem', fontSize: '0.875rem' }}>
          {MONTHS[currentMonth.month]} {currentMonth.year}
        </p>
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          <button onClick={goToPrevMonth} style={navBtnStyle} aria-label="Vorheriger Monat">
            Zurueck
          </button>
          <button onClick={goToToday} style={navBtnStyle}>Heute</button>
          <button onClick={goToNextMonth} style={navBtnStyle} aria-label="Naechster Monat">
            Vor
          </button>
          <a href={icalUrl} style={{ ...navBtnStyle, textDecoration: 'none', textAlign: 'center' }}>
            Kalender abonnieren
          </a>
        </div>
        {loading ? (
          <p role="status" style={{ color: '#6b7280', textAlign: 'center', padding: '3rem' }}>Laden...</p>
        ) : sortedDates.length === 0 ? (
          <p style={{ color: '#9ca3af', textAlign: 'center', padding: '3rem' }}>Keine Sitzungen in diesem Monat.</p>
        ) : (
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {sortedDates.map(dateKey => (
              <li key={dateKey}>
                <h2 style={{ fontSize: '0.875rem', fontWeight: 600, color: '#374151', marginBottom: '0.5rem' }}>
                  {formatDateLong(dateKey)}
                </h2>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {meetingsByDate[dateKey].map(m => (
                    <li key={m.id}>
                      <a href={`/sitzungen/${m.id}`} style={meetingCardStyle(m.meeting_state)}>
                        <span style={{ fontWeight: 500 }}>{m.name}</span>
                        <span style={{ color: '#6b7280', fontSize: '0.8125rem' }}>
                          {formatTime(m.start)} - {stateLabels[m.meeting_state] || m.meeting_state}
                        </span>
                      </a>
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>Sitzungskalender</h1>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Alle Sitzungstermine im Ueberblick
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button onClick={goToPrevMonth} style={navBtnStyle} aria-label="Vorheriger Monat">
            &larr;
          </button>
          <span style={{ fontWeight: 600, minWidth: '160px', textAlign: 'center' }}>
            {MONTHS[currentMonth.month]} {currentMonth.year}
          </span>
          <button onClick={goToNextMonth} style={navBtnStyle} aria-label="Naechster Monat">
            &rarr;
          </button>
          <button onClick={goToToday} style={{ ...navBtnStyle, marginLeft: '0.5rem' }}>Heute</button>
          <a
            href={icalUrl}
            style={{
              ...navBtnStyle,
              textDecoration: 'none',
              textAlign: 'center',
              background: '#1e3a5f',
              color: '#fff',
              borderColor: '#1e3a5f',
            }}
            aria-label="Kalender als iCal abonnieren"
          >
            Kalender abonnieren
          </a>
        </div>
      </div>

      {loading ? (
        <p role="status" style={{ color: '#6b7280', textAlign: 'center', padding: '3rem' }}>Laden...</p>
      ) : (
        <div style={{ display: 'flex', gap: '1.5rem' }}>
          {/* Calendar Grid */}
          <div style={{ flex: '1 1 auto' }}>
            <div
              role="grid"
              aria-label={`Kalender ${MONTHS[currentMonth.month]} ${currentMonth.year}`}
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(7, 1fr)',
                border: '1px solid #e5e7eb',
                borderRadius: '0.5rem',
                overflow: 'hidden',
                background: '#fff',
              }}
            >
              {WEEKDAYS.map(day => (
                <div
                  key={day}
                  role="columnheader"
                  style={{
                    padding: '0.5rem',
                    textAlign: 'center',
                    fontWeight: 600,
                    fontSize: '0.8125rem',
                    color: '#374151',
                    background: '#f9fafb',
                    borderBottom: '2px solid #e5e7eb',
                  }}
                >
                  {day}
                </div>
              ))}

              {calendarDays.map(({ date, isCurrentMonth }, idx) => {
                const dateKey = date.toISOString().split('T')[0];
                const dayMeetings = meetingsByDate[dateKey] || [];
                const isToday = dateKey === todayStr;
                const isSelected = dateKey === selectedDate;

                return (
                  <div
                    key={idx}
                    role="gridcell"
                    tabIndex={isCurrentMonth ? 0 : -1}
                    aria-label={`${date.getDate()}. ${MONTHS[date.getMonth()]}, ${dayMeetings.length} Sitzungen`}
                    aria-selected={isSelected}
                    onClick={() => setSelectedDate(dateKey)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        setSelectedDate(dateKey);
                      }
                    }}
                    style={{
                      minHeight: '80px',
                      padding: '0.375rem',
                      borderRight: '1px solid #f3f4f6',
                      borderBottom: '1px solid #f3f4f6',
                      cursor: isCurrentMonth ? 'pointer' : 'default',
                      background: isSelected ? '#eff6ff' : isToday ? '#fffbeb' : '#fff',
                      opacity: isCurrentMonth ? 1 : 0.4,
                    }}
                  >
                    <div style={{
                      fontSize: '0.8125rem',
                      fontWeight: isToday ? 700 : 400,
                      color: isToday ? '#1e3a5f' : '#374151',
                      marginBottom: '0.25rem',
                    }}>
                      {date.getDate()}
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2px' }}>
                      {dayMeetings.slice(0, 3).map(m => (
                        <div
                          key={m.id}
                          title={m.name}
                          style={{
                            width: '100%',
                            padding: '1px 4px',
                            borderRadius: '3px',
                            fontSize: '0.625rem',
                            fontWeight: 500,
                            color: '#fff',
                            background: stateColors[m.meeting_state] || '#6b7280',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {m.name}
                        </div>
                      ))}
                      {dayMeetings.length > 3 && (
                        <div style={{ fontSize: '0.625rem', color: '#6b7280' }}>
                          +{dayMeetings.length - 3}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Sidebar: Selected day detail */}
          <div style={{ width: '300px', flexShrink: 0 }} aria-live="polite">
            {selectedDate ? (
              <div>
                <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>
                  {formatDateLong(selectedDate)}
                </h2>
                {selectedMeetings.length === 0 ? (
                  <p style={{ color: '#9ca3af', fontSize: '0.875rem' }}>Keine Sitzungen an diesem Tag.</p>
                ) : (
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {selectedMeetings.map(m => (
                      <li key={m.id}>
                        <a href={`/sitzungen/${m.id}`} style={meetingCardStyle(m.meeting_state)}>
                          <div style={{ fontWeight: 500, fontSize: '0.875rem' }}>{m.name}</div>
                          <div style={{ fontSize: '0.8125rem', color: '#6b7280', marginTop: '0.25rem' }}>
                            {formatTime(m.start)}
                            {m.end ? ` - ${formatTime(m.end)}` : ''}
                          </div>
                          <span
                            style={{
                              display: 'inline-block',
                              marginTop: '0.375rem',
                              padding: '0.125rem 0.5rem',
                              borderRadius: '9999px',
                              fontSize: '0.6875rem',
                              fontWeight: 600,
                              color: '#fff',
                              background: stateColors[m.meeting_state] || '#6b7280',
                            }}
                          >
                            {stateLabels[m.meeting_state] || m.meeting_state}
                          </span>
                        </a>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ) : (
              <p style={{ color: '#9ca3af', fontSize: '0.875rem' }}>
                Klicken Sie auf einen Tag, um die Sitzungen anzuzeigen.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

const navBtnStyle: React.CSSProperties = {
  padding: '0.5rem 1rem',
  borderRadius: '0.375rem',
  border: '1px solid #d1d5db',
  background: '#fff',
  color: '#374151',
  cursor: 'pointer',
  fontWeight: 600,
  fontSize: '0.875rem',
  minHeight: '44px',
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
};

function meetingCardStyle(state: string): React.CSSProperties {
  return {
    display: 'block',
    background: '#fff',
    border: '1px solid #e5e7eb',
    borderRadius: '0.375rem',
    padding: '0.75rem 1rem',
    textDecoration: 'none',
    color: 'inherit',
    borderLeft: `3px solid ${stateColors[state] || '#6b7280'}`,
  };
}
