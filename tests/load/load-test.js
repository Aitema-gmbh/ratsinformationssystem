/**
 * k6 Load Test für aitema|Rats (OParl 1.1 API)
 * k6 run tests/load/load-test.js --env BASE_URL=https://ris.yourdomain.de
 */
import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

const errorRate = new Rate("errors");

export const options = {
  stages: [
    { duration: "1m", target: 20 },
    { duration: "3m", target: 100 },
    { duration: "5m", target: 100 },
    { duration: "2m", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<3000"],  // Next.js SSR darf max 3s brauchen
    http_req_failed: ["rate<0.01"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:3000";

const SEARCH_TERMS = ["Haushalt", "Bebauungsplan", "Satzung", "Jahresbericht", "Förderung"];

export default function () {
  const rand = Math.random();
  
  if (rand < 0.4) {
    // Startseite
    const res = http.get(BASE_URL);
    check(res, { "Homepage 200": (r) => r.status === 200 });
    
  } else if (rand < 0.7) {
    // Suche
    const term = SEARCH_TERMS[Math.floor(Math.random() * SEARCH_TERMS.length)];
    const res = http.get(`${BASE_URL}/suche?q=${encodeURIComponent(term)}`);
    check(res, { "Suche 200": (r) => r.status === 200 });
    
  } else if (rand < 0.85) {
    // OParl API
    const res = http.get(`${BASE_URL}/api/oparl/v1.1/system`);
    check(res, {
      "OParl API 200": (r) => r.status === 200,
      "Content-Type JSON": (r) => r.headers["Content-Type"].includes("application/json"),
    });
    
  } else {
    // Sitzungsliste
    const res = http.get(`${BASE_URL}/sitzungen`);
    check(res, { "Sitzungen 200": (r) => r.status === 200 });
  }
  
  sleep(Math.random() * 3 + 1);
}
