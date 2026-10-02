"""HW 03a: list a GitHub user's repositories and the number of commits in each."""
import json
import sys

import requests

API_URL = "https://api.github.com"


def fetch_json(url):
    """GET a URL and return (status_code, parsed JSON body, next page URL or None)."""
    response = requests.get(url, timeout=10)
    try:
        body = json.loads(response.text)
    except ValueError:
        body = None
    next_url = response.links.get("next", {}).get("url")
    return response.status_code, body, next_url


def get_all_pages(url, fetch=fetch_json):
    """Follow GitHub's pagination and return every item from every page."""
    items = []
    while url:
        status, body, url = fetch(url)
        if status == 409:
            # GitHub returns 409 Conflict for the commits of an empty repository
            return []
        if status != 200:
            message = body.get("message", "") if isinstance(body, dict) else ""
            raise ValueError(f"GitHub API error {status}: {message}")
        if not isinstance(body, list):
            raise ValueError("GitHub API returned an unexpected response (expected a list)")
        items.extend(body)
    return items


def get_repo_commit_counts(user_id, fetch=fetch_json):
    """Return a list of (repo name, number of commits) tuples for user_id.

    `fetch` does the HTTP work; tests pass in a fake so no network is needed.
    """
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("user_id must be a non-empty string")
    user_id = user_id.strip()

    repos = get_all_pages(f"{API_URL}/users/{user_id}/repos?per_page=100", fetch)
    results = []
    for repo in repos:
        name = repo["name"]
        commits = get_all_pages(
            f"{API_URL}/repos/{user_id}/{name}/commits?per_page=100", fetch
        )
        results.append((name, len(commits)))
    return results


def format_results(results):
    """Turn (repo, count) tuples into the output lines required by the assignment."""
    return [f"Repo: {name} Number of commits: {count}" for name, count in results]


def main(user_id):
    for line in format_results(get_repo_commit_counts(user_id)):
        print(line)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "richkempinski")
