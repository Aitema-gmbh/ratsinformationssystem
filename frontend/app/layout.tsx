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
  themeColor: '#1e40af',
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
      </head>
      <body>
        <a href="#main-content" className="skip-link">
          Zum Hauptinhalt springen
        </a>
        <header className="site-header" role="banner">
          <nav className="main-nav" id="main-navigation" aria-label="Hauptnavigation">
            <div className="nav-brand">
              <a href="/" aria-label="Startseite">
                <strong>aitema|Rats</strong>
              </a>
            </div>
            <ul className="nav-links">
              <li><a href="/sitzungen">Sitzungen</a></li>
              <li><a href="/vorlagen">Vorlagen</a></li>
              <li><a href="/personen">Personen</a></li>
              <li><a href="/gremien">Gremien</a></li>
              <li><a href="/suche">Suche</a></li>
            </ul>
          </nav>
        </header>
        <main id="main-content" role="main">
          {children}
        </main>
        <footer className="site-footer" role="contentinfo">
          <div className="footer-content">
            <p>Powered by <a href="https://aitema.de">aitema|Rats</a> - OParl 1.1 kompatibel</p>
            <nav aria-label="Footer-Navigation">
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
