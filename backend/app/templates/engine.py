"""Template engine for customizable notification messages."""

from jinja2 import Environment, BaseLoader, TemplateNotFound, TemplateSyntaxError
from typing import Dict, Any, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


# Default templates for each event type
DEFAULT_TEMPLATES = {
    "push": """
🚀 **Push to {{ project }}**

👤 {{ author }} pushed {{ commit_count }} commit(s) to `{{ ref }}`

{% if commits %}
📝 **Commits:**
{% for commit in commits[:3] %}
  • {{ commit.message | truncate(60) }} - {{ commit.author.name }}
{% endfor %}
{% if commits|length > 3 %}
  ... and {{ commits|length - 3 }} more
{% endif %}
{% endif %}

🔗 {{ project_url }}
""",

    "merge_request": """
🔀 **Merge Request {{ mr_action }}**

👤 {{ author }}: {{ mr_title }}

{{ mr_description | truncate(200) }}

`{{ source_branch }}` → `{{ target_branch }}`

Status: **{{ mr_state }}**

🔗 {{ mr_url }}
""",

    "pipeline": """
{% if pipeline_status == 'success' -%}
✅
{%- elif pipeline_status == 'failed' -%}
❌
{%- else -%}
⚙️
{%- endif %} **Pipeline {{ pipeline_status }}**

👤 {{ author }}
📦 Project: {{ project }}
🌿 Branch: {{ ref }}

{% if pipeline_duration %}⏱️ Duration: {{ pipeline_duration }}s{% endif %}

🔗 {{ pipeline_url }}
""",

    "issue": """
🐛 **Issue {{ issue_action }}**

👤 {{ author }}: {{ issue_title }}

{{ issue_description | truncate(200) }}

Status: **{{ issue_state }}**

🔗 {{ issue_url }}
""",

    "release": """
🎉 **New Release: {{ release_name }}**

📦 Project: {{ project }}
🏷️ Tag: {{ release_tag }}

{{ release_description | truncate(300) }}

🔗 {{ release_url }}
""",

    "deployment": """
🚢 **Deployment to {{ deployment_environment }}**

👤 {{ author }}
📦 Project: {{ project }}
🌿 Branch: {{ ref }}

Status: **{{ deployment_status }}**

🔗 {{ deployment_url }}
""",

    "default": """
📢 **{{ event_type }} event**

👤 {{ author }}
📦 Project: {{ project }}

{% if ref %}🌿 Branch: {{ ref }}{% endif %}
"""
}


class MemoryLoader(BaseLoader):
    """Jinja2 loader that loads templates from memory/database."""

    def __init__(self, templates: Dict[str, str]):
        self.templates = templates

    def get_source(self, environment, template):
        if template not in self.templates:
            raise TemplateNotFound(template)
        source = self.templates[template]
        return source, None, lambda: True


class TemplateEngine:
    """Template engine for rendering notification messages."""

    def __init__(self, custom_templates: Optional[Dict[str, str]] = None):
        """
        Initialize template engine.

        Args:
            custom_templates: Dictionary of custom templates {event_type: template_string}
        """
        # Merge custom templates with defaults
        templates = DEFAULT_TEMPLATES.copy()
        if custom_templates:
            templates.update(custom_templates)

        # Create Jinja2 environment
        loader = MemoryLoader(templates)
        self.env = Environment(
            loader=loader,
            autoescape=False,  # Don't escape for Markdown/HTML formatting
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.env.filters['truncate'] = self._truncate_filter

    @staticmethod
    def _truncate_filter(value: str, length: int = 100, suffix: str = "...") -> str:
        """Truncate string to given length."""
        if not value:
            return ""
        if len(value) <= length:
            return value
        return value[:length].rsplit(' ', 1)[0] + suffix

    def render(self, event_type: str, context: Dict[str, Any]) -> str:
        """
        Render template for given event type.

        Args:
            event_type: Event type (push, merge_request, etc.)
            context: Template context (variables)

        Returns:
            Rendered message string

        Raises:
            TemplateNotFound: If template not found
            TemplateSyntaxError: If template has syntax errors
        """
        try:
            # Use specific template or fallback to default
            template_name = event_type if event_type in self.env.list_templates() else "default"
            template = self.env.get_template(template_name)

            # Render with context
            rendered = template.render(**context)

            # Clean up whitespace
            rendered = rendered.strip()

            logger.debug(f"Rendered template for {event_type}")
            return rendered

        except TemplateNotFound:
            logger.error(f"Template not found: {event_type}")
            raise
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error in {event_type}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error rendering template {event_type}: {e}")
            raise

    def validate_template(self, template_string: str) -> tuple[bool, Optional[str]]:
        """
        Validate template syntax.

        Args:
            template_string: Template string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self.env.from_string(template_string)
            return True, None
        except TemplateSyntaxError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"


# Global template engine instance
_template_engine: Optional[TemplateEngine] = None


def get_template_engine() -> TemplateEngine:
    """Get or create global template engine instance."""
    global _template_engine
    if _template_engine is None:
        _template_engine = TemplateEngine()
    return _template_engine
