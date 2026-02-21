'use client';

import { useState } from 'react';

export type SubscriptionType = 'organization' | 'keyword' | 'meeting_calendar';

interface SubscribeButtonProps {
  targetId: string;
  targetLabel: string;
  type: SubscriptionType;
  className?: string;
}

type UIState = 'idle' | 'form' | 'loading' | 'sent' | 'error';

export function SubscribeButton({
  targetId,
  targetLabel,
  type,
  className = '',
}: SubscribeButtonProps) {
  const [email, setEmail] = useState('');
  const [state, setState] = useState<UIState>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async () => {
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setErrorMsg('Bitte geben Sie eine gueltige E-Mail-Adresse ein.');
      return;
    }
    setState('loading');
    setErrorMsg('');
    try {
      const res = await fetch('/api/subscriptions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          subscription_type: type,
          target_id: targetId,
          target_label: targetLabel,
        }),
      });
      if (res.ok || res.status === 201 || res.status === 409) {
        setState('sent');
      } else {
        const data = await res.json().catch(() => ({}));
        setErrorMsg(data?.detail || 'Ein Fehler ist aufgetreten.');
        setState('error');
      }
    } catch {
      setErrorMsg('Netzwerkfehler. Bitte pruefen Sie Ihre Verbindung.');
      setState('error');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSubmit();
    if (e.key === 'Escape') setState('idle');
  };

  if (state === 'sent') {
    return (
      <div className="flex items-center gap-2 text-sm text-emerald-700 font-medium py-1">
        <span className="text-base">&#10003;</span>
        <span>Bestaetigungsmail gesendet. Bitte pruefen Sie Ihr Postfach.</span>
      </div>
    );
  }

  if (state === 'form' || state === 'loading' || state === 'error') {
    return (
      <div className="mt-2">
        <div className="flex gap-2">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="ihre@email.de"
            disabled={state === 'loading'}
            autoFocus
            className="border border-slate-300 rounded-md px-3 py-1.5 text-sm flex-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-50"
            aria-label="E-Mail-Adresse fuer Benachrichtigungen"
          />
          <button
            onClick={handleSubmit}
            disabled={state === 'loading'}
            className="bg-blue-600 text-white px-3 py-1.5 rounded-md text-sm font-medium hover:bg-blue-700 active:bg-blue-800 disabled:bg-blue-400 transition-colors whitespace-nowrap"
          >
            {state === 'loading' ? 'Wird gesendet...' : 'Abonnieren'}
          </button>
          <button
            onClick={() => { setState('idle'); setErrorMsg(''); setEmail(''); }}
            disabled={state === 'loading'}
            className="text-slate-500 hover:text-slate-700 px-2 py-1.5 text-sm rounded-md hover:bg-slate-100 transition-colors"
            aria-label="Abbrechen"
          >
            &#10005;
          </button>
        </div>
        {errorMsg && (
          <p className="text-red-600 text-xs mt-1">{errorMsg}</p>
        )}
        <p className="text-slate-500 text-xs mt-1">
          Sie erhalten eine Bestaetigungsmail (Double-Opt-In). Jederzeit abbestellbar.
        </p>
      </div>
    );
  }

  return (
    <button
      onClick={() => setState('form')}
      className={`flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-800 font-medium hover:underline transition-colors ${className}`}
      aria-label={`Benachrichtigungen fuer ${targetLabel} abonnieren`}
    >
      <span className="text-base" aria-hidden="true">&#128276;</span>
      <span>Benachrichtigungen</span>
    </button>
  );
}
