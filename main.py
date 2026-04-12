from fastmcp import FastMCP
from typing import Dict, Any, Optional
from app.services.bitbucket_service import BitbucketService
from app.services.repository_service import RepositoryService
from app.services.workspace_service import WorkspaceService
import httpx

# Initialize the MCP Server
mcp = FastMCP("Bitbucket Server")

@mcp.tool()
async def setup_bitbucket(workspace: str, api_token: str, username: Optional[str] = None) -> Dict[str, Any]:
    """
    Configure Bitbucket access using API tokens, test connection, and safely save to a local environment file.
    
    Args:
        workspace: Your Bitbucket workspace
        api_token: Bitbucket API token
        username: Keep empty if using a Workspace Token. Enter your email if using a User API Token (from Personal Settings).
    """
    try:
        result = await BitbucketService.configure_and_test(
            workspace=workspace,
            api_token=api_token,
            username=username
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ----------------------------------------------------------------------------
# WORKSPACE TOOLS
# ----------------------------------------------------------------------------

@mcp.tool()
async def get_current_user() -> Dict[str, Any]:
    """Fetch details of the currently authenticated Bitbucket user."""
    try:
        return await WorkspaceService.get_current_user()
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def list_workspaces(limit: int = 10, page: int = 1) -> Dict[str, Any]:
    """Fetch workspaces accessible by the authenticated user."""
    try:
        return await WorkspaceService.list_workspaces(limit=limit, page=page)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

# ----------------------------------------------------------------------------
# REPOSITORY TOOLS
# ----------------------------------------------------------------------------

@mcp.tool()
async def list_repositories(limit: int = 10, page: int = 1) -> Dict[str, Any]:
    """Fetch a list of repositories in the configured workspace."""
    try:
        return await RepositoryService.list_repositories(limit=limit, page=page)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_repository(repo_slug: str) -> Dict[str, Any]:
    """
    Fetch details for a specific repository.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository (e.g., 'my-repo').
    """
    try:
        return await RepositoryService.get_repository(repo_slug)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def create_repository(name: str, repo_slug: str, is_private: bool = True, description: str = "") -> Dict[str, Any]:
    """
    Create a new repository in the configured workspace.
    
    Args:
        name: Human-readable name of the repository.
        repo_slug: The URL-friendly identifier of the repository (e.g., 'my-repo').
        is_private: Whether the repository should be private.
        description: Optional description for the repository.
    """
    try:
        return await RepositoryService.create_repository(
            name=name, repo_slug=repo_slug, is_private=is_private, description=description
        )
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

# ----------------------------------------------------------------------------
# SOURCE & COMMITS TOOLS
# ----------------------------------------------------------------------------
from app.services.source_service import SourceService

@mcp.tool()
async def list_commits(repo_slug: str, branch_or_commit: Optional[str] = None, limit: int = 10, page: int = 1) -> Dict[str, Any]:
    """
    Fetch commit history for a repository or a specific branch/commit.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        branch_or_commit: (Optional) specific branch or commit hash to list history for.
        limit: Max number of records to return.
        page: Page number for pagination.
    """
    try:
        return await SourceService.list_commits(repo_slug, branch_or_commit, limit, page)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def list_branches(repo_slug: str, limit: int = 10, page: int = 1) -> Dict[str, Any]:
    """
    Fetch all branches in a repository.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
    """
    try:
        return await SourceService.list_branches(repo_slug, limit, page)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def create_branch(repo_slug: str, branch_name: str, target_hash_or_branch: str) -> Dict[str, Any]:
    """
    Create a new branch off an existing commit hash or branch.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        branch_name: The name of the new branch to create.
        target_hash_or_branch: The commit hash or existing branch name to branch off from.
    """
    try:
        return await SourceService.create_branch(repo_slug, branch_name, target_hash_or_branch)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def read_file_content(repo_slug: str, file_path: str, commit_or_branch: str = "main") -> Dict[str, Any]:
    """
    Fetch the contents of a specific file from the repository at a given commit or branch.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        file_path: The specific path to the file in the repo (e.g. 'src/main.py').
        commit_or_branch: Ex: 'main' or 'feature-branch' or commit hash.
    """
    try:
        return await SourceService.read_file_content(repo_slug, file_path, commit_or_branch)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}



# ----------------------------------------------------------------------------
# PULL REQUEST TOOLS
# ----------------------------------------------------------------------------
from app.services.pull_request_service import PullRequestService

@mcp.tool()
async def list_pull_requests(repo_slug: str, state: str = "OPEN", limit: int = 10, page: int = 1) -> Dict[str, Any]:
    """
    Fetch list of pull requests for a repository.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        state: State of PRs to return (e.g., 'OPEN', 'MERGED', 'DECLINED', 'SUPERSEDED'). Default is 'OPEN'.
    """
    try:
        return await PullRequestService.list_pull_requests(repo_slug, state, limit, page)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_pull_request(repo_slug: str, pr_id: int) -> Dict[str, Any]:
    """
    Fetch details of a specific pull request.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        pr_id: The ID of the pull request.
    """
    try:
        return await PullRequestService.get_pull_request(repo_slug, pr_id)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def create_pull_request(repo_slug: str, title: str, source_branch: str, destination_branch: str = "main", description: str = "") -> Dict[str, Any]:
    """
    Create a new pull request.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        title: Title of the pull request.
        source_branch: branch containing your changes.
        destination_branch: Target branch to merge into. Defaults to 'main'.
        description: Details about the changes.
    """
    try:
        return await PullRequestService.create_pull_request(repo_slug, title, source_branch, destination_branch, description)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def merge_pull_request(repo_slug: str, pr_id: int, message: str = "") -> Dict[str, Any]:
    """
    Merge an open pull request.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        pr_id: The ID of the pull request.
        message: Optional commit message for the merge.
    """
    try:
        return await PullRequestService.merge_pull_request(repo_slug, pr_id, message)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def add_pr_comment(repo_slug: str, pr_id: int, comment: str) -> Dict[str, Any]:
    """
    Add a comment to an existing pull request.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        pr_id: The ID of the pull request.
        comment: The text content of the comment.
    """
    try:
        return await PullRequestService.add_pr_comment(repo_slug, pr_id, comment)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

# ----------------------------------------------------------------------------
# ISSUE TOOLS
# ----------------------------------------------------------------------------
from app.services.issue_service import IssueService

@mcp.tool()
async def list_issues(repo_slug: str, state: Optional[str] = None, limit: int = 10, page: int = 1) -> Dict[str, Any]:
    """
    Fetch list of issues for a repository.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        state: Optional state filter (e.g., 'new', 'open', 'resolved', 'on hold', 'invalid', 'duplicate', 'wontfix').
    """
    try:
        return await IssueService.list_issues(repo_slug, state, limit, page)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_issue(repo_slug: str, issue_id: int) -> Dict[str, Any]:
    """
    Fetch details of a specific issue.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        issue_id: The ID of the issue.
    """
    try:
        return await IssueService.get_issue(repo_slug, issue_id)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def create_issue(repo_slug: str, title: str, description: str = "", kind: str = "task", priority: str = "major") -> Dict[str, Any]:
    """
    Create a new issue.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        title: Title of the issue.
        description: Description of the issue.
        kind: Kind of issue (e.g., 'bug', 'enhancement', 'proposal', 'task'). Default is 'task'.
        priority: Priority of issue (e.g., 'trivial', 'minor', 'major', 'critical', 'blocker'). Default is 'major'.
    """
    try:
        return await IssueService.create_issue(repo_slug, title, description, kind, priority)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def update_issue(repo_slug: str, issue_id: int, state: Optional[str] = None, title: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
    """
    Update an existing issue.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        issue_id: The ID of the issue.
        state: Optional new state (e.g., 'resolved').
        title: Optional new title.
        content: Optional new description content.
    """
    try:
        return await IssueService.update_issue(repo_slug, issue_id, state, title, content)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

# ----------------------------------------------------------------------------
# PIPELINE (CI/CD) TOOLS
# ----------------------------------------------------------------------------
from app.services.pipeline_service import PipelineService

@mcp.tool()
async def list_pipelines(repo_slug: str, limit: int = 10, page: int = 1) -> Dict[str, Any]:
    """
    Fetch list of pipelines executed in a repository.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
    """
    try:
        return await PipelineService.list_pipelines(repo_slug, limit, page)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def trigger_pipeline(repo_slug: str, branch_name: str = "main") -> Dict[str, Any]:
    """
    Manually trigger a pipeline execution for a specific branch.
    
    Args:
        repo_slug: The URL-friendly identifier of the repository.
        branch_name: The branch name you want to trigger the pipeline on. Defaults to 'main'.
    """
    try:
        return await PipelineService.trigger_pipeline(repo_slug, branch_name)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Starting Bitbucket FastMCP Server...")
    mcp.run()
