#!/usr/bin/env python3
"""
Load GitHub issues into Fider board
Usage: From the root of the load_pb_board/ directory:
  python run.py \
    --org agilesix \
    --repo simpler-grants-sandbox \
    --label label \
    --board simplergrants \
    --dry-run
"""

import argparse

from fider import (
    extract_github_urls_from_fider_posts,
    fetch_fider_posts,
    insert_new_fider_posts,
)
from github import fetch_github_issues
from utils import log

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
