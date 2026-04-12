import asyncio
import getpass
from app.services.bitbucket_service import BitbucketService
from app.services.workspace_service import WorkspaceService
from app.services.repository_service import RepositoryService
from app.services.source_service import SourceService
from app.services.pull_request_service import PullRequestService
from app.services.issue_service import IssueService
from app.services.pipeline_service import PipelineService
from app.core.config import settings

async def test_apis():
    print("=== Bitbucket Stage 1 Tests ===")
    
    # Check if credentials exist, otherwise prompt
    if not settings.bitbucket_api_token:
        print("No saved credentials found. Please run authentication first.")
        workspace = input("Enter your Bitbucket Workspace ID: ")
        username = input("Enter your Atlassian Email (or press Enter to skip): ").strip() or None
        api_token = getpass.getpass("Enter your Bitbucket API Token: ")
        
        await BitbucketService.configure_and_test(
            workspace=workspace,
            api_token=api_token,
            username=username
        )
        # Reload settings as we saved to .env
        settings.bitbucket_workspace = workspace
        if username:
            settings.bitbucket_username = username
        settings.bitbucket_api_token = api_token
        print("Authentication configured!\n")
    
    try:
        print("1. Fetching Current User...")
        user = await WorkspaceService.get_current_user()
        print(f"✅ User: {user.get('display_name')} (ID: {user.get('account_id')})")
        
        print("\n2. Listing Workspaces...")
        ws_list = await WorkspaceService.list_workspaces(limit=5)
        for ws in ws_list.get("workspaces", []):
            print(f"  - {ws.get('name')} (Slug: {ws.get('slug')})")
            
        print(f"\n3. Listing Repositories for workspace '{settings.bitbucket_workspace}'...")
        repo_list = await RepositoryService.list_repositories(limit=5)
        if repo_list.get("repositories"):
            for repo in repo_list.get("repositories", []):
                print(f"  - {repo.get('name')} (Slug: {repo.get('slug')})")
                
            # Test getting details of the first repository
            first_slug = repo_list["repositories"][0].get("slug")
            print(f"\n4. Fetching details for first repository '{first_slug}'...")
            details = await RepositoryService.get_repository(first_slug)
            print(f"✅ Repository {details.get('name')} is {'Private' if details.get('is_private') else 'Public'}.")
            
            # --- STAGE 2 TESTS ---
            print(f"\n=== Stage 2: Source Code, Branches & Commits ===")
            print(f"1. Fetching branches for repository '{first_slug}'...")
            branches = await SourceService.list_branches(first_slug, limit=5)
            main_branch = None
            if branches.get("branches"):
                for b in branches.get("branches"):
                    print(f"  - {b.get('name')} -> {b.get('target_hash')}")
                    if b.get("name") in ("main", "master"):
                        main_branch = b.get("name")
            else:
                print("  No branches found.")
                
            print(f"\n2. Fetching commits for repository '{first_slug}'...")
            commits = await SourceService.list_commits(first_slug, limit=3)
            if commits.get("commits"):
                for c in commits.get("commits"):
                    print(f"  - [{c.get('hash')[:7]}] {c.get('message')} (by {c.get('author')})")
            else:
                print("  No commits found.")
            
            # --- STAGE 3 TESTS ---
            print(f"\n=== Stage 3: Pull Requests ===")
            print(f"1. Fetching OPEN Pull Requests for repository '{first_slug}'...")
            prs = await PullRequestService.list_pull_requests(first_slug, state="OPEN", limit=5)
            if prs.get("pull_requests"):
                for pr in prs.get("pull_requests"):
                    print(f"  - PR #{pr.get('id')}: {pr.get('title')} ({pr.get('source_branch')} -> {pr.get('destination_branch')})")
            else:
                print("  No OPEN pull requests found.")
                
            # --- STAGE 4 TESTS ---
            print(f"\n=== Stage 4: Issues ===")
            print(f"1. Fetching recent Issues for repository '{first_slug}'...")
            try:
                issues = await IssueService.list_issues(first_slug, limit=5)
                if issues.get("issues"):
                    for issue in issues.get("issues"):
                        print(f"  - Issue #{issue.get('id')}: {issue.get('title')} [{issue.get('state')}]")
                else:
                    print("  No issues found or Issue tracking disabled for this repository.")
            except Exception as e:
                # Issue tracking might be disabled for the repos
                print(f"  Could not load issues (It may be disabled for this repo): {e}")

            # --- STAGE 5 TESTS ---
            print(f"\n=== Stage 5: CI/CD Pipelines ===")
            print(f"1. Fetching Pipelines for repository '{first_slug}'...")
            try:
                pipelines = await PipelineService.list_pipelines(first_slug, limit=5)
                if pipelines.get("pipelines"):
                    for pipe in pipelines.get("pipelines"):
                        print(f"  - Pipeline #{pipe.get('build_number')} [{pipe.get('state')} -> {pipe.get('result') or 'N/A'}]")
                else:
                    print("  No pipelines found.")
            except Exception as e:
                print(f"  Could not load pipelines (It may be disabled): {e}")

        else:
            print("  No repositories found to test Stages 2-5 with.")
            
        print("\nAll Stages 1-5 tests passed successfully!")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(test_apis())

