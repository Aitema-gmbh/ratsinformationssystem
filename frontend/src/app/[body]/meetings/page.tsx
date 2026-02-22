/**
 * aitema|RIS - Sitzungskalender Page
 * Displays meetings for a specific body with calendar and list views.
 */
"use client";

import { useState, useEffect } from "react";
import { apiClient, type OParlMeeting } from "@/lib/api";

interface MeetingsPageProps {
  params: { body: string };
}

export default function MeetingsPage({ params }: MeetingsPageProps) {
  const [meetings, setMeetings] = useState<OParlMeeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<"list" | "calendar">("list");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    async function loadMeetings() {
      setLoading(true);
      try {
        const data = await apiClient.getMeetings(params.body, page);
        setMeetings(data.data || []);
        setTotalPages(data.pagination?.totalPages || 1);
      } catch (error) {
        console.error("Failed to load meetings:", error);
      } finally {
        setLoading(false);
      }
    }
    loadMeetings();
  }, [params.body, page]);

  return (
    <div className="min-h-screen bg-slate-50">

      {/* Page Header */}
      <div className="bg-[#0f172a] text-white px-4 sm:px-6 lg:px-8 py-10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-blue-400 text-sm font-medium mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Sitzungskalender
              </div>
              <h1 className="text-3xl font-bold tracking-tight">Sitzungen</h1>
              <p className="mt-1 text-slate-400 text-sm">
                Alle oeffentlichen Sitzungen des Gremiums
              </p>
            </div>

            {/* View Toggle */}
            <div
              className="flex rounded-xl overflow-hidden border border-white/20 self-start sm:self-center"
              role="group"
              aria-label="Ansicht wechseln"
            >
              <button
                type="button"
                onClick={() => setView("list")}
                className={`px-4 py-2 text-sm font-medium flex items-center gap-2 transition-colors duration-150 ${
                  view === "list"
                    ? "bg-blue-500 text-white"
                    : "bg-white/10 text-slate-300 hover:bg-white/20 hover:text-white"
                }`}
                aria-pressed={view === "list"}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
                Liste
              </button>
              <button
                type="button"
                onClick={() => setView("calendar")}
                className={`px-4 py-2 text-sm font-medium flex items-center gap-2 border-l border-white/20 transition-colors duration-150 ${
                  view === "calendar"
                    ? "bg-blue-500 text-white"
                    : "bg-white/10 text-slate-300 hover:bg-white/20 hover:text-white"
                }`}
                aria-pressed={view === "calendar"}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Kalender
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {loading ? (
          /* Skeleton Loader */
          <div role="status" aria-label="Sitzungen werden geladen">
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="bg-white rounded-xl border border-slate-100 p-5 flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-slate-100 animate-pulse flex-shrink-0" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-slate-100 rounded animate-pulse w-2/3" />
                    <div className="h-3 bg-slate-100 rounded animate-pulse w-1/3" />
                  </div>
                  <div className="w-20 h-6 bg-slate-100 rounded-full animate-pulse" />
                </div>
              ))}
            </div>
          </div>

        ) : view === "list" ? (

          /* ---- LIST VIEW ---- */
          <div className="space-y-3">
            {meetings.length === 0 ? (
              <div className="bg-white rounded-xl border border-slate-100 p-16 text-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-slate-300 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="text-slate-500 font-medium">Keine Sitzungen gefunden.</p>
              </div>
            ) : (
              meetings.map((meeting) => {
                const dateObj = meeting.start ? new Date(meeting.start) : null;
                const isUpcoming = dateObj ? dateObj > new Date() : false;
                return (
                  <article
                    key={meeting.id}
                    className="bg-white rounded-xl border border-slate-100 shadow-card hover:shadow-card-hover transition-all duration-200 overflow-hidden"
                  >
                    <a
                      href={`/${params.body}/meetings/${encodeURIComponent(meeting.id)}`}
                      className="flex flex-col sm:flex-row sm:items-center gap-4 p-5 group"
                    >
                      {/* Date Badge */}
                      <div className={`flex-shrink-0 w-16 h-16 rounded-xl flex flex-col items-center justify-center border ${isUpcoming ? "bg-blue-50 border-blue-200 text-blue-700" : "bg-slate-50 border-slate-200 text-slate-500"}`}>
                        {dateObj ? (
                          <>
                            <span className="text-[10px] font-bold uppercase leading-none opacity-70 tracking-wide">
                              {dateObj.toLocaleDateString("de-DE", { month: "short" })}
                            </span>
                            <span className="text-2xl font-bold leading-tight">
                              {dateObj.getDate()}
                            </span>
                            <span className="text-[10px] leading-none opacity-60">
                              {dateObj.getFullYear()}
                            </span>
                          </>
                        ) : (
                          <span className="text-xs text-slate-400">–</span>
                        )}
                      </div>

                      {/* Main Info */}
                      <div className="flex-1 min-w-0">
                        <h2 className="text-base font-semibold text-slate-800 group-hover:text-blue-700 transition-colors truncate">
                          {meeting.name || "Sitzung"}
                        </h2>
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1">
                          {dateObj && (
                            <time
                              dateTime={meeting.start}
                              className="text-sm text-slate-500 flex items-center gap-1"
                            >
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              {dateObj.toLocaleDateString("de-DE", {
                                weekday: "long",
                                day: "2-digit",
                                month: "long",
                                year: "numeric",
                              })}
                              {", "}
                              {dateObj.toLocaleTimeString("de-DE", {
                                hour: "2-digit",
                                minute: "2-digit",
                              })} Uhr
                            </time>
                          )}
                          {meeting.location && (
                            <span className="text-sm text-slate-400 flex items-center gap-1">
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                              </svg>
                              Siehe Details
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Status & Arrow */}
                      <div className="flex items-center gap-3 flex-shrink-0">
                        <MeetingStatusBadge
                          state={meeting.meetingState}
                          cancelled={meeting.cancelled}
                          upcoming={isUpcoming}
                        />
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-slate-300 group-hover:text-blue-400 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </a>
                  </article>
                );
              })
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <nav
                className="flex items-center justify-between pt-4"
                aria-label="Seitennavigation"
              >
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium bg-white border border-slate-200 rounded-lg shadow-sm text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                  </svg>
                  Zurueck
                </button>
                <span className="text-sm text-slate-500 font-medium">
                  Seite {page} von {totalPages}
                </span>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium bg-white border border-slate-200 rounded-lg shadow-sm text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  Weiter
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </nav>
            )}
          </div>

        ) : (
          /* ---- CALENDAR VIEW ---- */
          <div className="bg-white rounded-xl border border-slate-100 shadow-card p-10 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-14 w-14 text-slate-200 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p className="text-slate-500 font-medium">Kalenderansicht wird implementiert.</p>
            <p className="text-slate-400 text-sm mt-1">Bitte nutzen Sie in der Zwischenzeit die Listenansicht.</p>
          </div>
        )}

      </div>
    </div>
  );
}

function MeetingStatusBadge({
  state,
  cancelled,
  upcoming,
}: {
  state?: string;
  cancelled?: boolean;
  upcoming?: boolean;
}) {
  if (cancelled) {
    return (
      <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold rounded-full bg-red-50 text-red-700 border border-red-100">
        <span className="w-1.5 h-1.5 rounded-full bg-red-500 inline-block" />
        Abgesagt
      </span>
    );
  }

  if (state === "durchgefuehrt") {
    return (
      <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-100">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
        Durchgefuehrt
      </span>
    );
  }

  if (state === "vertagt") {
    return (
      <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold rounded-full bg-orange-50 text-orange-700 border border-orange-100">
        <span className="w-1.5 h-1.5 rounded-full bg-orange-500 inline-block" />
        Vertagt
      </span>
    );
  }

  if (upcoming) {
    return (
      <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold rounded-full bg-blue-50 text-blue-700 border border-blue-100">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-60" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500" />
        </span>
        Anstehend
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold rounded-full bg-slate-100 text-slate-600 border border-slate-200">
      <span className="w-1.5 h-1.5 rounded-full bg-slate-400 inline-block" />
      {state || "Geplant"}
    </span>
  );
}
