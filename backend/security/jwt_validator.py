import requests
from jose import jwt
from fastapi import HTTPException
from config import config

AUTH0_DOMAIN = config.AUTH0_DOMAIN
API_AUDIENCE = config.AUTH0_AUDIENCE
ALGORITHMS = ["RS256"]


def get_jwks():

    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"

    response = requests.get(jwks_url)

    return response.json()


def verify_jwt(token):

    jwks = get_jwks()

    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token header")

    rsa_key = {}

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    if rsa_key == {}:
        raise HTTPException(status_code=401, detail="Unable to find appropriate key")

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Token validation failed")

    return payload