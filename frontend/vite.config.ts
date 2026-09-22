import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [tailwindcss(), react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      proxy: {
        '/api': {
          target: env.VITE_BACKEND_URL || 'http://localhost:8000',
          // Preserve the browser-facing Host header. This mirrors a real API
          // gateway and avoids exposing the private Docker service name to
          // Django's Host validation.
          changeOrigin: false,
        },
        '/media': {
          target: env.VITE_BACKEND_URL || 'http://localhost:8000',
          changeOrigin: false,
        },
      },
    },
    build: {
      // Vite 8 uses Rolldown. Keeping framework, charts and forms separate
      // keeps the initial application chunk comfortably inside the demo budget.
      rolldownOptions: {
        output: {
          manualChunks(id) {
            if (!id.includes('node_modules')) return;
            if (id.includes('recharts')) return 'charts';
            if (id.includes('@tanstack')) return 'tanstack';
            if (id.includes('react-hook-form') || id.includes('zod')) return 'forms';
            if (id.includes('react')) return 'react-vendor';
          },
        },
      },
    },
  }
})
