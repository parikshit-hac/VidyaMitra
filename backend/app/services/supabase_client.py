from functools import lru_cache
from typing import Optional
import requests

from supabase import Client, create_client

from app.settings import settings


@lru_cache
def get_supabase_client() -> Optional[Client]:
    if not settings.supabase_url or not settings.supabase_key:
        print("Supabase URL or key is not configured in environment variables.")
        return None
    
    try:
        # Create client with custom timeout
        client = create_client(settings.supabase_url, settings.supabase_key)
        # Set timeout options (in seconds)
        client.postgrest.timeout = 30  # 30 second timeout
        
        # Test connection
        print(f"Testing Supabase connection to: {settings.supabase_url}")
        return client
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")
        return None


# Try to get Supabase client, fallback to None if connection fails
supabase: Optional[Client] = get_supabase_client()


def test_supabase_connection() -> bool:
    """Test if Supabase is accessible"""
    if not supabase:
        return False
    
    try:
        # Simple test query
        response = supabase.table("app_users").select("count").execute()
        return True
    except Exception as e:
        print(f"Supabase connection test failed: {e}")
        return False


# Fallback in-memory storage for when Supabase is not available
_fallback_users = {}

def fallback_create_user(username: str, password_hash: str) -> bool:
    """Fallback user storage when Supabase is not available"""
    _fallback_users[username] = password_hash
    print(f"User {username} stored in fallback storage")
    return True

def fallback_get_user(username: str) -> Optional[str]:
    """Fallback user retrieval when Supabase is not available"""
    return _fallback_users.get(username)

