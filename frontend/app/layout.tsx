import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'aitema|Rats - Ratsinformationssystem',
  description: 'Offenes Ratsinformationssystem fuer deutsche Kommunen - OParl 1.1 kompatibel',
  keywords: 'RIS, Ratsinformationssystem, OParl, Kommune, Gemeinderat, Open Data',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'aitema|Rats',
  },
};

export const viewport: Viewport = {
  themeColor: '#0f172a',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <a href="#main-content" className="skip-link">
          Zum Hauptinhalt springen
        </a>

        <header className="site-header" role="banner">
          <nav className="main-nav" id="main-navigation" aria-label="Hauptnavigation">

            {/* Brand */}
            <div className="nav-brand">
              <a href="/" aria-label="aitema|Rats - Startseite">
                <div className="nav-brand-logo" aria-hidden="true">aR</div>
                <div className="nav-brand-text">
                  <span className="nav-brand-name">
                    aitema|<span className="accent">Rats</span>
                  </span>
                  <span className="nav-brand-tagline">
                    Ratsinformationssystem
                    <span className="nav-oparl-badge">OParl 1.1</span>
                  </span>
                </div>
              </a>
            </div>

            {/* Navigation Links */}
            <ul className="nav-links" role="list">
              <li>
                <a href="/sitzungen" aria-label="Sitzungen anzeigen">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                  Sitzungen
                </a>
              </li>
              <li>
                <a href="/vorlagen" aria-label="Vorlagen anzeigen">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                    <polyline points="10 9 9 9 8 9"/>
                  </svg>
                  Vorlagen
                </a>
              </li>
              <li>
                <a href="/personen" aria-label="Personen anzeigen">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                  Personen
                </a>
              </li>
              <li>
                <a href="/gremien" aria-label="Gremien anzeigen">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                  </svg>
                  Gremien
                </a>
              </li>
            </ul>

            {/* Search CTA */}
            <a
              href="/suche"
              className="nav-search-btn"
              aria-label="Zur Volltextsuche"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              Suche
            </a>
          </nav>
        </header>

        <main id="main-content" role="main">
          {children}
        </main>

        <footer className="site-footer" role="contentinfo">
          <div className="footer-content">
            <div className="footer-brand">
              <strong>aitema|Rats</strong>
              <span>OParl 1.1 kompatibel &bull; Open Data fuer Kommunen</span>
            </div>
            <nav className="footer-nav" aria-label="Footer-Navigation">
              <a href="/impressum">Impressum</a>
              <a href="/datenschutz">Datenschutz</a>
              <a href="/barrierefreiheit">Barrierefreiheit</a>
              <a href="/oparl">OParl API</a>
            </nav>
          </div>
        </footer>

        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js')
                    .then(function(reg) {
                      console.log('Service Worker registriert:', reg.scope);
                    })
                    .catch(function(err) {
                      console.log('Service Worker Fehler:', err);
                    });
                });
              }
            `,
          }}
        />
      </body>
    </html>
  );
}
