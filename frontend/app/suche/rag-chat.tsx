"use client";
import { useState, useRef } from "react";

interface Source {
  id: string;
  title: string;
  reference: string;
  date: string;
  similarity: number;
}

export default function RAGChat() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setAnswer("");
    setSources([]);
    abortRef.current = new AbortController();

    try {
      const res = await fetch("/api/rag/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
        signal: abortRef.current.signal,
      });

      if (!res.ok || !res.body) {
        setAnswer("Fehler beim Verbinden mit dem KI-Assistenten.");
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        for (const line of chunk.split("\n")) {
          if (!line.startsWith("data: ")) continue;
          const raw = line.slice(6).trim();
          if (raw === "[DONE]") break;
          try {
            const data = JSON.parse(raw);
            if (data.sources) setSources(data.sources);
            if (data.text) setAnswer((prev) => prev + data.text);
          } catch {
            // Partial JSON chunk – ignore
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== "AbortError") {
        setAnswer("Verbindungsfehler. Bitte versuchen Sie es erneut.");
      }
    } finally {
      setLoading(false);
    }
  }

  function handleStop() {
    abortRef.current?.abort();
    setLoading(false);
  }

  return (
    <section
      aria-label="KI-Assistent fuer Ratsbeschluesse"
      style={{
        marginTop: "2.5rem",
        padding: "1.5rem",
        background: "#f0f7ff",
        border: "1px solid #bfdbfe",
        borderRadius: "0.75rem",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "0.625rem", marginBottom: "1rem" }}>
        <span
          aria-hidden="true"
          style={{
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            width: "2rem",
            height: "2rem",
            borderRadius: "50%",
            background: "linear-gradient(135deg, #3b82f6, #2563eb)",
            color: "#fff",
            fontSize: "1rem",
            flexShrink: 0,
          }}
        >
          ✦
        </span>
        <h2
          style={{
            fontSize: "1.125rem",
            fontWeight: 700,
            color: "#1e3a5f",
            margin: 0,
          }}
        >
          KI-Assistent: Fragen zu Ratsbeschluessen
        </h2>
      </div>

      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", gap: "0.625rem", marginBottom: "1.25rem" }}
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="z.B. Was wurde ueber den Radweg an der Bahnhofstrasse beschlossen?"
          aria-label="Frage an den KI-Assistenten"
          disabled={loading}
          style={{
            flex: 1,
            padding: "0.6875rem 1rem",
            borderRadius: "0.5rem",
            border: "1px solid #93c5fd",
            fontSize: "0.9375rem",
            background: "#fff",
            outline: "none",
            color: "#0f172a",
          }}
        />
        {loading ? (
          <button
            type="button"
            onClick={handleStop}
            style={{
              padding: "0.6875rem 1.25rem",
              background: "#ef4444",
              color: "#fff",
              border: "none",
              borderRadius: "0.5rem",
              fontWeight: 700,
              cursor: "pointer",
              fontSize: "0.875rem",
              whiteSpace: "nowrap",
            }}
          >
            Stopp
          </button>
        ) : (
          <button
            type="submit"
            disabled={!query.trim()}
            style={{
              padding: "0.6875rem 1.25rem",
              background:
                query.trim()
                  ? "linear-gradient(135deg, #3b82f6, #2563eb)"
                  : "#cbd5e1",
              color: "#fff",
              border: "none",
              borderRadius: "0.5rem",
              fontWeight: 700,
              cursor: query.trim() ? "pointer" : "not-allowed",
              fontSize: "0.875rem",
              whiteSpace: "nowrap",
              transition: "background 0.15s",
            }}
          >
            Fragen
          </button>
        )}
      </form>

      {(answer || loading) && (
        <div
          style={{
            background: "#fff",
            border: "1px solid #dbeafe",
            borderRadius: "0.625rem",
            padding: "1.25rem",
          }}
        >
          {loading && !answer && (
            <div
              style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#64748b" }}
            >
              <span
                style={{
                  display: "inline-block",
                  width: "0.875rem",
                  height: "0.875rem",
                  border: "2px solid #bfdbfe",
                  borderTopColor: "#3b82f6",
                  borderRadius: "50%",
                  animation: "rag-spin 0.6s linear infinite",
                }}
                aria-hidden="true"
              />
              Durchsuche Beschluesse…
              <style>{"@keyframes rag-spin { to { transform: rotate(360deg); } }"}</style>
            </div>
          )}

          {answer && (
            <p
              style={{
                lineHeight: 1.75,
                color: "#0f172a",
                whiteSpace: "pre-wrap",
                margin: 0,
              }}
            >
              {answer}
              {loading && (
                <span
                  style={{
                    display: "inline-block",
                    width: "0.5rem",
                    height: "1.1em",
                    background: "#3b82f6",
                    marginLeft: "0.125rem",
                    verticalAlign: "text-bottom",
                    animation: "rag-blink 0.9s step-end infinite",
                  }}
                  aria-hidden="true"
                />
              )}
              <style>
                {
                  "@keyframes rag-blink { 0%,100%{opacity:1} 50%{opacity:0} }"
                }
              </style>
            </p>
          )}

          {sources.length > 0 && (
            <div
              style={{
                marginTop: "1rem",
                paddingTop: "1rem",
                borderTop: "1px solid #e2e8f0",
              }}
            >
              <p
                style={{
                  fontSize: "0.75rem",
                  fontWeight: 700,
                  color: "#64748b",
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  marginBottom: "0.5rem",
                  marginTop: 0,
                }}
              >
                Gefundene Drucksachen
              </p>
              <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "0.375rem" }}>
                {sources.map((s) => (
                  <li key={s.id}>
                    <a
                      href={`/vorlagen/${s.id}`}
                      style={{ fontSize: "0.875rem", color: "#2563eb", textDecoration: "none" }}
                    >
                      {s.reference ? `${s.reference} – ` : ""}
                      {s.title}
                      {s.date ? ` (${s.date})` : ""}
                    </a>
                    {s.similarity > 0 && (
                      <span
                        style={{
                          marginLeft: "0.375rem",
                          fontSize: "0.75rem",
                          color: "#94a3b8",
                        }}
                      >
                        {s.similarity}% Relevanz
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
