import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'

/** Inlines the built script and stylesheet, so report.html opens from disk with nothing next to it. */
function inlineAssets(): Plugin {
  return {
    name: 'inline-assets',
    enforce: 'post',
    generateBundle(_, bundle) {
      const html = bundle['report.html']
      if (html?.type !== 'asset') return
      let source = String(html.source)
      for (const [name, file] of Object.entries(bundle)) {
        if (file.type === 'chunk') {
          const code = file.code.replaceAll('</script', '<\\/script')
          source = source.replace(
            new RegExp(`<script type="module" crossorigin src="/${name}"></script>`),
            () => `<script type="module">${code}</script>`,
          )
        } else if (name.endsWith('.css')) {
          source = source.replace(
            new RegExp(`<link rel="stylesheet" crossorigin href="/${name}">`),
            () => `<style>${String(file.source)}</style>`,
          )
        } else continue
        delete bundle[name]
      }
      html.source = source
    },
  }
}

// The static run report `ws update` writes: the same RunReport component as the web UI, in one file.
// Runs after the main build, into the same folder.
export default defineConfig({
  plugins: [react(), tailwindcss(), inlineAssets()],
  build: {
    emptyOutDir: false,
    rollupOptions: { input: 'report.html' },
  },
})
