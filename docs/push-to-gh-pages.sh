#!/bin/bash
set -e

# Deploy local repo to cca org on GitHub and enable Pages
# Usage: ./deploy-to-cca-org.sh [repo-name]
# If no repo name provided, uses current directory name

REPO_NAME=$(basename "$PWD")
ORG="cca"

# Create git repo
if ! git status &>/dev/null; then
  echo "📁 Initializing new git repository..."
  git init
  git add .
  git commit -m "Initial commit"
fi

echo "📦 Creating GitHub repo: $ORG/$REPO_NAME"
gh repo create "$ORG/$REPO_NAME" --public --source=. --remote=origin --push

echo "📄 Enabling GitHub Pages..."
gh api repos/${ORG}/"${REPO_NAME}"/pages \
  -F source[branch]=main \
  -F source[path]=/ \
  --method POST \
  || echo "⚠️  Pages may already be enabled or needs manual configuration"

gh repo edit "$ORG/$REPO_NAME" --description "Web archive of $REPO_NAME" --homepage "https://$ORG.github.io/$REPO_NAME"

echo "✅ Done! Pages will be available at: https://$ORG.github.io/$REPO_NAME"
