# aitema|Rats RIS - Multi-Stage Build
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
LABEL org.opencontainers.image.title="aitema|Rats RIS"
LABEL org.opencontainers.image.description="OParl 1.1 Ratsinformationssystem"
LABEL org.opencontainers.image.source="https://github.com/Aitema-gmbh/ratsinformationssystem"
LABEL org.opencontainers.image.licenses="AGPL-3.0"

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000 HOSTNAME="0.0.0.0"
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://localhost:3000/api/health || exit 1
CMD ["node", "server.js"]
