'use client';

import Image from 'next/image';

const HeroSection = () => {
  return (
    <section className="py-14 border-b border-slate-200 bg-white">
      <div className="max-w-5xl mx-auto px-6">

        {/* Label */}
        <p className="text-xs font-semibold tracking-widest uppercase text-slate-400 mb-5">
          Ratsinformationssystem — Open Source
        </p>

        <div style={{display:'grid', gridTemplateColumns:'3fr 2fr', gap:'3rem', alignItems:'center'}}>
          <div>
            <h1 className="text-4xl font-bold text-slate-900 tracking-tight leading-tight mb-4">
              Offenes<br/>Ratsinformationssystem
            </h1>
            <p className="text-slate-500 text-base leading-relaxed mb-8 max-w-lg">
              Sitzungen, Vorlagen und Beschlüsse transparent zugänglich —
              für Bürgerinnen, Bürger und Verwaltung.
              OParl 1.1 kompatibel, BITV 2.0 konform, vollständig quelloffen.
            </p>

            <div className="flex flex-wrap gap-2 mb-6">
              <span className="text-xs text-slate-500 border border-slate-200 px-3 py-1 rounded-sm font-mono">OParl 1.1</span>
              <span className="text-xs text-slate-500 border border-slate-200 px-3 py-1 rounded-sm font-mono">BITV 2.0 AA</span>
              <span className="text-xs text-slate-500 border border-slate-200 px-3 py-1 rounded-sm font-mono">DSGVO-konform</span>
              <span className="text-xs text-emerald-700 border border-emerald-300 px-3 py-1 rounded-sm font-mono">&lt;/&gt; MIT-Lizenz</span>
            </div>

            <a
              href="/suche"
              className="inline-block bg-slate-900 text-white text-sm font-medium px-5 py-2.5 rounded hover:bg-slate-700 transition-colors"
            >
              Suche öffnen →
            </a>
          </div>

          <div className="flex justify-center">
            <Image
              src="/hero-animation.svg"
              alt="Informationsfluss von Ratssitzung über Vorlage zum Bürger"
              width={440}
              height={290}
              priority
              className="w-full h-auto"
              style={{maxWidth:'440px'}}
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
