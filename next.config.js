const withPWA = require('next-pwa')

const withTM = require('next-transpile-modules')(['@yearn-finance/web-lib'])
const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.js',
  unstable_contentDump: true,
  unstable_flexsearch: true,
  unstable_staticImage: true,
})

/** @type {import('next').NextConfig} */
const config = {
  images: {
    domains: ['rawcdn.githack.com', 'raw.githubusercontent.com'],
  },
  pwa: {
    dest: 'public',
  },
  env: {
    /* 🔵 - Yearn Finance **************************************************
     ** Config over the RPC
     **********************************************************************/
    WEB_SOCKET_URL: {
      1: process.env.WS_URL_MAINNET,
      250: process.env.WS_URL_FANTOM,
      42161: process.env.WS_URL_ARBITRUM,
    },
    JSON_RPC_URL: {
      1: process.env.RPC_URL_MAINNET,
      250: process.env.RPC_URL_FANTOM,
      42161: process.env.RPC_URL_ARBITRUM,
    },
    ALCHEMY_KEY: process.env.ALCHEMY_KEY,
    INFURA_KEY: process.env.INFURA_KEY,
  },
  reactStrictMode: true,
  typescript: {
    // Disable type checking since eslint handles this
    ignoreBuildErrors: true,
  },
}

module.exports = withPWA(withTM(withNextra(config)))
