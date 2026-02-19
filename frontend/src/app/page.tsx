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
      <p className="text-gray-500 text-sm">
        Keine anstehenden Sitzungen gefunden.
      </p>
    );
  }

  return (
    <ul className="divide-y divide-gray-200" role="list">
      {meetings.map((meeting: any) => (
        <li key={meeting.id} className="py-3">
          <a
            href={`/meetings/${encodeURIComponent(meeting.id)}`}
            className="block hover:bg-gray-50 -mx-2 px-2 py-1 rounded"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">
                {meeting.name || "Sitzung"}
              </span>
              {meeting.start && (
                <time
                  dateTime={meeting.start}
                  className="text-xs text-gray-500"
                >
                  {new Date(meeting.start).toLocaleDateString("de-DE", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </time>
              )}
            </div>
            {meeting.meetingState && (
              <span className="inline-block mt-1 px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">
                {meeting.meetingState}
              </span>
            )}
          </a>
        </li>
      ))}
    </ul>
  );
}

function PapersList({ papers }: { papers: any[] }) {
  if (!papers.length) {
    return (
      <p className="text-gray-500 text-sm">Keine Vorlagen gefunden.</p>
    );
  }

  return (
    <ul className="divide-y divide-gray-200" role="list">
      {papers.map((paper: any) => (
        <li key={paper.id} className="py-3">
          <a
            href={`/papers/${encodeURIComponent(paper.id)}`}
            className="block hover:bg-gray-50 -mx-2 px-2 py-1 rounded"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-sm font-medium text-gray-900">
                  {paper.name}
                </span>
                {paper.reference && (
                  <span className="ml-2 text-xs text-gray-500">
                    ({paper.reference})
                  </span>
                )}
              </div>
              {paper.paperType && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                  {paper.paperType}
                </span>
              )}
            </div>
          </a>
        </li>
      ))}
    </ul>
  );
}

export default async function HomePage() {
  const [meetings, papers] = await Promise.all([
    getUpcomingMeetings(),
    getRecentPapers(),
  ]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Section */}
      <section className="text-center mb-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Ratsinformationssystem
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Transparente Informationen zu Sitzungen, Vorlagen und Beschluessen
          Ihrer Kommune. Alle Daten sind ueber die offene OParl-Schnittstelle
          verfuegbar.
        </p>

        {/* Search Bar */}
        <form
          action="/search"
          method="get"
          className="mt-6 max-w-xl mx-auto"
          role="search"
        >
          <div className="flex">
            <label htmlFor="hero-search" className="sr-only">
              Volltextsuche
            </label>
            <input
              id="hero-search"
              type="search"
              name="q"
              placeholder="Vorlagen, Sitzungen, Personen durchsuchen..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Suchen
            </button>
          </div>
        </form>
      </section>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upcoming Meetings */}
        <section aria-labelledby="meetings-heading">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2
                id="meetings-heading"
                className="text-lg font-semibold text-gray-900"
              >
                Anstehende Sitzungen
              </h2>
              <a
                href="/meetings"
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Alle anzeigen
              </a>
            </div>
            <Suspense
              fallback={
                <p className="text-gray-400 text-sm">Lade Sitzungen...</p>
              }
            >
              <MeetingsList meetings={meetings} />
            </Suspense>
          </div>
        </section>

        {/* Recent Papers */}
        <section aria-labelledby="papers-heading">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2
                id="papers-heading"
                className="text-lg font-semibold text-gray-900"
              >
                Aktuelle Vorlagen
              </h2>
              <a
                href="/papers"
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Alle anzeigen
              </a>
            </div>
            <Suspense
              fallback={
                <p className="text-gray-400 text-sm">Lade Vorlagen...</p>
              }
            >
              <PapersList papers={papers} />
            </Suspense>
          </div>
        </section>
      </div>

      {/* Info Cards */}
      <section className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
          <div className="text-3xl mb-2" aria-hidden="true">
            &#128197;
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">
            Sitzungskalender
          </h3>
          <p className="text-sm text-gray-600">
            Ueberblick ueber alle oeffentlichen Sitzungen mit
            Tagesordnungen und Protokollen.
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
          <div className="text-3xl mb-2" aria-hidden="true">
            &#128196;
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">
            Vorlagensuche
          </h3>
          <p className="text-sm text-gray-600">
            Durchsuchen Sie alle Beschlussvorlagen, Antraege und Anfragen.
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
          <div className="text-3xl mb-2" aria-hidden="true">
            &#128279;
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">
            Offene Daten (OParl)
          </h3>
          <p className="text-sm text-gray-600">
            Alle Daten sind ueber die standardisierte OParl-Schnittstelle
            frei zugaenglich.
          </p>
        </div>
      </section>
    </div>
  );
}
