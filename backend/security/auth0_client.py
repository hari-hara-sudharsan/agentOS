from fastapi import Request, HTTPException
from security.jwt_validator import verify_jwt


async def get_current_user(request: Request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    parts = auth_header.split()

    if parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = parts[1]

    payload = verify_jwt(token)

    return payload


def get_user_role(payload):

    roles = payload.get("roles", [])

    if not roles:
        return "basic_user"

    return roles[0]


class ConsentRequiredException(Exception):
    pass

def check_mfa_and_consent(user_context, params):
    """
    Job 4: Async Step-up Auth (Human-in-the-loop).
    Checks if the user has provided explicit step-up consent for high-stakes actions.
    """
    if not params.get("consent_granted"):
        raise ConsentRequiredException("step_up_required")