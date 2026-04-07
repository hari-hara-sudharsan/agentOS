import requests
from jose import jwt
from fastapi import HTTPException
from config import config
import time
import logging

logger = logging.getLogger(__name__)

AUTH0_DOMAIN = config.AUTH0_DOMAIN
API_AUDIENCE = config.AUTH0_AUDIENCE
ALGORITHMS = ["RS256"]

# JWKS cache to avoid fetching on every request
_jwks_cache = {
    "keys": None,
    "fetched_at": 0,
    "ttl": 3600  # Cache for 1 hour
}


def get_jwks():
    """Fetch JWKS with caching and error handling."""
    global _jwks_cache
    
    current_time = time.time()
    
    # Return cached keys if still valid
    if _jwks_cache["keys"] and (current_time - _jwks_cache["fetched_at"]) < _jwks_cache["ttl"]:
        return _jwks_cache["keys"]
    
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    
    try:
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        jwks = response.json()
        
        # Update cache
        _jwks_cache["keys"] = jwks
        _jwks_cache["fetched_at"] = current_time
        
        return jwks
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching JWKS: {e}")
        # Return cached keys if available, even if expired
        if _jwks_cache["keys"]:
            logger.warning("Using expired JWKS cache due to connection error")
            return _jwks_cache["keys"]
        raise HTTPException(
            status_code=503, 
            detail="Unable to verify authentication - Auth0 connection failed. Please try again."
        )
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout fetching JWKS: {e}")
        if _jwks_cache["keys"]:
            logger.warning("Using expired JWKS cache due to timeout")
            return _jwks_cache["keys"]
        raise HTTPException(
            status_code=503, 
            detail="Authentication service timeout. Please try again."
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching JWKS: {e}")
        if _jwks_cache["keys"]:
            logger.warning("Using expired JWKS cache due to request error")
            return _jwks_cache["keys"]
        raise HTTPException(
            status_code=503, 
            detail="Authentication service unavailable. Please try again."
        )


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