from typing import Dict, Any, List
from app.services.bitbucket_service import BitbucketService

class WorkspaceService:
    @staticmethod
    async def get_current_user() -> Dict[str, Any]:
        """Fetch details of the currently authenticated user."""
        client, _ = BitbucketService.get_client()
        
        async with client:
            response = await client.get("/user")
            response.raise_for_status()
            user = response.json()
            
            return {
                "account_id": user.get("account_id"),
                "display_name": user.get("display_name"),
                "nickname": user.get("nickname"),
                "is_staff": user.get("is_staff"),
                "uuid": user.get("uuid")
            }

    @staticmethod
    async def list_workspaces(limit: int = 10, page: int = 1) -> Dict[str, Any]:
        """Fetch workspaces accessible by the authenticated user."""
        client, _ = BitbucketService.get_client()
        
        async with client:
            response = await client.get("/workspaces", params={"pagelen": limit, "page": page})
            response.raise_for_status()
            data = response.json()
            
            workspaces = []
            for ws in data.get("values", []):
                workspaces.append({
                    "name": ws.get("name"),
                    "slug": ws.get("slug"),
                    "uuid": ws.get("uuid"),
                    "is_private": ws.get("is_private")
                })
            
            return {
                "page": data.get("page"),
                "pagelen": data.get("pagelen"),
                "size": data.get("size"),
                "next": data.get("next"),
                "workspaces": workspaces
            }
