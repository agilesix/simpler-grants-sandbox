#!/usr/bin/env python3
"""
Load GitHub issues into Fider board
Usage:
  python linters/load_fider_board/run.py \
    --org agilesix \
    --repo simpler-grants-sandbox \
    --label label \
    --board simplergrants \
    --dry-run
"""

import argparse
import json
import logging
import os
import re
import sys
import urllib.parse
import urllib.request

# #######################################################
# Logging
# #######################################################

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def log(message: str) -> None:
    """Log an info message."""
    logger.info(message)


def err(message: str) -> None:
    """Log an error message and exit."""
    logger.error(message)
    sys.exit(1)


# #######################################################
# Environment variables
# #######################################################


def get_env(name: str) -> str:
    """Get an environment variable and exit if it's not set."""
    value = os.environ.get(name)
    if not value:
        err(f"{name} environment variable must be set")
        sys.exit(1)
    return value


GITHUB_TOKEN = get_env("GITHUB_TOKEN")
FIDER_API_KEY = get_env("FIDER_API_KEY")

# #######################################################
# HTTP requests
# #######################################################


def make_request(
    url: str,
    headers: dict[str, str],
    method: str = "GET",
    data: str | None = None,
) -> dict:
    """Make an HTTP request and return JSON response."""
    try:
        req = urllib.request.Request(url, headers=headers, method=method)
        if data:
            req.data = data.encode()

        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.request.HTTPError as e:
        err(f"HTTP request failed: {e.code} - {e.reason}")
        sys.exit(1)
    except json.JSONDecodeError:
        err("Failed to parse JSON response")
        sys.exit(1)
    except Exception as e:
        err(f"Request failed: {e}")
        sys.exit(1)

    # This should never be reached due to sys.exit() calls above
    return {}


# #######################################################
# GitHub
# #######################################################


def fetch_github_issues(
    org: str,
    repo: str,
    label: str,
    state: str = "open",
    batch: int = 100,
) -> dict[str, dict]:
    """Fetch GitHub issues using the GitHub API."""
    log(f"Fetching {state} issues from {org}/{repo} with label '{label}'")

    # Get GitHub token from environment
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        err("GITHUB_TOKEN environment variable must be set")

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = f"https://api.github.com/repos/{org}/{repo}/issues"
    params = {
        "state": state,
        "labels": label,
        "per_page": min(batch, 100),  # GitHub API max is 100
        "page": 1,
    }

    # Build query string using standard library
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"

    issues_data = make_request(full_url, headers)

    # Convert to the same format as the original script
    issues_dict = {}
    for issue in issues_data:
        issue_url = issue.get("html_url")
        issue_title = issue.get("title")

        # Skip if no URL or title
        if not issue_url or not issue_title:
            continue

        # Add to dict
        issues_dict[issue_url] = {
            "title": issue_title,
            "description": issue.get("body", ""),
            "labels": [label["name"] for label in issue.get("labels", [])],
        }

    log(f"Found {len(issues_dict)} GitHub issues")
    return issues_dict


# #######################################################
# Fider - fetch and parse posts
# #######################################################


def fetch_fider_posts(board: str) -> list[dict]:
    """Fetch Fider posts using the API."""
    log(f"Fetching current Fider posts from {board}.fider.io")

    url = f"https://{board}.fider.io/api/v1/posts"
    headers = {"Authorization": f"Bearer {FIDER_API_KEY}"}

    posts = make_request(url, headers)
    log(f"Loaded {len(posts)} Fider posts")
    return posts if isinstance(posts, list) else []


def extract_github_urls_from_fider_posts(
    posts: list[dict],
    org: str,
    repo: str,
) -> set[str]:
    """Extract GitHub issue URLs from Fider post descriptions."""
    log("Extracting GitHub issue URLs from Fider posts")

    pattern = re.compile(f"https://github.com/{org}/{repo}/issues/[0-9]+")
    urls = set()

    for post in posts:
        description = post.get("description", "")
        if description:
            matches = pattern.findall(description)
            urls.update(matches)

    log(f"Found {len(urls)} GitHub issues already in Fider")
    return urls


# #######################################################
# Fider - create post
# #######################################################


def create_fider_post(board: str, title: str, description: str) -> None:
    """Create a new Fider post."""
    url = f"https://{board}.fider.io/api/v1/posts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIDER_API_KEY}",
    }

    data = {"title": title, "description": description}

    make_request(url, headers, method="POST", data=json.dumps(data))
    log("Created Fider post successfully")


def format_post_description(url: str, description: str) -> str:
    """Format the post description by extracting content between markdown headers."""
    import re

    # Extract text between first and second ### headers using regex
    # The pattern matches: ^###\s+.*?\n(.*?)(?=\n###\s+|$)
    # This finds content between the first ### header and either the next ### header or end of string
    pattern = r"""
        ^                # Start of line
        \#\#\#\s+        # Three hash symbols followed by whitespace
        .*?              # Non-greedy match of any characters
        (\n)+            # One or more newlines
        (?P<content>.*?) # Named group: Non-greedy match of any characters (the content we want)
        (?=              # Positive lookahead
            \n\#\#\#\s+  # Newline followed by ### and whitespace
            |            # OR
            $            # End of string
        )
    """
    match = re.search(pattern, description, re.DOTALL | re.MULTILINE | re.VERBOSE)

    if not match:
        # Fallback: use the full description, truncated to 255 characters
        summary = re.sub(r"\s+", " ", description).strip()[:255] + "..."
    else:
        # Clean and limit the extracted text
        extracted_text = match.group("content")
        summary = re.sub(r"\s+", " ", extracted_text).strip()[:150] + "..."

    # Format with GitHub link and summary
    return f"{summary}\n\n[GitHub issue]({url})"


def insert_new_fider_posts(
    board: str,
    github_issues: dict[str, dict],
    fider_urls: set[str],
    *,
    dry_run: bool,
) -> None:
    """Insert new Fider posts."""
    for issue_url, issue_data in github_issues.items():
        # Skip if already in Fider
        if issue_url in fider_urls:
            log(f"Skipping {issue_url} - already exists in Fider")
            continue

        # Create new Fider post
        log(f"Creating new Fider post for {issue_url}")
        title = issue_data.get("title", "")
        description = issue_data.get("description", "")

        # Format the description using the parsing logic
        formatted_description = format_post_description(issue_url, description)

        # Dry run
        if dry_run:
            log(f"DRY RUN: Would create post with title: {title}")
            log(f"DRY RUN: Formatted description: {formatted_description[:100]}...")
            continue

        # Create new Fider post
        create_fider_post(
            board=board,
            title=title,
            description=formatted_description,
        )


# #######################################################
# Main
# #######################################################


def main() -> int:
    parser = argparse.ArgumentParser(description="Load GitHub issues into Fider board")
    parser.add_argument("--org", required=True, help="GitHub organization")
    parser.add_argument("--repo", required=True, help="GitHub repository")
    parser.add_argument("--label", required=True, help="GitHub issue label")
    parser.add_argument("--board", required=True, help="Fider board name")
    parser.add_argument("--state", default="open", help="GitHub issue state")
    parser.add_argument("--batch", type=int, default=100, help="Batch size")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")

    args = parser.parse_args()

    if args.dry_run:
        log("Running in dry run mode")

    # Fetch GitHub issues
    github_issues = fetch_github_issues(
        org=args.org,
        repo=args.repo,
        label=args.label,
        state=args.state,
        batch=args.batch,
    )

    # Fetch Fider posts
    fider_posts = fetch_fider_posts(args.board)

    # Extract GitHub URLs from Fider posts
    fider_urls = extract_github_urls_from_fider_posts(
        posts=fider_posts,
        org=args.org,
        repo=args.repo,
    )

    # Check which GitHub issues need to be added
    log("Checking which GitHub issues need to be added to Fider")
    insert_new_fider_posts(
        board=args.board,
        github_issues=github_issues,
        fider_urls=fider_urls,
        dry_run=args.dry_run,
    )

    return 0  # success


if __name__ == "__main__":
    exit(main())
