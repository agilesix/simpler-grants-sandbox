#!/usr/bin/env python3
"""
GitHub API functionality for fetching issues.
"""

import urllib.parse
from utils import get_env, log, make_request

GITHUB_API_TOKEN = get_env("GITHUB_API_TOKEN")


def fetch_github_issues(
    org: str,
    repo: str,
    label: str,
    state: str = "open",
    batch: int = 100,
) -> dict[str, dict]:
    """Fetch GitHub issues using the GitHub API."""
    log(f"Fetching {state} issues from {org}/{repo} with label '{label}'")

    headers = {
        "Authorization": f"token {GITHUB_API_TOKEN}",
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
