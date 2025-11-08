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

    # Deployment
    deployment_id: Optional[int] = None
    deployment_status: Optional[str] = None
    deployment_environment: Optional[str] = None
    deployment_url: Optional[str] = None

    # Release
    release_name: Optional[str] = None
    release_tag: Optional[str] = None
    release_description: Optional[str] = None
    release_url: Optional[str] = None

    # Job/Build
    job_id: Optional[int] = None
    job_name: Optional[str] = None
    job_stage: Optional[str] = None
    job_status: Optional[str] = None

    # Feature Flag
    feature_flag_name: Optional[str] = None
    feature_flag_description: Optional[str] = None
    feature_flag_active: Optional[bool] = None

    # Emoji
    emoji_name: Optional[str] = None
    emoji_action: Optional[str] = None
    emoji_awardable_type: Optional[str] = None

    # Access Token
    token_name: Optional[str] = None
    token_expires_at: Optional[str] = None

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
