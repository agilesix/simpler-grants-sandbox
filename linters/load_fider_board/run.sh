#! /bin/bash
# Propagate project metadata from parent issues to their children
# Usage:
# ./linters/bulk_inherit_metadata/run.sh \
#   --org HHS \
#   --project 12

# #######################################################
# Define helper functions
# #######################################################

set -euo pipefail

log() { echo "[info] $1"; }
err() { echo "[error] $1" >&2; exit 1; }

pluck_field() {
  local json_data="$1"
  local field_path="$2"
  local default_value="${3:-}"
  jq -r "$field_path" <<< "$json_data"
}

check_required_args() {
  local args=("$@")
  local missing_args=()
  
  for arg in "${args[@]}"; do
    if [[ -z "${!arg:-}" ]]; then
      missing_args+=("$arg")
    fi
  done
  
  if [[ ${#missing_args[@]} -gt 0 ]]; then
    err "Missing required arguments: ${missing_args[*]}"
  fi
}

# #######################################################
# Parse command line args with format `--option arg`
# #######################################################

# see this stack overflow for more details:
# https://stackoverflow.com/a/14203146/7338319
batch=100
state=open
dry_run=NO
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      log "Running in dry run mode"
      dry_run=YES
      shift # past argument
      ;;
    --batch)
      batch="$2"
      shift # past argument
      shift # past value
      ;;
    --org)
      org="$2"
      shift # past argument
      shift # past value
      ;;
    --repo)
      repo="$2"
      shift # past argument
      shift # past value
      ;;
    --label)
      label="$2"
      shift # past argument
      shift # past value
      ;;
    --board)
      board="$2"
      shift # past argument
      shift # past value
      ;;
    --state)
      state="$2"
      shift # past argument
      shift # past value
      ;;
    -*|--*)
      err "Unknown option $1"
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

check_required_args "org" "repo" "label" "board"

# #######################################################
# Set temp file for issue export
# #######################################################

mkdir -p ./tmp

gh_issue_urls="./tmp/gh-issue-urls.txt"
gh_issue_data="./tmp/gh-issue-data.json"
fider_post_data="./tmp/fider-posts.json"
fider_issue_urls="./tmp/fider-issue-urls.txt"
issues_to_add="./tmp/issues-to-add.json"

# #######################################################
# Fetch GitHub issue data
# #######################################################

log "Fetching $state issues from $org/$repo with label '$label'"

# Fetch GitHup issues and save to a JSON file with the following format:
# {
#   "https://github.com/agilesix/simpler-grants-sandbox/issues/1": {
#     "title": "Issue 1",
#     "description": "Description of issue 1"
#   },
#}
gh issue list \
  --repo "$org/$repo" \
  --label "$label" \
  --json "url,title,body" \
  --limit $batch \
  --state "${state:-open}" \
  --jq '
    map({ (.url): { title: .title, description: .body } }) | add
  ' > $gh_issue_data

log "Found $(jq -r 'keys | length' $gh_issue_data) GitHub issues"

# #######################################################
# Fetch current Fider posts
# #######################################################

log "Fetching current Fider posts from $board.fider.io"

# Fetch Fider posts and save to a JSON file with the following format:
# [
#   {
#     "id": 1,
#     "title": "Post 1",
#     "description": "Description of post 1"
#   },
# ]
curl -X GET \
  -H "Authorization: Bearer $FIDER_API_KEY" \
  "https://$board.fider.io/api/v1/posts" \
  | jq "." > $fider_post_data

if [[ ! -s $fider_post_data ]]; then
  err "Failed to fetch Fider posts or received empty response"
fi

log "Loaded $(wc -l < $fider_post_data) Fider posts"


# #######################################################
# Isolate new issues
# #######################################################

# 1. Load Fider posts into a map
# 2. Load GitHub issues into a map
# 3. Compare the two maps and output the differences (i.e. new issues)

log "Checking which GitHub issues need to be added to Fider"

# Create a temporary file with Fider issue URLs for easy checking
jq -r '.[] | .description // empty' $fider_post_data \
  | grep -oe "https://github.com/$org/$repo/issues/[0-9]\+" > $fider_issue_urls

# Iterate through each GitHub issue URL
jq -r 'keys[]' $gh_issue_data | while read -r issue_url; do
  if grep -q "^${issue_url}$" $fider_issue_urls; then
    log "Skipping $issue_url - already exists in Fider"
  else
    log "Creating new Fider post for $issue_url"
    issue_data=$(jq -r ".[\"$issue_url\"]" $gh_issue_data)
    echo "$issue_data"
    
    # TODO: Create Fider post with this data
    curl -X POST \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $FIDER_API_KEY" \
      -d "$issue_data" \
      "https://$board.fider.io/api/v1/posts"
  fi
done
