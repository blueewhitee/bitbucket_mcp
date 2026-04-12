import httpx
from typing import Dict, Any, Optional, Tuple
from app.core.config import settings, update_env_file

class BitbucketService:
    @staticmethod
    def get_client() -> Tuple[httpx.AsyncClient, str]:
        """Returns an authenticated AsyncClient and the base URL based on saved settings."""
        token = settings.bitbucket_api_token.get_secret_value()
        username = settings.bitbucket_username
        
        headers = {"Accept": "application/json"}
        auth = None

        if username:
            auth = (username, token)
        elif token:
            headers["Authorization"] = f"Bearer {token}"
        else:
            raise ValueError("Bitbucket credentials are not configured. Run setup_bitbucket first.")
            
        client = httpx.AsyncClient(
            base_url=settings.bitbucket_api_base_url,
            headers=headers,
            auth=auth,
            timeout=30.0
        )
        return client, settings.bitbucket_api_base_url

    @staticmethod
    def get_workspace() -> str:
        """Returns the configured workspace."""
        if not settings.bitbucket_workspace:
            raise ValueError("Bitbucket workspace is not configured. Run setup_bitbucket first.")
        return settings.bitbucket_workspace

    @staticmethod
    async def configure_and_test(
        workspace: str, 
        api_token: str,
        username: Optional[str] = None,
        api_base_url: str = "https://api.bitbucket.org/2.0"
    ) -> Dict[str, Any]:
        """Configure Bitbucket access using API Tokens and test the connection."""
        
        url = f"{api_base_url}/workspaces/{workspace}"
        headers = {"Accept": "application/json"}
        auth = None

        if username:
            # User API Tokens (generated under Personal Settings) require Basic Auth
            auth = (username, api_token)
        else:
            # Workspace/Project/Repo Access Tokens require Bearer Auth
            headers["Authorization"] = f"Bearer {api_token}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, auth=auth)
            
            if response.status_code != 200:
                raise Exception(f"Connection failed: {response.status_code} - {response.text}")
                
        # If connection successful, save to .env to persist for other tools
        env_updates = {
            "BITBUCKET_WORKSPACE": workspace,
            "BITBUCKET_API_TOKEN": api_token
        }
        if username:
            env_updates["BITBUCKET_USERNAME"] = username
            
        update_env_file(env_updates)
        
        return {
            "status": "success",
            "message": "Bitbucket configured and API Token saved securely to .env",
            "workspace": workspace,
            "auth_mode": "Basic (User Token)" if username else "Bearer (Workspace Token)"
        }
