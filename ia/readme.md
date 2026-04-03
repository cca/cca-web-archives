# Internet Archive

https://archive.org/developers/internetarchive/index.html

https://archive.org/developers/metadata-schema/index.html

## Setup

Enter Internet Archive credentials into the .env file. Look up the CCA/C Archives account in Dashlane.

```sh
uv sync # install python project
cp example.env .env
vim .env # edit in IA S3 credentials
```

## Test

```sh
uv run pytest # run tests
uv run ruff check . --fix # lint files and auto-fix
```
