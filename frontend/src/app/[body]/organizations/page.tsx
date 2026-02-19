/**
 * aitema|RIS - Gremien Page
 * Displays all organizations (committees, factions) for a body.
 */
"use client";

import { useState, useEffect } from "react";
import { apiClient, type OParlOrganization } from "@/lib/api";

interface OrganizationsPageProps {
  params: { body: string };
}

export default function OrganizationsPage({ params }: OrganizationsPageProps) {
  const [organizations, setOrganizations] = useState<OParlOrganization[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>("");

  useEffect(() => {
    async function loadOrganizations() {
      setLoading(true);
      try {
        const data = await apiClient.getOrganizations(params.body, {
          organizationType: filterType || undefined,
        });
        setOrganizations(data.data || []);
      } catch (error) {
        console.error("Failed to load organizations:", error);
      } finally {
        setLoading(false);
      }
    }
    loadOrganizations();
  }, [params.body, filterType]);

  const orgTypes = [
    { value: "", label: "Alle" },
    { value: "Rat", label: "Rat" },
    { value: "Ausschuss", label: "Ausschuesse" },
    { value: "Fraktion", label: "Fraktionen" },
    { value: "Beirat", label: "Beiraete" },
    { value: "Kommission", label: "Kommissionen" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Gremien und Fraktionen
      </h1>

      {/* Filter Tabs */}
      <div className="mb-6 border-b border-gray-200" role="tablist" aria-label="Gremientyp filtern">
        <nav className="flex space-x-4">
          {orgTypes.map((type) => (
            <button
              key={type.value}
              role="tab"
              aria-selected={filterType === type.value}
              onClick={() => setFilterType(type.value)}
              className={`px-3 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
                filterType === type.value
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              {type.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Organization Grid */}
      {loading ? (
        <div className="text-center py-12 text-gray-500" role="status">
          <p>Gremien werden geladen...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {organizations.map((org) => (
            <article
              key={org.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <h2 className="text-lg font-semibold text-gray-900">
                  <a
                    href={`/${params.body}/organizations/${encodeURIComponent(org.id)}`}
                    className="hover:text-blue-600"
                  >
                    {org.name}
                  </a>
                </h2>
              </div>

              {org.shortName && (
                <p className="text-sm text-gray-500 mb-2">{org.shortName}</p>
              )}

              {org.organizationType && (
                <span className="inline-block px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-600 mb-3">
                  {org.organizationType}
                </span>
              )}

              <div className="flex items-center justify-between text-sm text-gray-500 mt-3 pt-3 border-t border-gray-100">
                <span>
                  {org.startDate
                    ? `Seit ${new Date(org.startDate).toLocaleDateString("de-DE")}`
                    : ""}
                </span>
                <a
                  href={`/${params.body}/organizations/${encodeURIComponent(org.id)}`}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  Details &rarr;
                </a>
              </div>
            </article>
          ))}

          {organizations.length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-500">
              <p>Keine Gremien gefunden.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
