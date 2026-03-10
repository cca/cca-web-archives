# CCA Website Archive Gallery

An Astro-based filterable gallery for archived institutional websites.

## 🚀 Project Structure

Inside of your Astro project, you'll see the following folders and files:

```text
/
├── public/          # Static assets (favicons, etc.)
├── src/
│   ├── components/  # Astro components (ArchiveCard.astro)
│   ├── content/     # Archived website data (JSON files)
│   ├── pages/       # Website routes (index.astro)
│   └── content.config.ts # Data schema and collection setup
├── .github/
│   └── workflows/   # CI/CD deployment to GitHub Pages
└── package.json
```

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

| Command           | Action                                           |
| :---------------- | :----------------------------------------------- |
| `pnpm install`    | Installs dependencies                            |
| `pnpm dev`        | Starts local dev server at `localhost:4321`      |
| `pnpm build`      | Build your production site to `./dist/`          |
| `pnpm preview`    | Preview your build locally, before deploying     |
| `pnpm check`      | Validate Astro and TypeScript                    |
| `pnpm lint`       | Run ESLint to check code quality                 |
| `pnpm format`     | Format codebase with Prettier                    |
| `pnpm test`       | Run all CI checks (check + lint)                 |

## 🛠️ CI/CD & Maintenance

- **Deployment:** The site is automatically deployed to GitHub Pages on every push to the `main` branch via GitHub Actions using **pnpm**.
- **Updates:** Dependabot is configured to check for **pnpm** updates weekly.
- **Linting:** ESLint (Flat Config) and Prettier are integrated to maintain code standards.
