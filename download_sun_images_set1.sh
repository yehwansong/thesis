#!/bin/bash
SAVE_DIR="sun_images"
TARGET=100
mkdir -p "$SAVE_DIR"
COUNT=0

QUERIES=(
  "sun" "solar+flare" "sunspot" "solar+eclipse" "sun+corona"
  "solar+prominence" "solar+disk" "sun+chromosphere" "NASA+sun"
  "sun+photosphere" "solar+wind" "coronal+mass+ejection"
  "sun+ultraviolet" "solar+granulation" "sun+X-ray"
  "heliostat" "solar+observation" "sun+hydrogen+alpha"
  "solar+active+region" "sun+infrared"
)

for QUERY in "${QUERIES[@]}"; do
  [ "$COUNT" -ge "$TARGET" ] && break
  echo "[$COUNT/$TARGET] $QUERY"

  SEARCH=$(curl -s "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${QUERY}&srnamespace=6&srlimit=6&format=json" -H "User-Agent: SunImageCollector/1.0")
  TITLES=$(echo "$SEARCH" | grep -o '"title":"File:[^"]*"' | sed 's/"title":"//;s/"//')

  while IFS= read -r TITLE; do
    [ "$COUNT" -ge "$TARGET" ] && break
    [ -z "$TITLE" ] && continue

    ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$TITLE'''))" 2>/dev/null || echo "$TITLE" | sed 's/ /%20/g')
    INFO=$(curl -s "https://en.wikipedia.org/w/api.php?action=query&titles=${ENCODED}&prop=imageinfo&iiprop=url&iiurlwidth=1000&format=json" -H "User-Agent: SunImageCollector/1.0")

    IMG_URL=$(echo "$INFO" | grep -o '"thumburl":"[^"]*"' | head -1 | sed 's/"thumburl":"//;s/"//' | sed 's/\\//g')
    [ -z "$IMG_URL" ] && IMG_URL=$(echo "$INFO" | grep -o '"url":"https[^"]*\.\(jpg\|jpeg\|png\)"' | head -1 | sed 's/"url":"//;s/"//')
    [ -z "$IMG_URL" ] && continue

    EXT="${IMG_URL##*.}"; EXT="${EXT%%\?*}"; EXT=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')
    [[ ! "$EXT" =~ ^(jpg|jpeg|png)$ ]] && continue

    COUNT=$((COUNT + 1))
    SAFE=$(echo "$TITLE" | sed 's/File://;s/[^a-zA-Z0-9._-]/_/g' | cut -c1-60)
    FILE="$SAVE_DIR/$(printf '%03d' $COUNT)_${SAFE}.${EXT}"

    curl -sL "$IMG_URL" -o "$FILE" -H "User-Agent: SunImageCollector/1.0"
    KB=$(du -k "$FILE" | cut -f1)
    echo "  [$COUNT] $SAFE (${KB}KB)"
    sleep 0.3

  done <<< "$TITLES"
done

echo ""
echo "Done. $COUNT images saved to ./$SAVE_DIR/"
