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