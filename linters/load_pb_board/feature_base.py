import json
import re
from typing import Any

from utils import format_post_description, get_env, log, make_request

FEATURE_BASE_API_TOKEN = get_env("FEATURE_BASE_API_TOKEN")
CUSTOM_FIELD_ID = get_env("FEATURE_BASE_GITHUB_FIELD_ID")

# #######################################################
# FeatureBase - fetch and parse posts
# #######################################################


def fetch_posts() -> list[dict]:
    """Fetch FeatureBase posts using the API."""
    log("Fetching current FeatureBase posts from do.featurebase.app")

    # Use the correct URL structure with query parameters
    url = "https://do.featurebase.app/v2/posts?page=1&limit=100"
    headers = {"X-API-Key": FEATURE_BASE_API_TOKEN}

    # Debug: Log the request details (without exposing the full token)
    log(f"Making request to: {url}")
    log(
        f"Using API token: {FEATURE_BASE_API_TOKEN[:10]}...{FEATURE_BASE_API_TOKEN[-4:] if len(FEATURE_BASE_API_TOKEN) > 14 else '***'}"
    )
    log(f"Headers: {list(headers.keys())}")

    response = make_request(url, headers)
    posts = response.get("results", [])
    log(f"Loaded {len(posts)} FeatureBase posts")
    return posts


def extract_github_urls_from_posts(
    posts: list[dict],
    org: str,
    repo: str,
) -> set[str]:
    """Extract GitHub issue URLs from FeatureBase post content and custom fields."""
    log("Extracting GitHub issue URLs from FeatureBase posts")

    pattern = re.compile(f"https://github.com/{org}/{repo}/issues/[0-9]+")
    urls = set()

    for post in posts:
        # Check content field
        content = post.get("content", "")
        if content:
            matches = pattern.findall(content)
            urls.update(matches)

        # Check custom input values using the exact field ID
        github_url = post.get("customInputValues", {}).get(CUSTOM_FIELD_ID)
        if github_url and isinstance(github_url, str):
            matches = pattern.findall(github_url)
            urls.update(matches)

    log(f"Found {len(urls)} GitHub issues already in FeatureBase")
    return urls


# #######################################################
# FeatureBase - create post
# #######################################################


def create_post(
    title: str,
    content: str,
    github_url: str | None = None,
    category: str = "💡 Feature Requests",
) -> None:
    """Create a new FeatureBase post."""
    url = "https://do.featurebase.app/v2/posts"
    headers = {
        "X-API-Key": FEATURE_BASE_API_TOKEN,
        "Content-Type": "application/json",
    }

    data: dict[str, Any] = {
        "title": title,
        "content": content,
        "category": category,
    }

    # Add custom input values if GitHub URL is provided
    if github_url:
        data["customInputValues"] = {CUSTOM_FIELD_ID: github_url}

    make_request(url, headers, method="POST", data=json.dumps(data))
    log("Created FeatureBase post successfully")


def insert_new_posts(
    github_issues: dict[str, dict],
    post_urls: set[str],
    *,
    dry_run: bool,
) -> None:
    """Insert new FeatureBase posts."""
    for issue_url, issue_data in github_issues.items():
        # Skip if already in FeatureBase
        if issue_url in post_urls:
            log(f"Skipping {issue_url} - already exists in FeatureBase")
            continue

        # Create new FeatureBase post
        log(f"Creating new FeatureBase post for {issue_url}")
        title = issue_data.get("title", "")
        description = issue_data.get("description", "")

        # Format the description using the parsing logic
        formatted_content = format_post_description(issue_url, description)

        # Dry run
        if dry_run:
            log(f"DRY RUN: Would create post with title: {title}")
            log(f"DRY RUN: Formatted content: {formatted_content[:100]}...")
            continue

        # Create new FeatureBase post
        create_post(
            title=title,
            content=formatted_content,
            github_url=issue_url,
        )
