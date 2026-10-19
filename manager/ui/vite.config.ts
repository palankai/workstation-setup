import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // the Ruby grammar (~1.8 MB) is only fetched when a .rb file is viewed
  build: { chunkSizeWarningLimit: 2000 },
  server: {
    proxy: { '/api': 'http://127.0.0.1:8765' },
  },
})
