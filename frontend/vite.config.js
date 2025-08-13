import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    proxy: {
      '/orders': {
        target: 'http://order-service:5001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/orders/, ''),
      },
      '/menu': {
        target: 'http://menu-service:5003',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/menu/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
});
