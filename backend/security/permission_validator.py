from security.roles import ROLES
from security.permissions import check_permission


def validate_permission(role, tool):

    check_permission(tool)

    allowed_tools = ROLES.get(role, [])

    if tool not in allowed_tools:
        raise Exception(
            f"Role '{role}' cannot execute tool '{tool}'"
        )

    return True