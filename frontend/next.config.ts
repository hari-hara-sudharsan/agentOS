import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Optimize builds and caching
  reactStrictMode: true,
  
  // Optimize images
  images: {
    domains: ['hariharasudharsanj.us.auth0.com'],
  },

  // Environment variable validation
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_AUTH0_DOMAIN: process.env.NEXT_PUBLIC_AUTH0_DOMAIN,
    NEXT_PUBLIC_AUTH0_CLIENT_ID: process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID,
    NEXT_PUBLIC_AUTH0_AUDIENCE: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
  },

  // Cache optimization
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 2,
  },

  // Disable x-powered-by header for security
  poweredByHeader: false,

  // Production optimization
  swcMinify: true,
};

export default nextConfig;
