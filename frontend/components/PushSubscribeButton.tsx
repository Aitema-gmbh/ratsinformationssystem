"use client";
import { useState, useEffect } from "react";

export default function PushSubscribeButton({ topic }: { topic?: string }) {
  const [supported, setSupported] = useState(false);
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const isSupported =
      typeof window !== "undefined" &&
      "serviceWorker" in navigator &&
      "PushManager" in window;
    setSupported(isSupported);

    if (isSupported) {
      // Check if already subscribed
      navigator.serviceWorker.ready.then((reg) =>
        reg.pushManager.getSubscription()
      ).then((sub) => {
        setSubscribed(!!sub);
      }).catch(() => {});
    }
  }, []);

  if (!supported) return null;

  async function toggleSubscription() {
    setLoading(true);
    setError(null);
    try {
      const reg = await navigator.serviceWorker.ready;

      if (subscribed) {
        const sub = await reg.pushManager.getSubscription();
        if (sub) {
          await sub.unsubscribe();
          await fetch(
            "/api/push/unsubscribe?endpoint=" + encodeURIComponent(sub.endpoint),
            { method: "DELETE" }
          );
        }
        setSubscribed(false);
      } else {
        const keyRes = await fetch("/api/push/vapid-key");
        const { key } = await keyRes.json();

        const sub = await reg.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: key,
        });

        const p256dh = sub.getKey("p256dh");
        const auth = sub.getKey("auth");

        await fetch("/api/push/subscribe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            endpoint: sub.endpoint,
            keys: {
              p256dh: p256dh
                ? btoa(String.fromCharCode(...new Uint8Array(p256dh)))
                : "",
              auth: auth
                ? btoa(String.fromCharCode(...new Uint8Array(auth)))
                : "",
            },
            topic,
          }),
        });
        setSubscribed(true);
      }
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "Fehler beim Aktivieren der Benachrichtigungen"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: "inline-flex", flexDirection: "column", gap: "0.25rem" }}>
      <button
        onClick={toggleSubscription}
        disabled={loading}
        aria-label={
          subscribed
            ? "Benachrichtigungen deaktivieren"
            : "Benachrichtigungen aktivieren"
        }
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "0.375rem",
          padding: "0.5rem 1rem",
          borderRadius: "0.5rem",
          fontSize: "0.875rem",
          fontWeight: 600,
          cursor: loading ? "wait" : "pointer",
          border: "1px solid #e2e8f0",
          background: subscribed ? "#dcfce7" : "#f8fafc",
          color: "#0f172a",
          opacity: loading ? 0.7 : 1,
          transition: "background 0.2s ease",
        }}
      >
        <span aria-hidden="true">{subscribed ? "\uD83D\uDD14" : "\uD83D\uDD15"}</span>
        {loading
          ? "..."
          : subscribed
          ? "Benachrichtigungen aktiv"
          : "Benachrichtigungen aktivieren"}
      </button>
      {error && (
        <span style={{ fontSize: "0.75rem", color: "#dc2626" }}>{error}</span>
      )}
    </div>
  );
}
