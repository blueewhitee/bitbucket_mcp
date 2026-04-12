from typing import Dict, Any, Optional
from app.services.bitbucket_service import BitbucketService

class IssueService:
    @staticmethod
    async def list_issues(
        repo_slug: str, 
        state: Optional[str] = None, 
        limit: int = 10, 
        page: int = 1
    ) -> Dict[str, Any]:
        """Fetch list of issues for a repository."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        params = {"pagelen": limit, "page": page}
        # Bitbucket issues filters usually require a custom query language for 'state' or q.
        # Simple state query `q=state="resolved"` etc.
        if state:
            params["q"] = f'state="{state}"'
            
        async with client:
            response = await client.get(
                f"/repositories/{workspace}/{repo_slug}/issues",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            issues = []
            for issue in data.get("values", []):
                issues.append({
                    "id": issue.get("id"),
                    "title": issue.get("title"),
                    "state": issue.get("state"),
                    "kind": issue.get("kind"),
                    "reporter": issue.get("reporter", {}).get("display_name", "Unknown"),
                    "assignee": issue.get("assignee", {}).get("display_name") if issue.get("assignee") else None,
                    "created_on": issue.get("created_on"),
                    "link": issue.get("links", {}).get("html", {}).get("href")
                })
            
            return {
                "page": data.get("page"),
                "pagelen": data.get("pagelen"),
                "next": data.get("next"),
                "issues": issues
            }

    @staticmethod
    async def get_issue(repo_slug: str, issue_id: int) -> Dict[str, Any]:
        """Fetch details of a specific issue."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        async with client:
            response = await client.get(
                f"/repositories/{workspace}/{repo_slug}/issues/{issue_id}"
            )
            response.raise_for_status()
            issue = response.json()
            
            return {
                "id": issue.get("id"),
                "title": issue.get("title"),
                "description": issue.get("content", {}).get("raw", ""),
                "state": issue.get("state"),
                "kind": issue.get("kind"),
                "priority": issue.get("priority"),
                "reporter": issue.get("reporter", {}).get("display_name", "Unknown"),
                "assignee": issue.get("assignee", {}).get("display_name") if issue.get("assignee") else None,
                "created_on": issue.get("created_on"),
                "link": issue.get("links", {}).get("html", {}).get("href")
            }

    @staticmethod
    async def create_issue(
        repo_slug: str, 
        title: str, 
        description: str = "",
        kind: str = "task",
        priority: str = "major"
    ) -> Dict[str, Any]:
        """Create a new issue."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        payload = {
            "title": title,
            "content": {"raw": description},
            "kind": kind,
            "priority": priority
        }
        
        async with client:
            response = await client.post(
                f"/repositories/{workspace}/{repo_slug}/issues",
                json=payload
            )
            response.raise_for_status()
            issue = response.json()
            
            return {
                "status": "success",
                "id": issue.get("id"),
                "title": issue.get("title"),
                "link": issue.get("links", {}).get("html", {}).get("href")
            }

    @staticmethod
    async def update_issue(
        repo_slug: str, 
        issue_id: int, 
        state: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing issue."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        payload = {}
        if state: payload["state"] = state
        if title: payload["title"] = title
        if content: payload["content"] = {"raw": content}
            
        async with client:
            response = await client.put(
                f"/repositories/{workspace}/{repo_slug}/issues/{issue_id}",
                json=payload
            )
            response.raise_for_status()
            issue = response.json()
            
            return {
                "status": "success",
                "id": issue.get("id"),
                "state": issue.get("state"),
                "link": issue.get("links", {}).get("html", {}).get("href")
            }
