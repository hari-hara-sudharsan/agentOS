from security.roles import ROLES


def validate_permission(role, tool):

    allowed_tools = ROLES.get(role, [])

    if tool not in allowed_tools:
        raise Exception(
            f"Role '{role}' cannot execute tool '{tool}'"
        )

    return True