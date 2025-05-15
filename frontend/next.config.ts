/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['static-cdn.jtvnw.net'],
    // if you also load from other hosts, add them here:
    // domains: ['static-cdn.jtvnw.net', 'another.cdn.com']
  },
}

module.exports = nextConfig
