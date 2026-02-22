/**
 * aitema|RIS - Landing Page / Buergerportal
 * Public-facing page showing upcoming meetings, recent papers, and search.
 */

import { Suspense } from "react";

async function getUpcomingMeetings() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  try {
    const res = await fetch(`${apiUrl}/api/v1/oparl/body/default/meeting?per_page=5`, {
      next: { revalidate: 300 },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.data || [];
  } catch {
    return [];
  }
}

async function getRecentPapers() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  try {
    const res = await fetch(`${apiUrl}/api/v1/oparl/body/default/paper?per_page=5`, {
      next: { revalidate: 300 },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.data || [];
  } catch {
    return [];
  }
}

function MeetingsList({ meetings }: { meetings: any[] }) {
  if (!meetings.length) {
    return (
      <div className="flex flex-col items-center py-8 text-slate-400">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p className="text-sm">Keine anstehenden Sitzungen gefunden.</p>
      </div>
    );
  }

  return (
    <ul className="space-y-2" role="list">
      {meetings.map((meeting: any) => {
        const dateObj = meeting.start ? new Date(meeting.start) : null;
        return (
          <li key={meeting.id}>
            <a
              href={`/default/meetings/${encodeURIComponent(meeting.id)}`}
              className="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 border border-transparent hover:border-slate-100 transition-all duration-150 group"
            >
              {/* Date Badge */}
              <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-blue-50 border border-blue-100 flex flex-col items-center justify-center text-blue-700">
                {dateObj ? (
                  <>
                    <span className="text-[10px] font-semibold uppercase leading-none opacity-70">
                      {dateObj.toLocaleDateString("de-DE", { month: "short" })}
                    </span>
                    <span className="text-xl font-bold leading-tight">
                      {dateObj.getDate()}
                    </span>
                  </>
                ) : (
                  <span className="text-xs text-slate-400">–</span>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-800 truncate group-hover:text-blue-700 transition-colors">
                  {meeting.name || "Sitzung"}
                </p>
                {dateObj && (
                  <time
                    dateTime={meeting.start}
                    className="text-xs text-slate-500"
                  >
                    {dateObj.toLocaleDateString("de-DE", {
                      weekday: "short",
                      day: "2-digit",
                      month: "2-digit",
                      year: "numeric",
                    })}{" "}
                    {dateObj.toLocaleTimeString("de-DE", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })} Uhr
                  </time>
                )}
              </div>

              {/* Status */}
              {meeting.meetingState && (
                <span className="aitema-badge bg-blue-50 text-blue-700 border border-blue-100 whitespace-nowrap">
                  {meeting.meetingState}
                </span>
              )}

              {/* Arrow */}
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-slate-300 group-hover:text-blue-400 transition-colors flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </a>
          </li>
        );
      })}
    </ul>
  );
}

function PapersList({ papers }: { papers: any[] }) {
  const typeColors: Record<string, string> = {
    Beschlussvorlage: "bg-blue-50 text-blue-700 border-blue-100",
    Antrag:           "bg-violet-50 text-violet-700 border-violet-100",
    Anfrage:          "bg-emerald-50 text-emerald-700 border-emerald-100",
    Mitteilung:       "bg-amber-50 text-amber-700 border-amber-100",
    Bericht:          "bg-slate-100 text-slate-600 border-slate-200",
    Stellungnahme:    "bg-orange-50 text-orange-700 border-orange-100",
  };

  if (!papers.length) {
    return (
      <div className="flex flex-col items-center py-8 text-slate-400">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="text-sm">Keine Vorlagen gefunden.</p>
      </div>
    );
  }

  return (
    <ul className="space-y-2" role="list">
      {papers.map((paper: any) => {
        const badgeClass = paper.paperType
          ? (typeColors[paper.paperType] || "bg-slate-100 text-slate-600 border-slate-200")
          : "";
        return (
          <li key={paper.id}>
            <a
              href={`/default/papers/${encodeURIComponent(paper.id)}`}
              className="flex items-start gap-3 p-3 rounded-xl hover:bg-slate-50 border border-transparent hover:border-slate-100 transition-all duration-150 group"
            >
              {/* Doc icon */}
              <div className="flex-shrink-0 mt-0.5 w-9 h-9 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-800 group-hover:text-blue-700 transition-colors line-clamp-2">
                  {paper.name}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  {paper.reference && (
                    <span className="text-xs font-mono text-slate-400">{paper.reference}</span>
                  )}
                  {paper.date && (
                    <time dateTime={paper.date} className="text-xs text-slate-400">
                      {new Date(paper.date).toLocaleDateString("de-DE")}
                    </time>
                  )}
                </div>
              </div>

              {/* Type Badge */}
              {paper.paperType && (
                <span className={`aitema-badge border whitespace-nowrap flex-shrink-0 ${badgeClass}`}>
                  {paper.paperType}
                </span>
              )}
            </a>
          </li>
        );
      })}
    </ul>
  );
}

export default async function HomePage() {
  const [meetings, papers] = await Promise.all([
    getUpcomingMeetings(),
    getRecentPapers(),
  ]);

  return (
    <div className="flex flex-col">

      {/* ======== HERO SECTION ======== */}
      <section className="bg-aitema-gradient text-white py-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Decorative circles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
          <div className="absolute -top-20 -right-20 w-96 h-96 rounded-full bg-blue-400/10 blur-3xl" />
          <div className="absolute -bottom-20 -left-20 w-80 h-80 rounded-full bg-blue-600/10 blur-3xl" />
        </div>

        <div className="max-w-4xl mx-auto text-center relative">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-200 text-xs font-medium mb-6">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-300"></span>
            </span>
            OParl 1.1 konform &middot; Open Source
          </div>

          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4 leading-tight">
            Transparenz fuer{" "}
            <span className="text-blue-300">unsere Stadt</span>
          </h1>
          <p className="text-lg text-slate-300 max-w-2xl mx-auto mb-8 leading-relaxed">
            Alle Sitzungen, Vorlagen und Beschluesse Ihrer Kommune &mdash; offen, durchsuchbar und maschinenlesbar per OParl-Schnittstelle.
          </p>

          {/* Hero Search */}
          <form
            action="/search"
            method="get"
            className="mt-6 max-w-2xl mx-auto"
            role="search"
          >
            <div className="flex rounded-xl overflow-hidden shadow-xl ring-1 ring-white/20">
              <label htmlFor="hero-search" className="sr-only">
                Volltextsuche
              </label>
              <div className="relative flex-1">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  id="hero-search"
                  type="search"
                  name="q"
                  placeholder="Vorlagen, Sitzungen, Personen durchsuchen..."
                  className="w-full pl-12 pr-4 py-4 bg-white text-slate-900 text-sm sm:text-base placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
                />
              </div>
              <button
                type="submit"
                className="px-6 py-4 bg-blue-500 hover:bg-blue-600 text-white font-semibold text-sm sm:text-base transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-300 whitespace-nowrap"
              >
                Suchen
              </button>
            </div>
          </form>

          {/* Quick Links */}
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <a href="/default/meetings" className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-sm text-white transition-colors duration-150">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Sitzungen
            </a>
            <a href="/default/papers" className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-sm text-white transition-colors duration-150">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Vorlagen
            </a>
            <a href="/default/organizations" className="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 text-sm text-white transition-colors duration-150">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Gremien
            </a>
          </div>
        </div>
      </section>

      {/* ======== STATS BAR ======== */}
      <section className="bg-white border-b border-slate-100 shadow-sm" aria-label="Statistiken">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 sm:grid-cols-4 divide-x divide-slate-100">
            {[
              { label: "Sitzungen dieses Jahr", value: "–", icon: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" },
              { label: "Vorlagen gesamt", value: "–", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
              { label: "Aktive Gremien", value: "–", icon: "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" },
              { label: "OParl-konform seit", value: "2024", icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" },
            ].map((stat) => (
              <div key={stat.label} className="flex items-center gap-3 py-4 px-4 sm:px-8">
                <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d={stat.icon} />
                  </svg>
                </div>
                <div>
                  <p className="text-xl font-bold text-slate-900 leading-none">{stat.value}</p>
                  <p className="text-xs text-slate-500 mt-0.5 leading-tight">{stat.label}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ======== CONTENT GRID ======== */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          {/* Upcoming Meetings */}
          <div className="aitema-card p-0 overflow-hidden" aria-labelledby="meetings-heading">
            {/* Card Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <h2 id="meetings-heading" className="aitema-section-title">
                  Anstehende Sitzungen
                </h2>
              </div>
              <a
                href="/default/meetings"
                className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1 transition-colors"
              >
                Alle anzeigen
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>
            {/* Card Body */}
            <div className="px-4 py-3">
              <Suspense
                fallback={
                  <div className="space-y-3 py-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="flex items-center gap-3 p-3">
                        <div className="w-12 h-12 rounded-xl bg-slate-100 animate-pulse" />
                        <div className="flex-1 space-y-2">
                          <div className="h-4 bg-slate-100 rounded animate-pulse w-3/4" />
                          <div className="h-3 bg-slate-100 rounded animate-pulse w-1/2" />
                        </div>
                      </div>
                    ))}
                  </div>
                }
              >
                <MeetingsList meetings={meetings} />
              </Suspense>
            </div>
          </div>

          {/* Recent Papers */}
          <div className="aitema-card p-0 overflow-hidden" aria-labelledby="papers-heading">
            {/* Card Header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100 bg-gradient-to-r from-slate-50 to-white">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h2 id="papers-heading" className="aitema-section-title">
                  Aktuelle Vorlagen
                </h2>
              </div>
              <a
                href="/default/papers"
                className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1 transition-colors"
              >
                Alle anzeigen
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>
            {/* Card Body */}
            <div className="px-4 py-3">
              <Suspense
                fallback={
                  <div className="space-y-3 py-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="flex items-center gap-3 p-3">
                        <div className="w-9 h-9 rounded-lg bg-slate-100 animate-pulse" />
                        <div className="flex-1 space-y-2">
                          <div className="h-4 bg-slate-100 rounded animate-pulse w-full" />
                          <div className="h-3 bg-slate-100 rounded animate-pulse w-1/3" />
                        </div>
                      </div>
                    ))}
                  </div>
                }
              >
                <PapersList papers={papers} />
              </Suspense>
            </div>
          </div>

        </div>
      </section>

      {/* ======== FEATURES GRID ======== */}
      <section className="bg-white border-t border-slate-100 py-14" aria-label="Features">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-slate-900">Was Sie hier finden</h2>
            <p className="mt-2 text-slate-500 text-sm max-w-xl mx-auto">
              Das aitema|RIS bietet vollstaendige Transparenz ueber kommunalpolitische Prozesse.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className="aitema-card p-6 text-center group cursor-default">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-600 group-hover:border-blue-600 transition-colors duration-200">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-blue-600 group-hover:text-white transition-colors duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Sitzungskalender</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Ueberblick ueber alle oeffentlichen Sitzungen mit Tagesordnungen, Protokollen und Beschlussvorlagen.
              </p>
              <a href="/default/meetings" className="mt-4 inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 font-medium">
                Zu den Sitzungen
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>

            {/* Feature 2 */}
            <div className="aitema-card p-6 text-center group cursor-default">
              <div className="w-14 h-14 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-center justify-center mx-auto mb-4 group-hover:bg-emerald-600 group-hover:border-emerald-600 transition-colors duration-200">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-emerald-600 group-hover:text-white transition-colors duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Vorlagensuche</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Durchsuchen Sie alle Beschlussvorlagen, Antraege und Anfragen per Volltext oder Filterbedingungen.
              </p>
              <a href="/default/papers" className="mt-4 inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 font-medium">
                Zu den Vorlagen
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </a>
            </div>

            {/* Feature 3 */}
            <div className="aitema-card p-6 text-center group cursor-default">
              <div className="w-14 h-14 rounded-2xl bg-violet-50 border border-violet-100 flex items-center justify-center mx-auto mb-4 group-hover:bg-violet-600 group-hover:border-violet-600 transition-colors duration-200">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-violet-600 group-hover:text-white transition-colors duration-200" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">Offene Daten (OParl)</h3>
              <p className="text-sm text-slate-500 leading-relaxed">
                Alle Daten sind ueber die standardisierte OParl 1.1-Schnittstelle maschinenlesbar und frei zugaenglich.
              </p>
              <a href="/api/v1/oparl/system" className="mt-4 inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 font-medium">
                Zur API
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
