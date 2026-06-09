import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "https://ai-slop-api-lxxfdfgvoq-uc.a.run.app",  // dev: proxy directly to Cloud Run
    },
  },
});
