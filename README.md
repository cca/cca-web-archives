# CCA Website Archive Gallery

An Astro-based filterable gallery for archived institutional websites.

## Structure

`ia` has Internet Archive utilities for checking IA coverage of a site.

`rrr` was code for downloading _Rewind Review Respond_ journal issues from the main site.

Astro files: public contains thumbnail images, src is code, src/content is individual archived site JSON files.

`scripts` are miscellaneous utilities for working with web archives.

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

| Command        | Action                                       |
| :------------- | :------------------------------------------- |
| `pnpm install` | Installs dependencies                        |
| `pnpm dev`     | Starts local dev server at `localhost:4321`  |
| `pnpm build`   | Build your production site to `./dist/`      |
| `pnpm preview` | Preview your build locally, before deploying |
| `pnpm check`   | Validate Astro and TypeScript                |
| `pnpm lint`    | Run ESLint to check code quality             |
| `pnpm format`  | Format codebase with Prettier                |
| `pnpm test`    | Run all CI checks (check + lint)             |
