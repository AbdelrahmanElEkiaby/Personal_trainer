import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite is the tool that runs the dev server and builds the final files.
// The react plugin is what lets us write JSX inside .jsx files.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
