"""Git platform parsers"""

from typing import Dict, Any
from app.parsers.base import BaseParser, ParsedEvent
from app.parsers.gitlab import GitLabParser
from app.parsers.github import GitHubParser
from app.parsers.bitbucket import BitbucketParser


def get_parser(headers: Dict[str, Any]) -> BaseParser:
    """
    Get appropriate parser based on request headers.

    Args:
        headers: Request headers

    Returns:
        Parser instance

    Raises:
        ValueError: If platform cannot be determined
    """
    # Normalize headers to lowercase
    headers_lower = {k.lower(): v for k, v in headers.items()}

    # Detect platform from headers
    if "x-gitlab-event" in headers_lower:
        return GitLabParser()
    elif "x-github-event" in headers_lower:
        return GitHubParser()
    elif "x-event-key" in headers_lower:
        return BitbucketParser()
    else:
        raise ValueError(
            "Unknown webhook platform. Expected GitLab (X-Gitlab-Event), "
            "GitHub (X-GitHub-Event), or Bitbucket (X-Event-Key) headers."
        )


__all__ = [
    "BaseParser",
    "ParsedEvent",
    "GitLabParser",
    "GitHubParser",
    "BitbucketParser",
    "get_parser",
]
