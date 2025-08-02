#!/bin/bash

# Script to automatically update sitemap.xml with all generated documentation pages
# Usage: ./update-sitemap.sh

SITEMAP_FILE="sitemap.xml"
DOCS_DIR="docs"
BASE_URL="https://httpdss.github.io/struct"
TODAY=$(date +%Y-%m-%d)

echo "📄 Updating sitemap.xml with generated documentation pages..."

# Backup original sitemap
cp "$SITEMAP_FILE" "${SITEMAP_FILE}.backup"

# Find all HTML files in docs directory
echo "🔍 Finding HTML files in $DOCS_DIR..."
html_files=$(find "$DOCS_DIR" -name "*.html" | sort)

# Count files
file_count=$(echo "$html_files" | wc -l)
echo "📊 Found $file_count HTML files to add to sitemap"

# Create temporary file with new entries
temp_file=$(mktemp)

# Copy everything before </urlset>
sed '/<\/urlset>/d' "$SITEMAP_FILE" > "$temp_file"

# Add comment for generated docs
echo "" >> "$temp_file"
echo "  <!-- Generated Documentation Pages (auto-updated $(date)) -->" >> "$temp_file"
echo "" >> "$temp_file"

# Add each HTML file as a URL entry
while IFS= read -r file; do
  # Convert file path to URL path
  url_path=${file#docs/}

  # Remove index.html from path for cleaner URLs
  if [[ "$url_path" == */index.html ]]; then
    url_path=${url_path%/index.html}/
  fi

  # Add URL entry
  echo "  <url>" >> "$temp_file"
  echo "    <loc>$BASE_URL/$file</loc>" >> "$temp_file"
  echo "    <lastmod>$TODAY</lastmod>" >> "$temp_file"
  echo "    <changefreq>weekly</changefreq>" >> "$temp_file"
  echo "    <priority>0.8</priority>" >> "$temp_file"
  echo "  </url>" >> "$temp_file"
  echo "" >> "$temp_file"
done <<< "$html_files"

# Close urlset
echo "</urlset>" >> "$temp_file"

# Replace original sitemap
mv "$temp_file" "$SITEMAP_FILE"

echo "✅ Sitemap updated successfully!"
echo "📈 Total URLs in sitemap: $(grep -c '<url>' "$SITEMAP_FILE")"
echo "📂 Documentation pages: $(grep -c "docs/" "$SITEMAP_FILE")"
echo ""
echo "💡 Backup created: ${SITEMAP_FILE}.backup"
