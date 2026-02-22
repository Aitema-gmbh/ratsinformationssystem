'use client';

import Image from 'next/image';

const HeroSection = () => {
  return (
    <section className="py-12 border-b border-slate-200">
      <div className="max-w-4xl mx-auto px-4">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 text-xs font-medium text-aitema-emerald bg-emerald-50 border border-emerald-200 px-3 py-1 rounded mb-6">
          <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5">
            <polyline points="5,8 7,10 11,6"/>
            <circle cx="8" cy="8" r="7"/>
          </svg>
          Open Source · GitHub · OParl 1.1
        </div>

        <div className="grid md:grid-cols-2 gap-10 items-center">
          <div>
            <h1 className="text-3xl font-semibold text-slate-900 tracking-tight mb-3">
              Offenes Ratsinformationssystem
            </h1>
            <p className="text-slate-500 text-base leading-relaxed mb-6">
              Sitzungen, Vorlagen und Beschlüsse transparent zugänglich —
              für Bürgerinnen, Bürger und Verwaltung. OParl 1.1 kompatibel,
              BITV 2.0 konform, vollständig quelloffen.
            </p>
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-slate-500 bg-slate-100 border border-slate-200 px-3 py-1 rounded">OParl 1.1</span>
              <span className="text-xs text-slate-500 bg-slate-100 border border-slate-200 px-3 py-1 rounded">BITV 2.0 AA</span>
              <span className="text-xs text-slate-500 bg-slate-100 border border-slate-200 px-3 py-1 rounded">DSGVO-konform</span>
              <span className="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded">MIT-Lizenz</span>
            </div>
          </div>
          <div className="flex justify-center">
            <Image
              src="/hero-animation.svg"
              alt="Informationsfluss von Ratssitzung über Vorlage zum Bürger"
              width={420}
              height={280}
              priority
              className="opacity-90"
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
