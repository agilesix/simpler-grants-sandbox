import json
import re

from github import GithubIssueData
from utils import format_post_description, get_env, log, make_request

FIDER_API_TOKEN = get_env("FIDER_API_TOKEN")
BOARD = get_env("FIDER_BOARD")

# #######################################################
# Fider - fetch and parse posts
# #######################################################


def fetch_posts() -> list[dict]:
    """Fetch Fider posts using the API."""
    log(f"Fetching current Fider posts from {BOARD}.fider.io")

    url = f"https://{BOARD}.fider.io/api/v1/posts"
    headers = {"Authorization": f"Bearer {FIDER_API_TOKEN}"}

    posts = make_request(url, headers)
    log(f"Loaded {len(posts)} Fider posts")
    return posts if isinstance(posts, list) else []


def extract_github_urls_from_posts(
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


def create_post(title: str, description: str) -> None:
    """Create a new Fider post."""
    url = f"https://{BOARD}.fider.io/api/v1/posts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIDER_API_TOKEN}",
    }

    data = {"title": title, "description": description}

    make_request(url, headers, method="POST", data=json.dumps(data))
    log("Created Fider post successfully")


def insert_new_posts(
    github_issues: dict[str, GithubIssueData],
    post_urls: set[str],
    *,
    dry_run: bool,
) -> None:
    """Insert new Fider posts."""
    for issue_url, issue_data in github_issues.items():
        # Skip if already in Fider
        if issue_url in post_urls:
            log(f"Skipping {issue_url} - already exists in Fider")
            continue

        # Create new Fider post
        log(f"Creating new Fider post for {issue_url}")
        title = issue_data.title
        description = issue_data.body

        # Format the description using the parsing logic
        formatted_description = format_post_description(issue_url, description)

        # Dry run
        if dry_run:
            log(f"DRY RUN: Would create post with title: {title}")
            log(f"DRY RUN: Formatted description: {formatted_description[:100]}...")
            continue

        # Create new Fider post
        create_post(
            title=title,
            description=formatted_description,
        )
