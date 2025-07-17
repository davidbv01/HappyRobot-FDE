from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_api_keys() -> Dict[str, str]:
    """
    Load API keys from environment variables
    
    Returns:
        Dict[str, str]: Dictionary of API keys and their associated names
    """
    # Load from API_KEYS environment variable (format: key1:name1,key2:name2,...)
    api_keys_env = os.getenv("API_KEYS", "")
    
    if api_keys_env:
        api_keys = {}
        for key_pair in api_keys_env.split(","):
            if ":" in key_pair:
                key, name = key_pair.split(":", 1)
                api_keys[key.strip()] = name.strip()
            else:
                # If no name provided, use the key as the name
                api_keys[key_pair.strip()] = key_pair.strip()
        return api_keys
    else:
        # Fallback to individual environment variables or defaults
        return {
            os.getenv("ADMIN_API_KEY", "hr-api-key-2025"): "HappyRobot Admin",
            os.getenv("CARRIER_API_KEY", "carrier-api-key"): "Carrier Access", 
            os.getenv("DEMO_API_KEY", "demo-key-123"): "Demo User"
        }

# Load API keys from environment
VALID_API_KEYS = load_api_keys()

security = HTTPBearer()

async def get_api_key_from_header(x_api_key: Optional[str] = None) -> str:
    """
    Extract API key from x-api-key header
    
    Args:
        x_api_key: API key from header
        
    Returns:
        str: Validated API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing x-api-key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return x_api_key

async def validate_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Alternative method using Bearer token authentication
    
    Args:
        credentials: Bearer token credentials
        
    Returns:
        str: Validated API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if credentials.credentials not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return credentials.credentials

def get_user_info(api_key: str) -> dict:
    """
    Get user information associated with the API key
    
    Args:
        api_key: Validated API key
        
    Returns:
        dict: User information
    """
    return {
        "api_key": api_key,
        "user_name": VALID_API_KEYS.get(api_key, "Unknown"),
        "access_level": "standard"
    }

# Dependency for header-based API key authentication
from fastapi import Header

async def verify_api_key_header(authorization: str = Header(..., description="Authorization header with ApiKey format")) -> dict:
    """
    Dependency to verify API key from Authorization header (format: ApiKey <key>)
    
    Args:
        authorization: Authorization header with format "ApiKey <api_key>"
        
    Returns:
        dict: User information
    """
    # Extract API key from "ApiKey <key>" format
    if not authorization.startswith("ApiKey "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: 'ApiKey <your_api_key>'",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    api_key = authorization.replace("ApiKey ", "", 1)
    validated_key = await get_api_key_from_header(api_key)
    return get_user_info(validated_key)

# Dependency for Bearer token authentication
async def verify_api_key_bearer(api_key: str = Depends(validate_api_key)) -> dict:
    """
    Dependency to verify API key from Bearer token
    
    Args:
        api_key: Validated API key from Bearer token
        
    Returns:
        dict: User information
    """
    return get_user_info(api_key) 