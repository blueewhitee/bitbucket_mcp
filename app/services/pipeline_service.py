from typing import Dict, Any, Optional
from app.services.bitbucket_service import BitbucketService

class PipelineService:
    @staticmethod
    async def list_pipelines(
        repo_slug: str, 
        limit: int = 10, 
        page: int = 1
    ) -> Dict[str, Any]:
        """Fetch list of pipelines executed in a repository."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        async with client:
            response = await client.get(
                f"/repositories/{workspace}/{repo_slug}/pipelines",
                params={"pagelen": limit, "page": page, "sort": "-created_on"}
            )
            response.raise_for_status()
            data = response.json()
            
            pipelines = []
            for pipe in data.get("values", []):
                pipelines.append({
                    "uuid": pipe.get("uuid"),
                    "build_number": pipe.get("build_number"),
                    "creator": pipe.get("creator", {}).get("display_name", "Unknown"),
                    "repository": pipe.get("repository", {}).get("name"),
                    "state": pipe.get("state", {}).get("name"),
                    "result": pipe.get("state", {}).get("result", {}).get("name") if pipe.get("state", {}).get("type") == "pipeline_state_completed" else None,
                    "target_type": pipe.get("target", {}).get("ref_type"),
                    "target_name": pipe.get("target", {}).get("ref_name"),
                    "created_on": pipe.get("created_on"),
                    "completed_on": pipe.get("completed_on"),
                    "link": pipe.get("links", {}).get("steps", {}).get("href")
                })
            
            return {
                "page": data.get("page"),
                "pagelen": data.get("pagelen"),
                "next": data.get("next"),
                "pipelines": pipelines
            }

    @staticmethod
    async def trigger_pipeline(
        repo_slug: str, 
        branch_name: str = "main"
    ) -> Dict[str, Any]:
        """Manually trigger a pipeline for a specific branch."""
        client, _ = BitbucketService.get_client()
        workspace = BitbucketService.get_workspace()
        
        payload = {
            "target": {
                "ref_type": "branch",
                "type": "pipeline_ref_target",
                "ref_name": branch_name
            }
        }
        
        async with client:
            response = await client.post(
                f"/repositories/{workspace}/{repo_slug}/pipelines",
                json=payload
            )
            response.raise_for_status()
            pipe = response.json()
            
            return {
                "status": "success",
                "uuid": pipe.get("uuid"),
                "build_number": pipe.get("build_number"),
                "state": pipe.get("state", {}).get("name"),
                "link": pipe.get("links", {}).get("steps", {}).get("href")
            }
