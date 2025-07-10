# Placeholder for GitHub agent integration 

import os
import logging
from github import Github, GithubException
from typing import List, Dict, Any

logger = logging.getLogger("external_agents.github_agent")

def get_github_client():
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        logger.info("Using authenticated GitHub client.")
        return Github(token)
    else:
        logger.warning("No GITHUB_TOKEN set, using unauthenticated GitHub client (rate limits apply).")
        return Github()

def fetch_issues(repo_full_name: str, state: str = "open") -> List[Dict[str, Any]]:
    """Fetch issues from a GitHub repository. Returns a list or an error dict."""
    logger.info(f"Fetching {state} issues for repo: {repo_full_name}")
    gh = get_github_client()
    try:
        repo = gh.get_repo(repo_full_name)
        issues = repo.get_issues(state=state)
        return [
            {
                "id": issue.id,
                "number": issue.number,
                "title": issue.title,
                "user": issue.user.login,
                "state": issue.state,
                "url": issue.html_url,
            }
            for issue in issues if not issue.pull_request
        ]
    except GithubException as e:
        logger.error(f"GitHub API error: {e.data if hasattr(e, 'data') else str(e)}")
        return [{"error": f"GitHub API error: {e.data if hasattr(e, 'data') else str(e)}"}]
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return [{"error": f"Unexpected error: {str(e)}"}]

def fetch_pull_requests(repo_full_name: str, state: str = "open") -> List[Dict[str, Any]]:
    """Fetch pull requests from a GitHub repository. Returns a list or an error dict."""
    logger.info(f"Fetching {state} pull requests for repo: {repo_full_name}")
    gh = get_github_client()
    try:
        repo = gh.get_repo(repo_full_name)
        prs = repo.get_pulls(state=state)
        return [
            {
                "id": pr.id,
                "number": pr.number,
                "title": pr.title,
                "user": pr.user.login,
                "state": pr.state,
                "url": pr.html_url,
            }
            for pr in prs
        ]
    except GithubException as e:
        logger.error(f"GitHub API error: {e.data if hasattr(e, 'data') else str(e)}")
        return [{"error": f"GitHub API error: {e.data if hasattr(e, 'data') else str(e)}"}]
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return [{"error": f"Unexpected error: {str(e)}"}] 