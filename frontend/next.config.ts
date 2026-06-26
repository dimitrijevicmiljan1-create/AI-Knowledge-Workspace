import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      {
        source: "/register",
        destination: "/signup",
        permanent: true,
      },
      {
        source: "/onboarding",
        destination: "/chat/new",
        permanent: false,
      },
      {
        source: "/dashboard",
        destination: "/chat/new",
        permanent: false,
      },
      {
        source: "/github",
        destination: "/sources",
        permanent: false,
      },
      {
        source: "/obsidian",
        destination: "/sources",
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
