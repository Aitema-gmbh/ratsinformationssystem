'use client';

import { useState, useEffect } from 'react';

const steps = [
  {
    label: 'Ratssitzung',
    description: 'Gremien tagen, Beschlüsse werden gefasst und protokolliert.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-8 h-8">
        <rect x="3" y="4" width="18" height="16" rx="1"/>
        <path d="M8 4V2M16 4V2M3 9h18"/>
        <circle cx="8" cy="14" r="1.5" fill="currentColor" stroke="none"/>
        <circle cx="12" cy="14" r="1.5" fill="currentColor" stroke="none"/>
        <circle cx="16" cy="14" r="1.5" fill="currentColor" stroke="none"/>
      </svg>
    ),
  },
  {
    label: 'Digitale Erfassung',
    description: 'Vorlagen, Anträge und Beschlüsse werden strukturiert gespeichert (OParl 1.1).',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-8 h-8">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
        <polyline points="14,2 14,8 20,8"/>
        <line x1="8" y1="13" x2="16" y2="13"/>
        <line x1="8" y1="17" x2="13" y2="17"/>
      </svg>
    ),
  },
  {
    label: 'Volltextsuche',
    description: 'Bürgerinnen und Bürger durchsuchen alle Vorgänge per Stichwort.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-8 h-8">
        <circle cx="11" cy="11" r="7"/>
        <line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
    ),
  },
  {
    label: 'Öffentlicher Zugang',
    description: 'Alle Informationen sind transparent und barrierefrei abrufbar (BITV 2.0).',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-8 h-8">
        <circle cx="12" cy="8" r="3"/>
        <path d="M6 20v-1a6 6 0 0112 0v1"/>
      </svg>
    ),
  },
];

const ExplainerAnimation = () => {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setActive((i) => (i + 1) % steps.length), 4000);
    return () => clearInterval(t);
  }, []);

  return (
    <section className="py-10 border-b border-slate-200">
      <div className="max-w-4xl mx-auto px-4">
        <p className="text-xs font-medium text-slate-400 uppercase tracking-widest mb-6">So funktioniert es</p>
        {/* Step Tabs */}
        <div className="grid grid-cols-4 gap-1 mb-8 border border-slate-200 rounded p-1 bg-slate-50">
          {steps.map((s, i) => (
            <button
              key={i}
              onClick={() => setActive(i)}
              className={`text-xs font-medium px-2 py-2 rounded transition-colors ${
                i === active
                  ? 'bg-white text-aitema-navy shadow-sm border border-slate-200'
                  : 'text-slate-400 hover:text-slate-600'
              }`}
            >
              {i + 1}. {s.label}
            </button>
          ))}
        </div>
        {/* Active Step */}
        <div className="flex items-start gap-6 bg-white border border-slate-200 rounded p-6">
          <div className="text-aitema-accent flex-shrink-0 mt-1">
            {steps[active].icon}
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 mb-1">{steps[active].label}</h3>
            <p className="text-slate-500 text-sm leading-relaxed">{steps[active].description}</p>
          </div>
        </div>
        {/* Progress dots */}
        <div className="flex gap-1.5 mt-4 justify-end">
          {steps.map((_, i) => (
            <span
              key={i}
              className={`block w-1.5 h-1.5 rounded-full transition-colors ${i === active ? 'bg-aitema-accent' : 'bg-slate-300'}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default ExplainerAnimation;
