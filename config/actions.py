import re
from typing import Any

from nemoguardrails.actions import action


DANGEROUS_SQL = re.compile(r"\b(DROP|DELETE|TRUNCATE)\b", re.IGNORECASE)


def contains_dangerous_sql(message: str) -> bool:
    """Return True when a message contains a blocked SQL keyword."""
    return bool(DANGEROUS_SQL.search(message))


@action(is_system_action=True)
async def block_dangerous_sql(context: dict[str, Any] | None = None) -> bool:
    """Inspect the current user message before the main model is called."""
    message = (context or {}).get("user_message", "")
    return contains_dangerous_sql(message)
