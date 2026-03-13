#!/usr/bin/env bash
# create_psp_json.sh
# Creates PSP games JSON from covers folder only
# Output format matches: https://github.com/igiteam/psp-covers/blob/main/covers/007%20-%20From%20Russia%20with%20Love%20(USA).png

set -e  # Exit on error

# Configuration
OUTPUT_JSON="genesis_games_blastem.json"
COVERS_DIR="covers"
PLACEHOLDER_IMAGE="https://raw.githubusercontent.com/igiteam/psp-covers/refs/heads/master/psp-cover-default.png"
RAW_BASE_URL="https://raw.githubusercontent.com/igiteam/psp-covers/refs/heads/main/covers"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🎮 Sega Genesis Games JSON Generator"
echo "==========================="

# Check if directory exists
if [ ! -d "$COVERS_DIR" ]; then
    echo -e "${RED}❌ Error: $COVERS_DIR directory not found!${NC}"
    echo "Please run this script in the same directory as your covers folder"
    exit 1
fi

# Count files
total_files=$(find "$COVERS_DIR" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) | wc -l | tr -d ' ')
echo -e "${GREEN}📁 Found $total_files images in $COVERS_DIR${NC}"

if [ $total_files -eq 0 ]; then
    echo -e "${RED}❌ No image files found in $COVERS_DIR${NC}"
    exit 1
fi

# Start JSON array
echo "[" > "$OUTPUT_JSON"

# Process each image file
first_file=true
count=0

# Create a temporary file for processing
temp_file=$(mktemp)

# Process files in sorted order
find "$COVERS_DIR" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) | sort > "$temp_file"

while IFS= read -r file; do
    # Get filename without path
    filename=$(basename "$file")
    
    # Remove extension to get clean title
    title=$(echo "$filename" | sed -E 's/\.[^.]*$//')
    
    # URL encode the filename for GitHub raw URL
    # Using printf with %-escaping for better encoding
    encoded_filename=$(printf '%s' "$filename" | 
        sed 's/ /%20/g' | 
        sed 's/\[/%5B/g' | 
        sed 's/\]/%5D/g' | 
        sed 's/(/%28/g' | 
        sed 's/)/%29/g' | 
        sed 's/#/%23/g' | 
        sed 's/&/%26/g' | 
        sed 's/+/%2B/g' | 
        sed 's/:/%3A/g' | 
        sed 's/;/%3B/g' | 
        sed 's/=/%3D/g' | 
        sed 's/?/%3F/g' | 
        sed 's/@/%40/g' | 
        sed 's/\$/%24/g' | 
        sed 's/,/%2C/g' | 
        sed 's/!/%21/g' | 
        sed "s/'/%27/g" | 
        sed 's/"/%22/g')
    
    cover_url="${RAW_BASE_URL}/${encoded_filename}"
    
    # Add comma if not first file
    if [ "$first_file" = true ]; then
        first_file=false
    else
        echo "," >> "$OUTPUT_JSON"
    fi
    
    # Escape double quotes in title
    title_escaped=$(echo "$title" | sed 's/"/\\"/g')
    
    # Write JSON entry
    cat >> "$OUTPUT_JSON" <<EOF
  {
    "title": "$title_escaped",
    "cover_url": "$cover_url",
    "filename": "$filename"
  }
EOF
    
    # Progress indicator
    count=$((count + 1))
    if [ $((count % 50)) -eq 0 ]; then
        echo -e "${YELLOW}⏳ Processed $count/$total_files files...${NC}"
    fi
done < "$temp_file"

# Clean up temp file
rm -f "$temp_file"

# Close JSON array
echo "" >> "$OUTPUT_JSON"
echo "]" >> "$OUTPUT_JSON"

echo "" >> "$OUTPUT_JSON"  # Add newline at end

# Validate JSON if jq is available
if command -v jq &> /dev/null; then
    if jq empty "$OUTPUT_JSON" 2>/dev/null; then
        echo -e "${GREEN}✅ JSON is valid${NC}"
        
        # Show some stats
        total=$(jq length "$OUTPUT_JSON")
        echo -e "${GREEN}📊 Total games in JSON: $total${NC}"
        
        # Show first 3 entries as sample
        echo -e "\n${YELLOW}📋 Sample entries:${NC}"
        jq '.[:3] | map({title: .title, filename: .filename})' "$OUTPUT_JSON"
        
        # Show first URL as example
        first_url=$(jq -r '.[0].cover_url' "$OUTPUT_JSON")
        echo -e "\n${YELLOW}🔗 Example URL:${NC}"
        echo "$first_url"
    else
        echo -e "${RED}❌ JSON validation failed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  jq not installed, skipping validation${NC}"
    echo -e "${GREEN}📊 Total games: $count${NC}"
    echo -e "\n${YELLOW}🔗 First URL example:${NC}"
    head -n 5 "$OUTPUT_JSON" | grep -o '"cover_url": "[^"]*"' | head -1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Successfully created $OUTPUT_JSON${NC}"
echo -e "${YELLOW}📝 File size: $(du -h "$OUTPUT_JSON" | cut -f1)${NC}"