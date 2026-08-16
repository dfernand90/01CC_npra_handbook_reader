import os
from fastapi import Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def setup_auth_middleware(app):
    api_key = os.getenv("API_KEY", "contextual0192837465")
    
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        # Skip auth for health endpoint
        if request.url.path == "/health":
            return await call_next(request)
            
        # Get Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid Authorization header. Expected 'Bearer <key>'"}
            )
            
        token = auth_header.split(" ")[1]
        
        # We check against API_KEY. For MVP, one API key is fine.
        if token != api_key:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid API key"}
            )
            
        response = await call_next(request)
        return response
