"""GitHub connector for developer activity metrics.

This module provides a wrapper around the GitHub REST API endpoint for
weekly commit activity. GitHub returns an array of 52 weekly
dictionaries, each containing the total number of commits per day and
the week timestamp. Note that the endpoint only works on repositories
with fewer than 10 000 commits; otherwise GitHub returns status code
422【911524837470379†L318-L329】.
"""

import httpx


async def fetch_weekly_commit_activity(owner: str, repo: str) -> dict:
    """Fetch weekly commit activity from GitHub.

    Args:
        owner: GitHub user or organization name.
        repo: Repository name.

    Returns:
        JSON list of weekly commit activity or a message if the data is
        still being generated.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/stats/commit_activity"
    headers = {"Accept": "application/vnd.github+json"}
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, headers=headers)
        # A 202 status means GitHub is generating the statistic. The caller
        # should retry later. Return a friendly message instead of raising.
        if response.status_code == 202:
            return {"message": "GitHub is generating the statistics, please retry later"}
        response.raise_for_status()
        return response.json()