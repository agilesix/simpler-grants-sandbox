#!/usr/bin/env python3
"""
Load GitHub issues into Fider or FeatureBase board
Usage: From the root of the load_pb_board/ directory:
  python run.py \
    --org agilesix \
    --repo simpler-grants-sandbox \
    --label label \
    --platform fider \
    --dry-run
"""

import argparse

import fider
import feature_base
from github import fetch_github_issues
from utils import log

# #######################################################
# Main
# #######################################################


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Load GitHub issues into Fider or FeatureBase board"
    )
    parser.add_argument("--org", required=True, help="GitHub organization")
    parser.add_argument("--repo", required=True, help="GitHub repository")
    parser.add_argument("--label", required=True, help="GitHub issue label")
    parser.add_argument(
        "--platform",
        required=True,
        choices=["fider", "featurebase"],
        help="Platform to use (fider or featurebase)",
    )
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

    if args.platform == "fider":
        # Fetch Fider posts
        fider_posts = fider.fetch_posts()

        # Extract GitHub URLs from Fider posts
        post_urls = fider.extract_github_urls_from_posts(
            posts=fider_posts,
            org=args.org,
            repo=args.repo,
        )

        # Check which GitHub issues need to be added
        log("Checking which GitHub issues need to be added to Fider")
        fider.insert_new_posts(
            github_issues=github_issues,
            post_urls=post_urls,
            dry_run=args.dry_run,
        )

    elif args.platform == "featurebase":
        # Fetch FeatureBase posts
        featurebase_posts = feature_base.fetch_posts()

        # Extract GitHub URLs from FeatureBase posts
        post_urls = feature_base.extract_github_urls_from_posts(
            posts=featurebase_posts,
            org=args.org,
            repo=args.repo,
        )

        # Check which GitHub issues need to be added
        log("Checking which GitHub issues need to be added to FeatureBase")
        feature_base.insert_new_posts(
            github_issues=github_issues,
            post_urls=post_urls,
            dry_run=args.dry_run,
        )

    return 0  # success


if __name__ == "__main__":
    exit(main())
