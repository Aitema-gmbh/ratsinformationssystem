import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  i18n: {
    locales: ['de'],
    defaultLocale: 'de',
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_OPARL_URL: process.env.NEXT_PUBLIC_OPARL_URL || 'http://localhost:8000/oparl/v1',
  },
};

export default nextConfig;
