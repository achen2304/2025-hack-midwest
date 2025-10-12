/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['lovable.dev'],
  },
  typescript: {
    // !! WARN !!
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    // !! WARN !!
    ignoreBuildErrors: false,
  },
}

module.exports = nextConfig
