import hashlib
import json
from typing import Any
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

def generate_etag(content: Any) -> str:
    # Convert to JSON string
    json_str = json.dumps(content, sort_keys=True)
    etag = hashlib.md5(json_str.encode()).hexdigest()
    return f'"{etag}"'

def check_etag(request: Request, etag: str) -> bool:
    """Check if client's ETag matches current ETag"""
    client_etag = request.headers.get("if-none-match")
    return client_etag == etag

def create_etag_response(
        request: Request,
        content: Any,
        status_code: int = 200
) -> Response:
    """Create response with ETag header, return 304 if not modified"""
    encoded_content = jsonable_encoder(content)

    etag = generate_etag(encoded_content)

    # Check if client has matching ETag
    if check_etag(request, etag):
        return Response(status_code=304, headers={"ETag": etag})
    
    # Return full response with ETag
    response = JSONResponse(content=encoded_content, status_code=status_code)
    response.headers["ETag"] = etag
    return response