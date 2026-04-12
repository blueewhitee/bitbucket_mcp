from typing import Dict, Any, Optional
from app.services.bitbucket_service import BitbucketService

class PullRequestService:
    @staticmethod
    async def list_pull_requests(
        repo_slug: str, 
        state: str = "OPEN", 
        limit: int = 10, 
        page: int = 1
    ) -> Dict[str, Any]:
        """Fetch list of pull requests for a repository."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        async with client:
            response = await client.get(
                f"/repositories/{workspace}/{repo_slug}/pullrequests",
                params={"state": state, "pagelen": limit, "page": page}
            )
            response.raise_for_status()
            data = response.json()
            
            prs = []
            for pr in data.get("values", []):
                prs.append({
                    "id": pr.get("id"),
                    "title": pr.get("title"),
                    "state": pr.get("state"),
                    "source_branch": pr.get("source", {}).get("branch", {}).get("name"),
                    "destination_branch": pr.get("destination", {}).get("branch", {}).get("name"),
                    "author": pr.get("author", {}).get("display_name", "Unknown"),
                    "created_on": pr.get("created_on"),
                    "link": pr.get("links", {}).get("html", {}).get("href")
                })
            
            return {
                "page": data.get("page"),
                "pagelen": data.get("pagelen"),
                "next": data.get("next"),
                "pull_requests": prs
            }

    @staticmethod
    async def get_pull_request(repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """Fetch details of a specific pull request."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        async with client:
            response = await client.get(
                f"/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}"
            )
            response.raise_for_status()
            pr = response.json()
            
            return {
                "id": pr.get("id"),
                "title": pr.get("title"),
                "description": pr.get("description"),
                "state": pr.get("state"),
                "source_branch": pr.get("source", {}).get("branch", {}).get("name"),
                "destination_branch": pr.get("destination", {}).get("branch", {}).get("name"),
                "author": pr.get("author", {}).get("display_name", "Unknown"),
                "created_on": pr.get("created_on"),
                "updated_on": pr.get("updated_on"),
                "link": pr.get("links", {}).get("html", {}).get("href")
            }

    @staticmethod
    async def create_pull_request(
        repo_slug: str, 
        title: str, 
        source_branch: str, 
        destination_branch: str = "main",
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a new pull request."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        payload = {
            "title": title,
            "description": description,
            "source": {
                "branch": {"name": source_branch}
            },
            "destination": {
                "branch": {"name": destination_branch}
            }
        }
        
        async with client:
            response = await client.post(
                f"/repositories/{workspace}/{repo_slug}/pullrequests",
                json=payload
            )
            response.raise_for_status()
            pr = response.json()
            
            return {
                "status": "success",
                "id": pr.get("id"),
                "title": pr.get("title"),
                "link": pr.get("links", {}).get("html", {}).get("href")
            }

    @staticmethod
    async def merge_pull_request(repo_slug: str, pr_id: int, message: str = "") -> Dict[str, Any]:
        """Merge an open pull request."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        payload = {}
        if message:
            payload["message"] = message
            
        async with client:
            response = await client.post(
                f"/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/merge",
                json=payload
            )
            response.raise_for_status()
            pr = response.json()
            
            return {
                "status": "success",
                "state": pr.get("state"),
                "merged_by": pr.get("closed_by", {}).get("display_name", "Unknown")
            }

    @staticmethod
    async def add_pr_comment(repo_slug: str, pr_id: int, comment: str) -> Dict[str, Any]:
        """Add a comment to an existing pull request."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        payload = {
            "content": {"raw": comment}
        }
        
        async with client:
            response = await client.post(
                f"/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "status": "success",
                "comment_id": data.get("id"),
                "link": data.get("links", {}).get("html", {}).get("href")
            }
