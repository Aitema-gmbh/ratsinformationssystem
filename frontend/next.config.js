/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable ESLint during Docker build
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },

  // Enable React strict mode for highlighting potential problems
  reactStrictMode: true,

  // Output as standalone for Docker deployment
  output: "standalone",

  // Environment variables available on the client
  env: {
    NEXT_PUBLIC_APP_NAME: "aitema|RIS",
    NEXT_PUBLIC_APP_VERSION: "0.1.0",
  },

  // Image optimization config
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.aitema.de",
      },
    ],
  },

  // API proxy for development
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },

  // Security headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "X-Frame-Options",
            value: "SAMEORIGIN",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
