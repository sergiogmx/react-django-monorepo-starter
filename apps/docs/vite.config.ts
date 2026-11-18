import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

// Ladle adds the React plugin itself; we only add Tailwind so stories use the tokens.
export default defineConfig({
  plugins: [tailwindcss()],
});
