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
| `npm install`     | Installs dependencies                            |
| `npm run dev`     | Starts local dev server at `localhost:4321`      |
| `npm run build`   | Build your production site to `./dist/`          |
| `npm run preview` | Preview your build locally, before deploying     |
| `npm run check`   | Validate Astro and TypeScript                    |
| `npm run lint`    | Run ESLint to check code quality                 |
| `npm run format`  | Format codebase with Prettier                    |
| `npm run test`    | Run all CI checks (check + lint)                 |

## 🛠️ CI/CD & Maintenance

- **Deployment:** The site is automatically deployed to GitHub Pages on every push to the `main` branch via GitHub Actions.
- **Updates:** Dependabot is configured to check for npm updates weekly.
- **Linting:** ESLint (Flat Config) and Prettier are integrated to maintain code standards.
