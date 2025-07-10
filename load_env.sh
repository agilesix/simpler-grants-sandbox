#!/bin/zsh

# Check if .env file exists
if [[ ! -f .env ]]; then
    echo "Error: .env file not found"
    exit 1
fi

# Read .env file line by line
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" == \#* ]] && continue
    
    # Extract variable name (everything before the first =)
    var_name="${line%%=*}"
    
    # Export each valid environment variable
    export "$line"
    echo "Set variable: $var_name"
done < .env

echo "Environment variables loaded successfully"
