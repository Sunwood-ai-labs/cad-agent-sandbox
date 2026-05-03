import { defineConfig } from 'vitepress'

const repo = 'https://github.com/Sunwood-ai-labs/cad-agent-sandbox'
const base = process.env.VITEPRESS_BASE ?? '/cad-agent-sandbox/'
const withBase = (path: string) => `${base.replace(/\/$/, '')}/${path.replace(/^\//, '')}`

export default defineConfig({
  title: 'CAD Agent Sandbox',
  description: 'Windows-first CAD-as-code benchmark documentation.',
  base,
  cleanUrls: true,
  head: [
    ['link', { rel: 'icon', type: 'image/png', sizes: '32x32', href: withBase('cad-agent-sandbox-32.png') }],
    ['link', { rel: 'apple-touch-icon', sizes: '192x192', href: withBase('cad-agent-sandbox-192.png') }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'CAD Agent Sandbox' }],
    ['meta', { property: 'og:description', content: 'Compare local CAD-as-code toolchains against repeatable furniture specs.' }]
  ],
  themeConfig: {
    logo: '/cad-agent-sandbox.png',
    search: {
      provider: 'local'
    },
    socialLinks: [
      { icon: 'github', link: repo }
    ]
  },
  locales: {
    root: {
      label: 'English',
      lang: 'en-US',
      title: 'CAD Agent Sandbox',
      description: 'Windows-first CAD-as-code benchmark documentation.',
      themeConfig: {
        nav: [
          { text: 'Guide', link: '/guide/getting-started' },
          { text: 'Cases', link: '/guide/cases' },
          { text: '日本語', link: '/ja/' }
        ],
        sidebar: [
          {
            text: 'Guide',
            items: [
              { text: 'Getting Started', link: '/guide/getting-started' },
              { text: 'Cases', link: '/guide/cases' },
              { text: 'Verification', link: '/guide/verification' }
            ]
          },
          {
            text: 'Reference',
            items: [
              { text: 'Case Layout', link: '/CASE_LAYOUT' }
            ]
          }
        ]
      }
    },
    ja: {
      label: '日本語',
      lang: 'ja-JP',
      title: 'CAD Agent Sandbox',
      description: 'Windows 前提 CAD-as-code ベンチマークのドキュメント。',
      themeConfig: {
        nav: [
          { text: 'ガイド', link: '/ja/guide/getting-started' },
          { text: 'ケース', link: '/ja/guide/cases' },
          { text: 'English', link: '/' }
        ],
        sidebar: [
          {
            text: 'ガイド',
            items: [
              { text: 'はじめかた', link: '/ja/guide/getting-started' },
              { text: 'ケース', link: '/ja/guide/cases' },
              { text: '検証', link: '/ja/guide/verification' }
            ]
          },
          {
            text: 'リファレンス',
            items: [
              { text: 'ケース構成', link: '/CASE_LAYOUT' }
            ]
          }
        ]
      }
    }
  }
})
