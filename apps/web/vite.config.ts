/// <reference types="vitest/config" />
import { fileURLToPath } from 'node:url';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Read VITE_* variables from the repo-root .env, shared with the API.
  envDir: fileURLToPath(new URL('../..', import.meta.url)),
  server: {
    port: 5173,
    // The browser only talks to Vite; Vite forwards /api to Django.
    // Inside Docker Compose the target is http://api:8000.
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test-setup.ts'],
  },
});
