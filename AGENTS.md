# Instructions for agents

## Package manager

This project uses **bun** as its package manager. Always use `bun` instead of `npm`, `yarn`, or `pnpm` for any package-related commands.

- `bun install` — install dependencies
- `bun run <script>` — run a script from package.json (e.g., `bun run dev`, `bun run build`)
- `bun add <package>` — add a dependency
- `bun add -d <package>` — add a dev dependency
- `bun remove <package>` — remove a dependency
- `bun update` — update dependencies
- `bun <script>` — shorthand for running scripts

## Post-change verification

After making any code changes, always run both of these commands to verify correctness and consistency:

1. **`bun run check`** — runs `astro check` (TypeScript/type checking) followed by `astro build` + pagefind indexing. Ensures the project type-checks and builds successfully.
2. **`bun run lint`** — runs `prettier --check .` to verify all files are properly formatted.

Run these **before** committing. If either fails, fix the issues before proceeding.

## Project structure — detailed

```
├── src/
│   ├── components/            Reusable Astro components
│   │   ├── gametile.astro     Homepage game tile card (link + cover image + name)
│   │   └── flash.astro        Ruffle Flash emulator embed (polling-based loader)
│   ├── data/
│   │   └── game-seo.ts        Central registry: all games keyed by page slug,
│   │                          with SEO metadata (`title` is the display name)
│   ├── layout/
│   │   └── layout.astro       Main layout — used by BOTH home page and game pages
│   ├── pages/
│   │   ├── index.astro        Home page — lists all games via <Gametile> components
│   │   ├── dmca.astro         DMCA takedown notice page
│   │   └── games/
│   │       ├── webtris.astro  Iframe game page (Tetris clone)
│   │       ├── [slug].astro   Dynamic route for all Flash games (56 games)
│   │       └── run-3.astro    HTML5 game page (Run 3 — unique template)
│   └── styles/
│       └── styles.css         Global CSS + Tailwind v4 @import + .games-grid/.game-tile
├── public/
│   ├── flash/                 All .swf files for Flash games
│   ├── games/run3/            HTML5 game bundle for Run 3 (index.html, JS, assets)
│   ├── images/                Cover art (JPEG/PNG/AVIF/WEBP), logos, favicon
│   ├── pagefind/              Generated search index — build artifact, gitignored
│   ├── ruffle/                Ruffle WebAssembly Flash emulator (ruffle.js + .wasm)
│   ├── robots.txt             Blocks /flash/ from crawlers, links to llms.txt + sitemap
│   ├── llms.txt               AI-friendly site summary (llmstxt.org format)
│   ├── _redirects             Vercel redirect rule (/sitemap.xml → /sitemap-index.xml)
│   └── *.txt                  Domain verification file for search consoles
├── astro.config.mjs           Astro v6 config (prefetch, sitemap, Tailwind v4 via Vite)
├── tsconfig.json              TypeScript strict mode (extends astro/tsconfigs/strict)
├── postcss.config.cjs         DEAD — unused with Tailwind v4 + @tailwindcss/vite
├── wrangler.jsonc             DEAD — Cloudflare config for a Vercel-deployed site
└── package.json               Dependencies: astro, tailwindcss v4, pagefind, etc.
```

> **Tailwind v4 note:** This project uses Tailwind CSS v4, which moves configuration from `tailwind.config.js` to CSS `@theme` directives. Any theme extensions (colors, fonts, spacing, etc.) must be defined as CSS variables inside an `@theme` block in `src/styles/styles.css`. Do **not** create or edit a `tailwind.config.js` file — it will be ignored.

## The data layer (how games are registered)

One file: `src/data/game-seo.ts`. Exports `gamesMap: Record<string, GameSEO>` keyed by **page slug** (URL segment, e.g. `"breaking-the-bank"` for `/games/breaking-the-bank`). Each entry includes:

- `title` — display name (e.g. `"Henry Stickmin 1: Breaking the Bank"`)
- `description`, `image`, `genre`, `year` — SEO metadata
- `isFlash` — whether it needs Ruffle emulation
- `gamePath` — absolute path to the `.swf` file (empty string for non-Flash games)

Everything else derives from the slug: `layout.astro` takes a `slug` prop and looks up `gamesMap[slug]`; `index.astro` lists slugs in popularity order. There is no slug ↔ name mapping file — the slug is the key everywhere.

### How to add a new game

1. **Get the `.swf` file** — place it in `public/flash/` (lowercase, no spaces — convention is page-slug without hyphens, e.g. `bloonstd5.swf`)
2. **Get a cover image** — place it in `public/images/` (~300x200, any format)
3. **Register in `src/data/game-seo.ts`** — add entry to `gamesMap` keyed by the page slug, with full SEO metadata, `isFlash: true/false`, and `gamePath: "/flash/..."` (omit or empty for non-Flash)
4. **Update `src/pages/index.astro`** — add the slug to the hardcoded `games` array at the right popularity position
5. **Update `public/llms.txt`** — add the game URL to the list

For **non-Flash HTML5 games** (like Run 3), also create a dedicated `.astro` page in `src/pages/games/` — the dynamic `[slug].astro` only handles Flash games.

> **Important:** All asset paths (`.swf` files, cover images, scripts) must use **absolute paths** relative to the `public/` directory — e.g., `/flash/gamename.swf`, `/images/cover.png`. Never use relative paths like `images/cover.png` or `../images/cover.png`.

### The game page: `[slug].astro`

All Flash games (56 of 57) are served by a single dynamic route:

```astro
---
// [slug].astro — handles all Flash games
export async function getStaticPaths() {
  return Object.keys(gamesMap)
    .filter((slug) => gamesMap[slug].isFlash)
    .map((slug) => ({ params: { slug } }));
}
const { slug } = Astro.params!;
const seo = gamesMap[slug];
---
<Layout slug={slug}>
  <Flash gamePath={seo.gamePath || ""} />
</Layout>
```

The `Flash` component handles Ruffle loading (polling loop). The layout auto-reads SEO from `game-seo.ts` via the `slug` prop.

### The exception: `run-3.astro`

Run 3 is the only HTML5 game. It has its own `.astro` page because it needs a completely different template:

```astro
<Layout slug="run-3">
  <base href="/games/run3/" />
  <div id="run3-wrapper">...</div>
  <script src="/games/run3/Run3.js" is:inline></script>
</Layout>
```

No `Flash` component, no `.swf`. Direct JS bundle.

### The SEO system (how layout.astro + game-seo.ts work together)

- `game-seo.ts` exports `gamesMap: Record<string, GameSEO>` — one entry per game keyed by page slug.
- `layout.astro` receives a `slug` prop (string), looks up `gamesMap[slug]` for SEO data and the display name (`title`).
- The layout then generates: `<title>`, `<meta description/keywords>`, Open Graph tags, Twitter Card tags, JSON-LD structured data (BreadcrumbList + VideoGame for game pages, WebSite + CollectionPage + Organization for home).
- Use `layout.astro` with `isHome={true}` for the homepage — there is no separate home layout.

### Home page: `src/pages/index.astro`

- Uses `Layout` with `isHome={true}` and `pageTitle`.
- Iterates over games and renders `<Gametile Game={name} Path={"/games/" + slug} Image={cover} />`.
- The iteration order determines display order. Currently uses a hardcoded `games` array of page slugs.
- Has inline "Popular" links at the top — keep these in sync with the first ~9 games.
- The **naming conventions doc below** still applies for index.astro Path values.

### Popularity ordering

The `games` array in `index.astro` is ordered by estimated popularity (most popular first). When adding a game, place it at the appropriate position rather than appending to the end.

Guidelines for placement:

- **Tier 1 (top):** All-time greats (Happy Wheels, Plants vs Zombies, Run 3, Fireboy and Watergirl, Bloons TD 5, Super Mario 63, Tetris, Pac-Man)
- **Tier 2:** Beloved classics (Fancy Pants Adventure, Stick War, Age of War, Madness: Project Nexus, Strike Force Heroes, The World's Hardest Game, Vex 3, Gun Mayhem 2, Bubble Trouble, QWOP, Crush the Castle, Burrito Bison)
- **Tier 3:** Well-loved franchises (Boxhead, The Impossible Quiz, Henry Stickmin series, Duck Life series, Learn to Fly series)
- **Tier 4:** Established games (Achievement Unlocked, Super Mario Flash series, Ultimate Flash Sonic, Swords and Sandals series)
- **Tier 5 (bottom):** Niche games (Doom, Minesweeper, Geography Game USA, Riddle School series, Hobo series)

Series entries should be grouped together and placed as a block. The "Popular" links row should reflect the current top ~9 games.

### File naming conventions

| Artifact                  | Convention                                      | Example                                   |
| ------------------------- | ----------------------------------------------- | ----------------------------------------- |
| Page slug (URL)           | `kebab-case`                                    | `/games/breaking-the-bank`                |
| `.swf` in `public/flash/` | Lowercase, no spaces (often slug minus hyphens) | `happywheels.swf`, `bloonstd5.swf`        |
| Cover image               | Descriptive, any format                         | `happywheelscover.webp`, `sm63-cover.png` |
| `game-seo.ts` key         | Page slug (URL segment)                         | `"breaking-the-bank"`                     |
| `index.astro` `Path`      | `"/games/" + slug`                              | `"/games/breaking-the-bank"`              |

There are historical inconsistencies in `.swf` filenames (e.g. `bloonstd5.swf` for slug `bloons-td-5`). The `gamePath` field in `game-seo.ts` is the authoritative source; the `.swf` filename convention is descriptive, not enforced.

### Git commits

When committing, always load and follow the **git-commit** skill from `~/.agents/skills/git-commit/SKILL.md`. It handles conventional commit messages, intelligent staging, and message generation from the diff.

## Where NOT to look (save tokens)

These directories and files are **generated / boilerplate / irrelevant** for most tasks:

| Path                 | Why skip                                                                 |
| -------------------- | ------------------------------------------------------------------------ |
| `dist/`              | Build output — never manually inspect or edit                            |
| `.astro/`            | Generated TypeScript types — never edit                                  |
| `node_modules/`      | Dependencies — never relevant                                            |
| `public/ruffle/`     | Vendored WASM binary — never modify                                      |
| `public/games/run3/` | Vendored HTML5 game bundle — never modify (unless updating Run 3 itself) |
| `astro.config.mjs`   | Static Astro config — rarely changes                                     |
| `tsconfig.json`      | Standard strict TS config — rarely changes                               |
| `.gitignore`         | Standard ignores — rarely changes                                        |
| `postcss.config.cjs` | Dead — Tailwind v4 uses Vite plugin, not PostCSS                         |
| `wrangler.jsonc`     | Dead — Cloudflare Workers config for a Vercel-deployed site              |

## Quick reference — key files by task

| Task                        | File(s) to edit                                                      |
| --------------------------- | -------------------------------------------------------------------- |
| Add a new game              | `src/data/game-seo.ts` + `src/pages/index.astro` + `public/llms.txt` |
| Fix SEO for a game          | `src/data/game-seo.ts`                                               |
| Change homepage layout      | `src/pages/index.astro`                                              |
| Change global layout/SEO    | `src/layout/layout.astro`                                            |
| Change game tile appearance | `src/components/gametile.astro`                                      |
| Change Flash/Ruffle loading | `src/components/flash.astro`                                         |
| Change global styles        | `src/styles/styles.css`                                              |
| Add/edit a page slug        | `src/data/game-seo.ts` key (plus `index.astro` list)                 |
| Change deployment           | `package.json` scripts                                               |
| Add/edit dependency         | `bun add <package>` (not npm)                                        |
| Remove dead config          | `postcss.config.cjs`, `wrangler.jsonc`                               |

## Technology stack

- **Astro v6** — static site generator; pages are `.astro` files under `src/pages/`
- **Tailwind CSS v4** — utility-first CSS (via `@tailwindcss/vite` plugin in `astro.config.mjs`)
- **Ruffle** — Flash emulator running in-browser via WebAssembly (ships `ruffle.js` + `.wasm` under `public/ruffle/`)
- **Vercel Analytics & Speed Insights** — tracking and performance monitoring (plain script tags in layout, no packages)
- **No React** — `@astrojs/react` was removed; zero React components exist
- **Astro prefetch** — enabled globally for faster page transitions (uses `data-astro-prefetch` on links)
- **Vercel** — static site deployment host (via git integration, not CLI)
