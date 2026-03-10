#!/bin/bash

set -euo pipefail

MANIFEST_PATH="custom_components/plant_mk/manifest.json"

if [[ ! -f "$MANIFEST_PATH" ]]; then
    echo "ERROR: Missing $MANIFEST_PATH"
    exit 1
fi

echo "Podaj nowa wersje (np. 1.0.11):"
read -r VERSION

if [[ -z "${VERSION}" ]]; then
    echo "ERROR: Version cannot be empty"
    exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z]+)?$ ]]; then
    echo "ERROR: Version format is invalid (expected semver-like format, e.g. 1.0.11)"
    exit 1
fi

TAG="v$VERSION"

if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "ERROR: Tag $TAG already exists locally"
    exit 1
fi

if git ls-remote --tags origin "refs/tags/$TAG" | grep -q "$TAG"; then
    echo "ERROR: Tag $TAG already exists on origin"
    exit 1
fi

CURRENT_BRANCH="$(git branch --show-current)"
if [[ -z "$CURRENT_BRANCH" ]]; then
    echo "ERROR: Could not detect current branch"
    exit 1
fi

echo "Podaj opis zmian (commit message):"
read -r MESSAGE

if [[ -z "${MESSAGE}" ]]; then
    MESSAGE="Release $TAG"
fi

echo "Updating $MANIFEST_PATH version to $VERSION"
sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" "$MANIFEST_PATH"

if [[ -f "package.json" ]]; then
    echo "Updating package.json version to $VERSION"
    npm version "$VERSION" --no-git-tag-version

    echo "Running npm build"
    npm run build
fi

echo "Staging release files"
git add "$MANIFEST_PATH"
if [[ -f "package.json" ]]; then
    git add package.json
fi

if git diff --cached --quiet; then
    echo "No staged changes to commit"
    exit 1
fi

git commit -m "$MESSAGE ($TAG)"
git tag -a "$TAG" -m "$TAG"

echo "Pushing branch $CURRENT_BRANCH"
git push origin "$CURRENT_BRANCH"
echo "Pushing tag $TAG"
git push origin "$TAG"

echo "Done: released $TAG"