#!/usr/bin/env python3
"""
Shared utilities for the GitHub to Fider loader.
"""

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
