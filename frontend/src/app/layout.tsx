import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "aitema|RIS - Ratsinformationssystem",
  description:
    "OParl-First Ratsinformationssystem fuer transparente kommunale Politik",
  openGraph: {
    title: "aitema|RIS",
    description: "Ratsinformationssystem",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {/* Skip Navigation Link for Accessibility */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-4 focus:bg-blue-600 focus:text-white"
        >
          Zum Hauptinhalt springen
        </a>

        {/* Header */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <div className="flex items-center space-x-3">
                <a href="/" className="flex items-center space-x-2">
                  <span className="text-xl font-bold text-blue-700">
                    aitema
                  </span>
                  <span className="text-xl font-light text-gray-400">|</span>
                  <span className="text-xl font-semibold text-gray-900">
                    RIS
                  </span>
                </a>
              </div>

              {/* Main Navigation */}
              <nav aria-label="Hauptnavigation" className="hidden md:flex space-x-1">
                <a
                  href="/"
                  className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                >
                  Startseite
                </a>
                <a
                  href="/meetings"
                  className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                >
                  Sitzungen
                </a>
                <a
                  href="/papers"
                  className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                >
                  Vorlagen
                </a>
                <a
                  href="/organizations"
                  className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                >
                  Gremien
                </a>
              </nav>

              {/* Search & Auth */}
              <div className="flex items-center space-x-4">
                <form action="/search" method="get" role="search">
                  <label htmlFor="search-input" className="sr-only">
                    Suche
                  </label>
                  <input
                    id="search-input"
                    type="search"
                    name="q"
                    placeholder="Suche..."
                    className="w-48 px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </form>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main id="main-content" className="flex-1">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-gray-800 text-gray-300 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <h3 className="text-white font-semibold mb-3">
                  aitema|RIS
                </h3>
                <p className="text-sm">
                  OParl-konformes Ratsinformationssystem fuer
                  transparente kommunale Politik.
                </p>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-3">
                  Schnittstellen
                </h3>
                <ul className="text-sm space-y-1">
                  <li>
                    <a
                      href="/api/v1/oparl/system"
                      className="hover:text-white"
                    >
                      OParl API
                    </a>
                  </li>
                  <li>
                    <a href="/docs" className="hover:text-white">
                      API-Dokumentation
                    </a>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-white font-semibold mb-3">
                  Rechtliches
                </h3>
                <ul className="text-sm space-y-1">
                  <li>
                    <a href="/impressum" className="hover:text-white">
                      Impressum
                    </a>
                  </li>
                  <li>
                    <a href="/datenschutz" className="hover:text-white">
                      Datenschutz
                    </a>
                  </li>
                  <li>
                    <a href="/barrierefreiheit" className="hover:text-white">
                      Barrierefreiheit
                    </a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="mt-8 pt-4 border-t border-gray-700 text-xs text-gray-500">
              Powered by aitema GmbH &middot; Lizenz: EUPL-1.2
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
