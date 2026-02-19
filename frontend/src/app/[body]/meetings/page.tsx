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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Sitzungskalender</h1>

        {/* View Toggle */}
        <div className="flex rounded-md shadow-sm" role="group" aria-label="Ansicht wechseln">
          <button
            type="button"
            onClick={() => setView("list")}
            className={`px-4 py-2 text-sm font-medium rounded-l-md border ${
              view === "list"
                ? "bg-blue-600 text-white border-blue-600"
                : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
            }`}
            aria-pressed={view === "list"}
          >
            Liste
          </button>
          <button
            type="button"
            onClick={() => setView("calendar")}
            className={`px-4 py-2 text-sm font-medium rounded-r-md border-t border-b border-r ${
              view === "calendar"
                ? "bg-blue-600 text-white border-blue-600"
                : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
            }`}
            aria-pressed={view === "calendar"}
          >
            Kalender
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500" role="status">
          <p>Sitzungen werden geladen...</p>
        </div>
      ) : view === "list" ? (
        /* List View */
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Datum / Uhrzeit
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sitzung
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ort
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {meetings.map((meeting) => (
                <tr key={meeting.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {meeting.start
                      ? new Date(meeting.start).toLocaleDateString("de-DE", {
                          day: "2-digit",
                          month: "2-digit",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })
                      : "n/a"}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <a
                      href={`/${params.body}/meetings/${encodeURIComponent(meeting.id)}`}
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {meeting.name || "Sitzung"}
                    </a>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {meeting.location ? "Siehe Details" : "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <MeetingStatusBadge
                      state={meeting.meetingState}
                      cancelled={meeting.cancelled}
                    />
                  </td>
                </tr>
              ))}
              {meetings.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                    Keine Sitzungen gefunden.
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <nav className="flex items-center justify-between px-6 py-3 border-t border-gray-200" aria-label="Seitennavigation">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Zurueck
              </button>
              <span className="text-sm text-gray-600">
                Seite {page} von {totalPages}
              </span>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 text-sm border rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Weiter
              </button>
            </nav>
          )}
        </div>
      ) : (
        /* Calendar View Placeholder */
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center text-gray-500">
          <p>Kalenderansicht wird implementiert.</p>
        </div>
      )}
    </div>
  );
}

function MeetingStatusBadge({
  state,
  cancelled,
}: {
  state?: string;
  cancelled?: boolean;
}) {
  if (cancelled) {
    return (
      <span className="px-2 py-1 text-xs rounded-full bg-red-100 text-red-700">
        Abgesagt
      </span>
    );
  }

  const colors: Record<string, string> = {
    eingeladen: "bg-yellow-100 text-yellow-700",
    durchgefuehrt: "bg-green-100 text-green-700",
    vertagt: "bg-orange-100 text-orange-700",
  };

  return (
    <span
      className={`px-2 py-1 text-xs rounded-full ${
        colors[state || ""] || "bg-gray-100 text-gray-700"
      }`}
    >
      {state || "Geplant"}
    </span>
  );
}
