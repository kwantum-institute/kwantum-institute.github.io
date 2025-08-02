import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// https://vitejs.dev/config/
export default defineConfig({
  root: "frontend",
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, "frontend/index.html"),
        404: resolve(__dirname, "frontend/public/404.html"),
      },
    },
  },
});
