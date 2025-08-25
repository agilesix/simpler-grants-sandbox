#!/usr/bin/env python3
"""
Load GitHub issues into Fider or FeatureBase board
Usage: From the root of the load_pb_board/ directory:
  python run.py \
    --org agilesix \
    --repo simpler-grants-sandbox \
    --label proposal \
    --platform fider \
    --dry-run
"""

import argparse
from dataclasses import dataclass

import fider
import feature_base
from github import fetch_github_issues
from utils import log

# #######################################################
# CLI Argument Parsing
# #######################################################


@dataclass
class CliArgs:
    """Command line arguments for the application."""

    org: str
    repo: str
    label: str
    platform: str
    state: str = "open"
    batch: int = 100
    dry_run: bool = False


def parse_args() -> CliArgs:
    """Parse command line arguments and return a CliArgs dataclass."""
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
    return CliArgs(
        org=args.org,
        repo=args.repo,
        label=args.label,
        platform=args.platform,
        state=args.state,
        batch=args.batch,
        dry_run=args.dry_run,
    )


# #######################################################
# Fider Operations
# #######################################################


def load_fider_from_github(args: CliArgs) -> None:
    """Fetch GitHub issues and use them to populate a Fider board."""
    # Fetch GitHub issues
    github_issues = fetch_github_issues(
        org=args.org,
        repo=args.repo,
        label=args.label,
        state=args.state,
        batch=args.batch,
    )

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


def update_github_from_fider(args: CliArgs) -> None:
    """Fetch posts from Fider and use them to update issues in GitHub."""
    # Fetch Fider posts
    fider_posts = fider.fetch_posts()

    # Extract GitHub URLs from Fider posts
    fider.extract_github_urls_from_posts(
        posts=fider_posts,
        org=args.org,
        repo=args.repo,
    )

    # Update GitHub issues based on Fider posts
    log("Updating GitHub issues based on Fider posts")
    # TODO: Implement GitHub issue updates based on Fider posts
    if args.dry_run:
        log("Dry run: Would update GitHub issues from Fider posts")


# #######################################################
# FeatureBase Operations
# #######################################################


def load_featurebase_from_github(args: CliArgs) -> None:
    """Fetch GitHub issues and use them to populate a FeatureBase board."""
    # Fetch GitHub issues
    github_issues = fetch_github_issues(
        org=args.org,
        repo=args.repo,
        label=args.label,
        state=args.state,
        batch=args.batch,
    )

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


def update_github_from_featurebase(args: CliArgs) -> None:
    """Fetch posts from FeatureBase and use them to update issues in GitHub."""
    # Fetch FeatureBase posts
    featurebase_posts = feature_base.fetch_posts()

    # Extract GitHub URLs from FeatureBase posts
    feature_base.extract_github_urls_from_posts(
        posts=featurebase_posts,
        org=args.org,
        repo=args.repo,
    )

    # Update GitHub issues based on FeatureBase posts
    log("Updating GitHub issues based on FeatureBase posts")
    # TODO: Implement GitHub issue updates based on FeatureBase posts
    if args.dry_run:
        log("Dry run: Would update GitHub issues from FeatureBase posts")


# #######################################################
# Main
# #######################################################


def main() -> int:
    args = parse_args()

    if args.dry_run:
        log("Running in dry run mode")

    if args.platform == "fider":
        load_fider_from_github(args)
    elif args.platform == "featurebase":
        load_featurebase_from_github(args)

    return 0  # success


if __name__ == "__main__":
    exit(main())
