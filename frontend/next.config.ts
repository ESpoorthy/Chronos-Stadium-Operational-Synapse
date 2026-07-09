import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  devIndicators: false,
  allowedDevOrigins: ['guise-reproduce-shredding.ngrok-free.dev'],
};

export default nextConfig;
