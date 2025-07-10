import json
import re

from utils import get_env, log, make_request

FIDER_API_TOKEN = get_env("FIDER_API_TOKEN")

# #######################################################
# Fider - fetch and parse posts
# #######################################################


def fetch_fider_posts(board: str) -> list[dict]:
    """Fetch Fider posts using the API."""
    log(f"Fetching current Fider posts from {board}.fider.io")

    url = f"https://{board}.fider.io/api/v1/posts"
    headers = {"Authorization": f"Bearer {FIDER_API_TOKEN}"}

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
        "Authorization": f"Bearer {FIDER_API_TOKEN}",
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
