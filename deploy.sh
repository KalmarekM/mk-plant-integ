#!/bin/bash

# 1. Pytamy o wersję i opis
echo "🏷️ Podaj nową wersję (np. 1.0.9):"
read VERSION
echo "📝 Podaj opis zmian (commit message):"
read MESSAGE

# 2. Aktualizacja wersji w manifest.json (Używamy sed z Git Bash)
MANIFEST_PATH="custom_components/plant_mk/manifest.json"

if [ -f "$MANIFEST_PATH" ]; then
    echo "🆙 Aktualizacja wersji w manifest.json do $VERSION..."
    # 'sed -i' w Git Bash na Windows czasem wymaga pustego rozszerzenia dla backupu: sed -i '' 
    # ale zazwyczaj standardowe -i działa.
    sed -i "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" "$MANIFEST_PATH"
else
    echo "⚠️ Nie znaleziono pliku $MANIFEST_PATH!"
fi

# 3. Aktualizacja package.json (tylko jeśli istnieje - dla Twojej karty JS)
if [ -f "package.json" ]; then
    echo "🆙 Aktualizacja wersji w package.json..."
    npm version "$VERSION" --no-git-tag-version
    
    echo "🚀 Budowanie projektu (npm)..."
    if npm run build; then
        echo "✅ Kompilacja udana."
    else
        echo "❌ BŁĄD KOMPILACJI! Przerywam."
        exit 1
    fi
fi

# 4. Git Add & Commit
echo "📦 Dodawanie zmian do Git..."
git add .
git commit -m "$MESSAGE (v$VERSION)"

# 5. Push i Tagi
echo "☁️ Wysyłanie do GitHub..."
if git push origin main && git tag "v$VERSION" && git push origin "v$VERSION"; then
    echo "✅ Sukces! Wersja v$VERSION opublikowana."
else
    echo "❌ Błąd Git! Sprawdź połączenie z serwerem."
    exit 1
fi