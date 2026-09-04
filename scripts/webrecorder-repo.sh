#!/usr/bin/env bash
set -euo pipefail
# Scaffold out a git repo for a Webrecorder .WACZ file
# Usage: ./scripts/webrecorder-repo.sh <path-to-wacz-file>
# Creates the repo in the same directory as the WACZ.
# I recommend naming the WACZ DOMAIN.wacz e.g. www.example.com.wacz
FILE="$1"
if [[ ! -f "$FILE" ]]; then
  echo "Error: File '$FILE' does not exist."
  echo "Usage: $0 www.example.com.wacz"
  exit 1
fi

FILE_NAME="$(basename "$FILE")"
REPO_NAME="$(basename "$FILE" .wacz)"
cd "$(dirname "$FILE")"
mkdir -p "$REPO_NAME"
cd "$REPO_NAME"
git init

echo "Making service worker JS script"
mkdir replay
echo "importScripts(\"https://cdn.jsdelivr.net/npm/replaywebpage@2.4.6/sw.js\")" > replay/sw.js

echo "Making gh pages deploy workflow with git lfs enabled"
mkdir -p .github/workflows
wget https://raw.githubusercontent.com/cca/scaffold.architecture.cca.edu/refs/heads/main/.github/workflows/deploy.yml -O .github/workflows/deploy.yml

echo "Writing readme.md"
HASH='#' # Way to escape hashmark so it's not interpreted as a comment
cat <<EOF > readme.md
$HASH $REPO_NAME

This is an archive of the CCA $REPO_NAME website. It was archived using \[Webrecorder\]\(https://webrecorder.net\).

© 2026 California College of the Arts.
EOF

echo "Writing index.html"
cat <<EOF > index.html
<html>
<head>
    <title>$REPO_NAME</title>
    <link rel="canonical" href="https://$REPO_NAME/" />
    <meta content="website" property="og:type" />
    <meta content="https://$REPO_NAME/" property="og:url" />
    <meta content="" property="og:site_name" />
    <meta content="" property="og:image" />
    <meta content="" property="og:title" />
    <meta property="og:description" content="" />
    <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "WebSite",
          "url": "https://$REPO_NAME/",
          "description": "",
        }
    </script>
</head>
<body>
    <script src="https://cdn.jsdelivr.net/npm/replaywebpage@2.4.6/ui.js"></script>

    <replay-web-page source="./$FILE_NAME" url="https://$REPO_NAME/"></replay-web-page>
</body>
</html>
EOF
git add index.html readme.md replay/
git commit -m "initial commit"

# add WACZ file
cp -v "$FILE" .
git lfs install
git lfs track "*.wacz"
git add .gitattributes
git lfs migrate import --include="*.wacz" --everything
git add .
git commit -m "Add $FILE_NAME with git lfs"

echo
echo "Webrecorder repository for $REPO_NAME has been successfully created."
echo "Edit index.html to reflect the site's metadata."
