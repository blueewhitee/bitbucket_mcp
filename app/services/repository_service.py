from typing import Dict, Any, List
from app.services.bitbucket_service import BitbucketService

class RepositoryService:
    @staticmethod
    async def list_repositories(limit: int = 10, page: int = 1) -> Dict[str, Any]:
        """Fetch all repositories in the configured workspace."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        # Bitbucket uses pagelen (max is usually 100) and page
        async with client:
            response = await client.get(
                f"/repositories/{workspace}",
                params={"pagelen": limit, "page": page}
            )
            response.raise_for_status()
            data = response.json()
            
            # Simplify the response for the LLM
            repos = []
            for repo in data.get("values", []):
                repos.append({
                    "name": repo.get("name"),
                    "slug": repo.get("slug"),
                    "description": repo.get("description"),
                    "is_private": repo.get("is_private"),
                    "language": repo.get("language"),
                    "uuid": repo.get("uuid"),
                    "mainbranch": repo.get("mainbranch", {}).get("name")
                })
            
            return {
                "page": data.get("page"),
                "pagelen": data.get("pagelen"),
                "size": data.get("size"),
                "next": data.get("next"),
                "repositories": repos
            }

    @staticmethod
    async def get_repository(repo_slug: str) -> Dict[str, Any]:
        """Fetch details for a specific repository."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        async with client:
            response = await client.get(f"/repositories/{workspace}/{repo_slug}")
            response.raise_for_status()
            repo = response.json()
            
            return {
                "name": repo.get("name"),
                "slug": repo.get("slug"),
                "description": repo.get("description"),
                "is_private": repo.get("is_private"),
                "language": repo.get("language"),
                "uuid": repo.get("uuid"),
                "mainbranch": repo.get("mainbranch", {}).get("name"),
                "created_on": repo.get("created_on"),
                "updated_on": repo.get("updated_on"),
                "links": repo.get("links", {})
            }

    @staticmethod
    async def create_repository(
        name: str, 
        repo_slug: str, 
        is_private: bool = True, 
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a new repository."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        payload = {
            "name": name,
            "is_private": is_private,
            "description": description
        }
        
        async with client:
            response = await client.post(
                f"/repositories/{workspace}/{repo_slug}",
                json=payload
            )
            response.raise_for_status()
            repo = response.json()
            
            return {
                "status": "success",
                "name": repo.get("name"),
                "slug": repo.get("slug"),
                "uuid": repo.get("uuid")
            }

    @staticmethod
    async def clone_repository(repo_slug: str, destination_path: str = "./") -> Dict[str, Any]:
        """Clones a repository locally."""
        from app.core.config import settings
        import asyncio
        import os
        import base64
        
        workspace = BitbucketService.get_workspace()
        token = settings.bitbucket_api_token.get_secret_value()
        username = settings.bitbucket_username
        
        # Generate base64 auth for header to avoid credentials in URL & .git/config
        if username:
            auth_str = f"{username}:{token}"
        else:
            auth_str = f"x-token-auth:{token}"
        b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
            
        clone_url = f"https://bitbucket.org/{workspace}/{repo_slug}.git"
        
        # Determine actual destination path and expand ~ if used
        expanded_dest = os.path.expanduser(destination_path)
        target_dir = os.path.join(expanded_dest, repo_slug)
        
        # Inject auth securely via git config param instead of URL.
        # --depth 1 is a shallow clone: fetches only the latest commit snapshot,
        # not the full history. This is much faster and ideal for code reading/analysis.
        process = await asyncio.create_subprocess_exec(
            "git", "-c", f"http.extraHeader=Authorization: Basic {b64_auth}",
            "clone", "--depth", "1", clone_url, target_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return {
                "status": "error",
                "message": f"Git clone failed: {stderr.decode('utf-8')}"
            }
            
        return {
            "status": "success",
            "message": f"Successfully cloned repository into {target_dir}",
            "destination": target_dir
        }
