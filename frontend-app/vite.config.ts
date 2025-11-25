import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import path from "path";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        maximumFileSizeToCacheInBytes: 5 * 1024 * 1024 // 5MB로 제한 증가
      },
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'Frontend App',
        short_name: 'FrontendApp',
        description: 'React PWA Application',
        theme_color: '#F5F6FA',
        background_color: '#F5F6FA',
        theme_color_light: '#F5F6FA',
        theme_color_dark: '#0049AD',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: 'icon.svg',
            sizes: '192x192',
            type: 'image/svg+xml'
          },
          {
            src: 'icon.svg',
            sizes: '512x512',
            type: 'image/svg+xml'
          }
        ]
      },
      devOptions: {
        enabled: true,
        type: 'module'
      }
    })
  ],
  // PostCSS 설정 명시적 지정
  css: {
    postcss: './postcss.config.js'
  },
  server: {
    port: 3000,
    host: true
  },
  // Tailwind CSS와 PWA 호환성을 위한 빌드 설정
  build: {
    cssCodeSplit: false, // CSS를 하나의 파일로 번들링하여 PWA 캐싱 최적화
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom']
        }
      }
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
