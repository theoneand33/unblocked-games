# AGENTS.md — How to Change This Codebase

You change code. This doc tells you how to do it right. Keep your style concise, direct, and free of fluff. The user can override any preference.

## 1. Glossary

Use these names. Do not invent synonyms.

- **You** = the agent that reads this doc and edits the repo.
- **We / maintainers** = the team that owns this repo.
- **User** = the person who plays games on the site.
- **Slug** = kebab-case URL segment under `/games/` (for example, `breaking-the-bank`). The slug is the key in `gamesMap`.
- **Game entry** = one record in `src/data/game-seo.ts` (`title`, `description`, `image`, `genre`, `year`, `isFlash`, `gamePath`).
- **Flash game** = `.swf` file that runs through Ruffle. HTML5 game = standalone page with its own bundle.

## 2. What Makes This Project Special — Do Not Break

- **Static first.** Astro builds to static HTML. Do not add a server, database, or runtime API.
- **Ruffle for Flash.** All Flash games use `public/ruffle/` and `src/components/flash.astro`. Do not replace Ruffle or add a second emulator.
- **No React.** The project removed `@astrojs/react`. Do not add React, Vue, or Svelte.
- **SEO is a feature.** `src/data/game-seo.ts` drives `layout.astro` meta tags and JSON-LD. Do not bypass it.
- **Performance matters.** Keep pages light. Do not add large client JS or heavy dependencies.
- **Vercel deploy.** Build is `astro build && bunx pagefind --site dist`. Do not add Cloudflare or other hosts. `wrangler.jsonc` is dead.

## 3. How to Change the Codebase

### 3.1 Commands — Use `bun`, Not `npm`

| Do this         | Do not do this                 |
| --------------- | ------------------------------ |
| `bun install`   | `npm install`                  |
| `bun add <pkg>` | `npm install <pkg>`            |
| `bun run dev`   | `npm run dev`                  |
| `bun run check` | `astro check` alone            |
| `bun run lint`  | `npx prettier --check .` alone |

Gotchas:

- `bun run check` runs `git lfs pull`, then `astro check`, then `astro build`, then `pagefind`. It is slow. Wait for it to finish.
- `bun run lint` runs `prettier --check .`. Fix with `bunx prettier --write .`.
- Tailwind is v4 via `@tailwindcss/vite`. Add theme tokens in `src/styles/styles.css` inside `@theme { }`. Do not create `tailwind.config.js`. The file does not work.
- `postcss.config.cjs` and `wrangler.jsonc` are dead. Do not edit them.

### 3.2 Verify After Every Change

1. Run `bun run check`.
2. Run `bun run lint`.
3. If either fails, fix the error before you commit.

### 3.3 Add a New Game

Follow these steps in order.

1. Put the `.swf` in `public/flash/`. Use lowercase, no spaces. Example: `bloonstd5.swf`.
2. Put the cover image in `public/images/`. Use ~300x200. Example: `bloonstd5cover.webp`.
3. Add one entry to `gamesMap` in `src/data/game-seo.ts`. Key the entry by slug. Set `isFlash: true` and `gamePath: "/flash/<file>.swf"`.
4. Add the slug to `defaultGames` in `src/data/game-seo.ts`. Place it by popularity tier, not at the end. See tiers below.
5. Add the URL to `public/llms.txt`.
6. Use absolute paths for all assets (`/flash/...`, `/images/...`). Never use relative paths.

For a non-Flash HTML5 game, also create `src/pages/games/<slug>.astro`. Copy `run-3.astro` as a template. Set `<base href="...">` and load the bundle with `is:inline`. Do not use the `Flash` component.

Bad: `gamePath: "flash/mygame.swf"` or `Path: "games/mygame"`
Good: `gamePath: "/flash/mygame.swf"` and `Path: "/games/mygame"`

### 3.4 How Pages Work

- `src/data/game-seo.ts` is the single source of truth. `gamesMap[slug].title` is the display name.
- `src/layout/layout.astro` takes `slug` and reads `gamesMap[slug]` to build `<title>`, meta tags, Open Graph, and JSON-LD. For the home page, use `isHome={true}`.
- `src/pages/games/[slug].astro` serves all Flash games. It filters `gamesMap` by `isFlash: true`. Do not create per-game pages for Flash games.
- `src/pages/games/run-3.astro` and `webtris.astro` are exceptions. They use custom templates.
- `src/pages/index.astro` renders `defaultGames` via `<Gametile>`. The array order is the display order. Keep the "Popular" links in sync with the first 9 entries.

### 3.5 Popularity Tiers (Placement Guide)

Place a new slug in the correct tier.

- **Tier 1 — Top:** Happy Wheels, Plants vs Zombies, Run 3, Fireboy and Watergirl, Bloons TD 5, Super Mario 63, Tetris, Pac-Man
- **Tier 2 — Classics:** Fancy Pants, Stick War, Age of War, Madness, Strike Force Heroes, World's Hardest Game, Vex 3, Gun Mayhem 2, Bubble Trouble, QWOP, Crush the Castle, Burrito Bison
- **Tier 3 — Franchises:** Boxhead, Impossible Quiz, Henry Stickmin series, Duck Life series, Learn to Fly series
- **Tier 4 — Established:** Achievement Unlocked, Super Mario Flash, Ultimate Flash Sonic, Swords and Sandals series
- **Tier 5 — Niche:** Doom, Minesweeper, Geography Game USA, Riddle School series, Hobo series

Group series entries as a block.

## 4. Failure Modes — Do Not Do This

We saw these errors in past agent runs. Do not repeat them.

- **Do not kill the wrong process.** Check the process list before you kill anything. Kill only the PID you started.
- **Do not file draft PRs.** Create PRs as ready for review unless the user asks for a draft.
- **Do not overbuild.** Do not add a new package, abstraction, or config when native CSS, Astro, or the standard library solves the task. Ask before you add a dependency. Never use the `gradiants` package.
- **Do not stop early.** Finish the full task and run `bun run check` and `bun run lint` before you report success.
- **Do not make unasked edits.** Edit only the files the task requires. Do not reformat unrelated files or rename slugs.
- **Do not scope-creep a PR.** One task per PR. Do not mix a game addition with a layout refactor.
- **Do not edit build output.** Never edit `dist/`, `.astro/`, `public/ruffle/`, or `public/games/run3/` unless the task is to update that vendored bundle.
- **Do not use relative asset paths.** Always use `/flash/...` and `/images/...`.

## 5. Skills — When to Load Them

| When the user says                                  | Load this skill                                                                       |
| --------------------------------------------------- | ------------------------------------------------------------------------------------- |
| "commit", "stage", "push"                           | `git-commit` — follow `~/.agents/skills/git-commit/SKILL.md` for conventional commits |
| "simplest solution", "ponytail", "yagni", "do less" | `ponytail` — use the laziest solution that works                                      |
| "audit", "what can we delete", "over-engineered"    | `ponytail-review` or `ponytail-audit`                                                 |
| "is there a skill for X", "how do I do X"           | `find-skills`                                                                         |

Do not describe skills in prose. Load the skill file and follow it.

## 6. Where Not to Look

Skip these to save context. They rarely need changes.

| Path                 | Reason                        |
| -------------------- | ----------------------------- |
| `dist/`              | Build output                  |
| `.astro/`            | Generated types               |
| `node_modules/`      | Dependencies                  |
| `public/ruffle/`     | Vendored WASM                 |
| `public/games/run3/` | Vendored HTML5 bundle         |
| `astro.config.mjs`   | Static config, rarely changes |
| `postcss.config.cjs` | Dead                          |
| `wrangler.jsonc`     | Dead                          |

## 7. Quick Reference

| Task                     | File to Edit                                                              |
| ------------------------ | ------------------------------------------------------------------------- |
| Add a Flash game         | `src/data/game-seo.ts` + `public/llms.txt` (`defaultGames` order matters) |
| Fix SEO                  | `src/data/game-seo.ts`                                                    |
| Change home layout       | `src/pages/index.astro`                                                   |
| Change global SEO / head | `src/layout/layout.astro`                                                 |
| Change tile look         | `src/components/gametile.astro`                                           |
| Change Flash loader      | `src/components/flash.astro`                                              |
| Change global style      | `src/styles/styles.css` (`@theme` block)                                  |
