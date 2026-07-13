fswatch -0 -r /Users/sankalpomar/Pictures/Screenshots | while IFS= read -r -d '' file
do
    sleep 1

    echo "New file detected: $file. Sending to backend..."
    payload=$(jq -n --arg path "$file" '{path: $path}')

    curl -X POST http://localhost:1000/ingest \
         -H "Content-Type: application/json" \
         -d "$payload"
         
    echo -e "\n---"
done
