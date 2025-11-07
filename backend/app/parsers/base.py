"""Base parser for Git webhooks"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from abc import ABC, abstractmethod


class ParsedEvent(BaseModel):
    """Standardized parsed event structure"""

    platform: str  # "gitlab", "github", "bitbucket"
    event_type: str  # "push", "merge_request", "issue", etc.
    project: str  # "edcom/edcom-server"
    project_url: str
    author: str
    author_username: str
    author_avatar: Optional[str] = None

    # Event-specific data
    ref: Optional[str] = None  # Branch/tag name
    commits: Optional[List[Dict[str, Any]]] = None
    commit_count: Optional[int] = None

    # Merge/Pull Request
    mr_iid: Optional[int] = None
    mr_title: Optional[str] = None
    mr_description: Optional[str] = None
    mr_url: Optional[str] = None
    mr_state: Optional[str] = None
    mr_action: Optional[str] = None
    source_branch: Optional[str] = None
    target_branch: Optional[str] = None

    # Issue
    issue_iid: Optional[int] = None
    issue_title: Optional[str] = None
    issue_description: Optional[str] = None
    issue_url: Optional[str] = None
    issue_state: Optional[str] = None
    issue_action: Optional[str] = None

    # Pipeline/CI
    pipeline_id: Optional[int] = None
    pipeline_status: Optional[str] = None
    pipeline_url: Optional[str] = None
    pipeline_duration: Optional[int] = None
    pipeline_stages: Optional[List[str]] = None

    # Comment
    comment_body: Optional[str] = None
    comment_url: Optional[str] = None

    # Raw data for advanced usage
    raw_data: Dict[str, Any] = {}


class BaseParser(ABC):
    """Base class for Git platform parsers"""

    @abstractmethod
    def can_parse(self, headers: Dict[str, str], payload: Dict[str, Any]) -> bool:
        """Check if this parser can handle the webhook"""
        pass

    @abstractmethod
    def parse(self, headers: Dict[str, str], payload: Dict[str, Any]) -> ParsedEvent:
        """Parse webhook payload into standardized format"""
        pass

    @staticmethod
    def _truncate(text: str, max_length: int = 200) -> str:
        """Truncate text to max_length"""
        if not text:
            return ""
        text = text.strip()
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
