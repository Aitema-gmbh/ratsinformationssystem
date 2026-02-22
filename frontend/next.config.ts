import type { NextConfig } from 'next';
import withPWAInit from '@ducanh2912/next-pwa';

const withPWA = withPWAInit({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
});

const nextConfig: NextConfig = {
  experimental: {
    reactCompiler: false,
  },
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

export default withPWA(nextConfig);
