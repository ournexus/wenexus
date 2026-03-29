"""
agent.tools - LangGraph agent tools for roundtable facilitation.

Depends: langchain_core
Consumers: agent.graph
"""

from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_datetime() -> str:
    """Get the current date and time in ISO 8601 format."""
    return datetime.now().isoformat()


@tool
def format_discussion_points(topic: str, perspectives: list[str]) -> str:
    """Format structured discussion points for a topic from multiple perspectives.

    Args:
        topic: The discussion topic or question.
        perspectives: List of perspectives to cover (e.g., ["economic", "social", "technical"]).

    Returns:
        A formatted discussion outline string.
    """
    lines = [f"## Discussion: {topic}", ""]
    for i, perspective in enumerate(perspectives, 1):
        lines.append(f"{i}. **{perspective.capitalize()} perspective**")
        lines.append("   - Key questions to explore from this angle")
        lines.append("   - Potential stakeholders and impacts")
        lines.append("")
    return "\n".join(lines)


@tool
def suggest_expert_roles(topic: str) -> str:
    """Suggest relevant expert roles for a given discussion topic.

    Args:
        topic: The discussion topic to analyze.

    Returns:
        A list of suggested expert roles with rationale.
    """
    return (
        f"For the topic '{topic}', consider inviting experts in:\n"
        "- Domain specialists (subject matter experts)\n"
        "- Practitioners (real-world implementation experience)\n"
        "- Critics / devil's advocates (challenge assumptions)\n"
        "- Facilitators (keep discussion balanced and productive)\n"
        "Adjust based on the specific domain and goals of the roundtable."
    )


TOOLS = [get_current_datetime, format_discussion_points, suggest_expert_roles]
