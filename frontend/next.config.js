/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    output: 'standalone',
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: `${process.env.NEXT_PUBLIC_API_URL || 'https://athletic-alignment-production-db41.up.railway.app'}/api/:path*`,
            },
        ];
    },
};

module.exports = nextConfig;
