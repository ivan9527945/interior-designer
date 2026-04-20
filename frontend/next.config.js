/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",   // 更小的 Docker image

  // 圖片優化
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "9000" },
      { protocol: "https", hostname: "*.renderstudio.internal" },
    ],
    formats: ["image/avif", "image/webp"],
  },

  // 壓縮
  compress: true,

  // 實驗性功能
  experimental: {
    optimizePackageImports: ["@tanstack/react-query", "zustand"],
  },

  async rewrites() {
    const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
    return [
      { source: "/api/backend/:path*", destination: `${apiBase}/:path*` },
    ];
  },

  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "SAMEORIGIN" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
      {
        // 靜態資源長期快取
        source: "/_next/static/(.*)",
        headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }],
      },
    ];
  },
};

module.exports = nextConfig;
