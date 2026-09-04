// @ts-check
import { defineConfig } from "astro/config";

import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";

// https://astro.build/config
export default defineConfig({
  prefetch: true,
  site: "https://unblocked-games.vercel.app",
  // Slug variants that Google still serves impressions for — consolidate to canonical slugs.
  redirects: {
    "/games/happywheels": "/games/happy-wheels",
    "/games/run3": "/games/run-3",
    "/games/gun-mayhem2": "/games/gun-mayhem-2",
    "/games/geography-game": "/games/geography-game-usa",
  },
  integrations: [
    sitemap({
      namespaces: { news: false, xhtml: false, image: true, video: false },
    }),
  ],
  build: {
    inlineStylesheets: "always",
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
