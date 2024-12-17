const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
  search: true,
  toc: false,
})

module.exports = withNextra()
