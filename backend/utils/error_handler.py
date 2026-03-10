from fastapi.responses import JSONResponse
from fastapi import Request


async def global_exception_handler(request: Request, exc: Exception):

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": str(exc)
        }
    )