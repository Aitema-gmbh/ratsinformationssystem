import type { Metadata, Viewport } from 'next';
import Link from 'next/link';
import { Navigation } from '@/components/ui/Navigation';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'aitema|RIS — Modernes Ratsinformationssystem',
    template: '%s | aitema|RIS',
  },
  description: 'Ein state-of-the-art, offenes Ratsinformationssystem für deutsche Kommunen, basierend auf Next.js 15, React 19 und OParl 1.1.',
  manifest: '/manifest.json',
};

export const viewport: Viewport = {
  themeColor: '#0f172a',
  width: 'device-width',
  initialScale: 1,
};

function GradientLogo() {
  return (
    <Link href="/" className="flex items-center gap-3 group" aria-label="aitema|RIS — zur Startseite">
      <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-aitema-accent to-aitema-accent-hover shadow-lg transition-all duration-300 transform group-hover:scale-110 group-hover:shadow-blue-500/50">
        <span className="text-xl font-black text-white tracking-tighter" style={{ fontFamily: 'inherit' }}>aR</span>
      </div>
      <div className="hidden sm:block">
        <p className="text-lg font-bold tracking-tight text-white">
          aitema<span className="font-light opacity-80">|</span><span className="text-blue-300">RIS</span>
        </p>
      </div>
    </Link>
  );
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body className="bg-slate-50 text-slate-900 antialiased">
        <a href="#main-content" className="absolute z-50 p-3 m-3 text-sm text-white transition -translate-y-full rounded-md bg-aitema-accent focus:translate-y-0">
          Zum Hauptinhalt springen
        </a>

        <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-aitema-navy/80 backdrop-blur-xl">
          <div className="container flex items-center justify-between h-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <GradientLogo />
            <div className="flex items-center gap-4">
                <Navigation />
                <div className="w-px h-6 bg-white/10 hidden md:block"></div>
                <Link href="/suche" className="flex items-center justify-center w-10 h-10 rounded-full text-slate-300 hover:text-white hover:bg-white/10 transition-colors" title="Suche öffnen (Cmd+K)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <span className="sr-only">Suche öffnen</span>
                </Link>
            </div>
          </div>
        </header>

        <main id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {children}
        </main>

        <footer className="bg-aitema-navy text-slate-400 border-t border-white/10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex flex-col md:flex-row items-center justify-between gap-6">
                <p className="text-sm">&copy; {new Date().getFullYear()} aitema GmbH. Alle Rechte vorbehalten.</p>
                <div className="flex gap-6">
                    <Link href="/impressum" className="text-sm hover:text-white transition-colors">Impressum</Link>
                    <Link href="/datenschutz" className="text-sm hover:text-white transition-colors">Datenschutz</Link>
                    <Link href="/barrierefreiheit" className="text-sm hover:text-white transition-colors">Barrierefreiheit</Link>
                </div>
            </div>
        </footer>
      </body>
    </html>
  );
}
