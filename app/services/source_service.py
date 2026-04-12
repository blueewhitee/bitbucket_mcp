import urllib.parse
from typing import Dict, Any, List, Optional
from app.services.bitbucket_service import BitbucketService
import httpx

class SourceService:
    @staticmethod
    async def list_commits(repo_slug: str, branch_or_commit: Optional[str] = None, limit: int = 10, page: int = 1) -> Dict[str, Any]:
        """Fetch commit history for a repository or a specific branch/commit."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        endpoint = f"/repositories/{workspace}/{repo_slug}/commits"
        if branch_or_commit:
            # Need to URL encode the branch name as it might contain slashes
            encoded_ref = urllib.parse.quote(branch_or_commit, safe='')
            endpoint = f"{endpoint}/{encoded_ref}"
            
        async with client:
            response = await client.get(endpoint, params={"pagelen": limit, "page": page})
            response.raise_for_status()
            data = response.json()
            
            commits = []
            for commit in data.get("values", []):
                commits.append({
                    "hash": commit.get("hash"),
                    "message": commit.get("message", "").strip(),
                    "date": commit.get("date"),
                    "author": commit.get("author", {}).get("user", {}).get("display_name", "Unknown")
                })
            
            return {
                "page": data.get("page"),
                "pagelen": data.get("pagelen"),
                "next": data.get("next"),
                "commits": commits
            }

    @staticmethod
    async def list_branches(repo_slug: str, limit: int = 10, page: int = 1) -> Dict[str, Any]:
        """Fetch all branches in a repository."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        async with client:
            response = await client.get(
                f"/repositories/{workspace}/{repo_slug}/refs/branches",
                params={"pagelen": limit, "page": page}
            )
            response.raise_for_status()
            data = response.json()
            
            branches = []
            for branch in data.get("values", []):
                branches.append({
                    "name": branch.get("name"),
                    "target_hash": branch.get("target", {}).get("hash"),
                    "target_date": branch.get("target", {}).get("date")
                })
            
            return {
                "page": data.get("page"),
                "pagelen": data.get("pagelen"),
                "next": data.get("next"),
                "branches": branches
            }

    @staticmethod
    async def create_branch(repo_slug: str, branch_name: str, target_hash_or_branch: str) -> Dict[str, Any]:
        """Create a new branch off an existing commit hash or branch."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        payload = {
            "name": branch_name,
            "target": {
                "hash": target_hash_or_branch
            }
        }
        
        async with client:
            response = await client.post(
                f"/repositories/{workspace}/{repo_slug}/refs/branches",
                json=payload
            )
            response.raise_for_status()
            branch = response.json()
            
            return {
                "status": "success",
                "name": branch.get("name"),
                "target_hash": branch.get("target", {}).get("hash")
            }

    @staticmethod
    async def read_file_content(repo_slug: str, file_path: str, commit_or_branch: str = "main") -> Dict[str, Any]:
        """Fetch the contents of a specific file from the repository at a given commit/branch."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        encoded_ref = urllib.parse.quote(commit_or_branch, safe='')
        # file_path might have multiple slashes, they should usually be sent as normal slashes in the path
        # but the request path is /src/{commit}/{path}
        
        async with client:
            response = await client.get(
                f"/repositories/{workspace}/{repo_slug}/src/{encoded_ref}/{file_path}"
            )
            
            if response.status_code == 404:
                return {"error": f"File '{file_path}' not found at '{commit_or_branch}'."}
                
            response.raise_for_status()
            
            return {
                "file_path": file_path,
                "commit_or_branch": commit_or_branch,
                "content": response.text
            }
