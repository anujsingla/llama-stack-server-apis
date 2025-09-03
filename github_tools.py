import json
import requests
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from llama_stack_client.lib.agents.client_tool import client_tool
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "GitHub-Project-Analyst-Agent"
}

if GITHUB_TOKEN:
    headers["Authorization"] = f"token {GITHUB_TOKEN}"


def _make_github_request(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """Make a request to GitHub API"""
    try:
        url = f"https://api.github.com/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}


@client_tool
def get_repository_info(owner: str, repo: str) -> str:
    """
    Get basic information about a GitHub repository
    
    :param owner: Repository owner (username or organization)
    :param repo: Repository name
    :return: JSON string with repository information
    """
    print("************************************************")
    print("tool called: get_repository_info")
    print(f"Getting repository info for {owner}/{repo}")
    print("************************************************")
    data = _make_github_request(f"repos/{owner}/{repo}")
    
    if "error" in data:
        return json.dumps(data)
    
    # Extract key information
    repo_info = {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "size": data.get("size"),
        "default_branch": data.get("default_branch"),
        "topics": data.get("topics", []),
        "license": data.get("license", {}).get("name") if data.get("license") else None,
        "homepage": data.get("homepage"),
        "clone_url": data.get("clone_url"),
        "ssh_url": data.get("ssh_url")
    }
    
    return json.dumps(repo_info, indent=2)


@client_tool
def get_repository_languages(owner: str, repo: str) -> str:
    """
    Get programming languages used in a repository
    
    :param owner: Repository owner
    :param repo: Repository name
    :return: JSON string with language statistics
    """
    print("************************************************")
    print("tool called: get_repository_languages")
    print(f"Getting languages for {owner}/{repo}")
    print("************************************************")
    data = _make_github_request(f"repos/{owner}/{repo}/languages")
    
    if "error" in data:
        return json.dumps(data)
    
    # Calculate percentages
    total_bytes = sum(data.values())
    languages_with_percentages = {}
    
    for language, bytes_count in data.items():
        percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
        languages_with_percentages[language] = {
            "bytes": bytes_count,
            "percentage": round(percentage, 2)
        }
    
    # Sort by bytes count
    sorted_languages = dict(sorted(languages_with_percentages.items(), 
                                 key=lambda x: x[1]["bytes"], reverse=True))
    
    return json.dumps(sorted_languages, indent=2)


@client_tool
def get_repository_contributors(owner: str, repo: str, per_page: int = 30) -> str:
    """
    Get contributors to a repository
    
    :param owner: Repository owner
    :param repo: Repository name
    :param per_page: Number of contributors to fetch (max 100)
    :return: JSON string with contributor information
    """
    print("************************************************")
    print("tool called: get_repository_contributors")
    print(f"Getting contributors for {owner}/{repo}")
    print("************************************************")
    params = {"per_page": min(per_page, 100)}
    data = _make_github_request(f"repos/{owner}/{repo}/contributors", params)
    
    if "error" in data:
        return json.dumps(data)
    
    contributors = []
    for contributor in data:
        contributors.append({
            "login": contributor.get("login"),
            "contributions": contributor.get("contributions"),
            "type": contributor.get("type"),
            "profile_url": contributor.get("html_url")
        })
    
    return json.dumps(contributors, indent=2)


@client_tool
def get_repository_issues(owner: str, repo: str, state: str = "open", per_page: int = 30) -> str:
    """
    Get issues from a repository
    
    :param owner: Repository owner
    :param repo: Repository name
    :param state: Issue state ('open', 'closed', or 'all')
    :param per_page: Number of issues to fetch (max 100)
    :return: JSON string with issue information
    """
    print("************************************************")
    print("tool called: get_repository_issues")
    print(f"Getting issues for {owner}/{repo}")
    print("************************************************")
    params = {"state": state, "per_page": min(per_page, 100)}
    data = _make_github_request(f"repos/{owner}/{repo}/issues", params)
    
    if "error" in data:
        return json.dumps(data)
    
    issues = []
    for issue in data:
        # Skip pull requests (they appear in issues endpoint)
        if issue.get("pull_request"):
            continue
            
        issues.append({
            "number": issue.get("number"),
            "title": issue.get("title"),
            "state": issue.get("state"),
            "created_at": issue.get("created_at"),
            "updated_at": issue.get("updated_at"),
            "labels": [label.get("name") for label in issue.get("labels", [])],
            "assignees": [assignee.get("login") for assignee in issue.get("assignees", [])],
            "comments": issue.get("comments"),
            "author": issue.get("user", {}).get("login"),
            "url": issue.get("html_url")
        })
    
    return json.dumps(issues, indent=2)


@client_tool
def get_repository_pulls(owner: str, repo: str, state: str = "open", per_page: int = 30) -> str:
    """
    Get pull requests from a repository
    
    :param owner: Repository owner
    :param repo: Repository name
    :param state: PR state ('open', 'closed', or 'all')
    :param per_page: Number of PRs to fetch (max 100)
    :return: JSON string with pull request information
    """
    print("************************************************")
    print("tool called: get_repository_pulls")
    print(f"Getting pulls for {owner}/{repo}")
    print("************************************************")
    params = {"state": state, "per_page": min(per_page, 100)}
    data = _make_github_request(f"repos/{owner}/{repo}/pulls", params)
    
    if "error" in data:
        return json.dumps(data)
    
    pulls = []
    for pr in data:
        pulls.append({
            "number": pr.get("number"),
            "title": pr.get("title"),
            "state": pr.get("state"),
            "created_at": pr.get("created_at"),
            "updated_at": pr.get("updated_at"),
            "merged_at": pr.get("merged_at"),
            "author": pr.get("user", {}).get("login"),
            "base_branch": pr.get("base", {}).get("ref"),
            "head_branch": pr.get("head", {}).get("ref"),
            "additions": pr.get("additions"),
            "deletions": pr.get("deletions"),
            "changed_files": pr.get("changed_files"),
            "comments": pr.get("comments"),
            "review_comments": pr.get("review_comments"),
            "url": pr.get("html_url")
        })
    
    return json.dumps(pulls, indent=2)


@client_tool
def get_repository_releases(owner: str, repo: str, per_page: int = 10) -> str:
    """
    Get releases from a repository
    
    :param owner: Repository owner
    :param repo: Repository name
    :param per_page: Number of releases to fetch (max 100)
    :return: JSON string with release information
    """
    print("************************************************")
    print("tool called: get_repository_releases")
    print(f"Getting releases for {owner}/{repo}")
    print("************************************************")
    params = {"per_page": min(per_page, 100)}
    data = _make_github_request(f"repos/{owner}/{repo}/releases", params)
    
    if "error" in data:
        return json.dumps(data)
    
    releases = []
    for release in data:
        releases.append({
            "name": release.get("name"),
            "tag_name": release.get("tag_name"),
            "published_at": release.get("published_at"),
            "created_at": release.get("created_at"),
            "author": release.get("author", {}).get("login"),
            "prerelease": release.get("prerelease"),
            "draft": release.get("draft"),
            "assets_count": len(release.get("assets", [])),
            "body": release.get("body", "")[:500] + "..." if len(release.get("body", "")) > 500 else release.get("body", ""),
            "url": release.get("html_url")
        })
    
    return json.dumps(releases, indent=2)


@client_tool
def search_repositories(query: str, sort: str = "stars", order: str = "desc", per_page: int = 10) -> str:
    """
    Search for repositories on GitHub
    
    :param query: Search query
    :param sort: Sort criteria ('stars', 'forks', 'help-wanted-issues', 'updated')
    :param order: Sort order ('asc' or 'desc')
    :param per_page: Number of results to fetch (max 100)
    :return: JSON string with search results
    """
    print("************************************************")
    print("tool called: search_repositories")
    print(f"Searching for repositories for {query}")
    print("************************************************")
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": min(per_page, 100)
    }
    data = _make_github_request("search/repositories", params)
    
    if "error" in data:
        return json.dumps(data)
    
    results = {
        "total_count": data.get("total_count"),
        "incomplete_results": data.get("incomplete_results"),
        "repositories": []
    }
    
    for repo in data.get("items", []):
        results["repositories"].append({
            "name": repo.get("name"),
            "full_name": repo.get("full_name"),
            "description": repo.get("description"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count"),
            "forks": repo.get("forks_count"),
            "open_issues": repo.get("open_issues_count"),
            "created_at": repo.get("created_at"),
            "updated_at": repo.get("updated_at"),
            "topics": repo.get("topics", []),
            "license": repo.get("license", {}).get("name") if repo.get("license") else None,
            "url": repo.get("html_url")
        })
    
    return json.dumps(results, indent=2)