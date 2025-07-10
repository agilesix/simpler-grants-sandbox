#!/usr/bin/env python3
"""
Shared utilities for the GitHub to Fider loader.
"""

import re
import json
import logging
import os
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
    # Always add a User-Agent header to avoid Cloudflare bot blocking
    headers = dict(headers)  # copy to avoid mutating caller's dict
    if "User-Agent" not in headers:
        headers["User-Agent"] = "Mozilla/5.0 (compatible; FeatureBaseBot/1.0)"
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


# #######################################################
# Formatting
# #######################################################


def format_post_description(url: str, description: str) -> str:
    """Format the post description by extracting content between markdown headers."""
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
