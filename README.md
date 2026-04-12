# Bitbucket FastMCP Server

A FastMCP-based Python server that exposes Bitbucket Cloud Rest API capabilities directly to AI agents (like Claude Desktop). This allows the AI to manage repositories, read code, handle pull requests, track issues, and trigger CI/CD pipelines natively.

## Prerequisites
1. **Python 3.12+** and **uv** package manager installed.
2. A **Bitbucket API Token**:
   - For Personal Account: Create via `Personal Settings -> API Tokens` (requires Atlassian Email).
   - For Workspace: Create via `Workspace Settings -> Access Tokens` (no email required).
   
Make sure your token has the necessary read/write scopes for the repositories, PRs, issues, and pipelines.

## 1. Local Setup & Authentication

Before running the server, let's configure your authentication and verify the connection:

```bash
# Clone the repository and navigate into it
cd e:\accenture_project

# Run the interactive authentication and feature test script
uv run python test_logic.py
```
This script will:
1. Prompt you for your Workspace ID, Email (if using Personal API Token), and Token.
2. Formulate the correct authentication mode (Basic or Bearer).
3. Validate connection and test the API stages (Commits, Branches, PRs, etc.).
4. Securely save your credentials directly into a local `.env` file for the MCP server to use.

## 2. Using with Claude Desktop

To connect these tools to Claude Desktop, you just need to edit Claude's configuration file.

1. Open `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac).
2. Insert the following configuration:

```json
{
  "mcpServers": {
    "bitbucket-server": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "main.py"
      ],
      "cwd": "e:\\accenture_project"
    }
  }
}
```
*(Note: adjust `cwd` if the project directory is moved)*

3. Save the file and **restart Claude Desktop**.
4. Look for the "plug" icon in Claude Desktop's chat bar to see your new Bitbucket tools loaded!

---

## Available MCP Tools

Once connected, your AI gains access to the following 5 domains:

* **Repositories & Workspaces:** `list_workspaces`, `get_current_user`, `list_repositories`, `get_repository`, `create_repository`
* **Source & Branches:** `list_commits`, `list_branches`, `create_branch`, `read_file_content`
* **Pull Requests:** `list_pull_requests`, `get_pull_request`, `create_pull_request`, `merge_pull_request`, `add_pr_comment`
* **Issue Tracking:** `list_issues`, `get_issue`, `create_issue`, `update_issue`
* **Pipelines (CI/CD):** `list_pipelines`, `trigger_pipeline`
