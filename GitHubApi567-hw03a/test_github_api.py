"""HW 03b: unit tests with every GitHub API call mocked out using unittest.mock.

Every test class that exercises API code is decorated with
@mock.patch("github_api.requests.get"), so requests.get is replaced for every
test in it and no test can reach GitHub.
"""
import json
import unittest
from unittest import mock

import requests

from github_api import (
    API_URL,
    fetch_json,
    format_results,
    get_all_pages,
    get_repo_commit_counts,
)


def make_response(status, body=None, next_url=None, text=None):
    """Build a fake requests.Response with only the attributes github_api uses."""
    response = mock.Mock()
    response.status_code = status
    response.text = json.dumps(body) if text is None else text
    response.links = {"next": {"url": next_url}} if next_url else {}
    return response


def serve(responses):
    """Return a fake requests.get that answers from a dict of {url: response}."""
    def fake_get(url, timeout=None):
        if url not in responses:
            raise AssertionError(f"unexpected request to {url}")
        return responses[url]
    return fake_get


def requested_urls(mock_get):
    """The URLs requests.get was called with, in order."""
    return [c.args[0] for c in mock_get.call_args_list]


def repos_url(user):
    return f"{API_URL}/users/{user}/repos?per_page=100"


def commits_url(user, repo):
    return f"{API_URL}/repos/{user}/{repo}/commits?per_page=100"


@mock.patch("github_api.requests.get")
class TestGetRepoCommitCounts(unittest.TestCase):

    def test_two_repos(self, mock_get):
        mock_get.side_effect = serve({
            repos_url("John567"): make_response(200, [{"name": "Triangle567"}, {"name": "Square567"}]),
            commits_url("John567", "Triangle567"): make_response(200, [{}] * 10),
            commits_url("John567", "Square567"): make_response(200, [{}] * 27),
        })
        self.assertEqual(
            get_repo_commit_counts("John567"),
            [("Triangle567", 10), ("Square567", 27)],
        )

    def test_calls_the_two_github_apis_in_order(self, mock_get):
        mock_get.side_effect = serve({
            repos_url("John567"): make_response(200, [{"name": "Triangle567"}, {"name": "Square567"}]),
            commits_url("John567", "Triangle567"): make_response(200, [{}]),
            commits_url("John567", "Square567"): make_response(200, [{}]),
        })
        get_repo_commit_counts("John567")
        self.assertEqual(
            requested_urls(mock_get),
            [
                repos_url("John567"),
                commits_url("John567", "Triangle567"),
                commits_url("John567", "Square567"),
            ],
        )

    def test_requests_use_a_timeout(self, mock_get):
        mock_get.side_effect = serve({repos_url("u"): make_response(200, [])})
        get_repo_commit_counts("u")
        mock_get.assert_called_once_with(repos_url("u"), timeout=10)

    def test_user_with_no_repos(self, mock_get):
        mock_get.side_effect = serve({repos_url("empty"): make_response(200, [])})
        self.assertEqual(get_repo_commit_counts("empty"), [])

    def test_empty_repo_has_zero_commits(self, mock_get):
        mock_get.side_effect = serve({
            repos_url("u"): make_response(200, [{"name": "blank"}]),
            commits_url("u", "blank"): make_response(409, {"message": "Git Repository is empty."}),
        })
        self.assertEqual(get_repo_commit_counts("u"), [("blank", 0)])

    def test_commits_over_multiple_pages_are_all_counted(self, mock_get):
        page2 = commits_url("u", "big") + "&page=2"
        mock_get.side_effect = serve({
            repos_url("u"): make_response(200, [{"name": "big"}]),
            commits_url("u", "big"): make_response(200, [{}] * 100, next_url=page2),
            page2: make_response(200, [{}] * 35),
        })
        self.assertEqual(get_repo_commit_counts("u"), [("big", 135)])

    def test_repos_over_multiple_pages_are_all_listed(self, mock_get):
        page2 = repos_url("u") + "&page=2"
        names = [f"repo{i}" for i in range(102)]
        responses = {
            repos_url("u"): make_response(200, [{"name": n} for n in names[:100]], next_url=page2),
            page2: make_response(200, [{"name": n} for n in names[100:]]),
        }
        for n in names:
            responses[commits_url("u", n)] = make_response(200, [{}])
        mock_get.side_effect = serve(responses)
        self.assertEqual(get_repo_commit_counts("u"), [(n, 1) for n in names])

    def test_error_on_one_repo_raises_instead_of_partial_results(self, mock_get):
        mock_get.side_effect = serve({
            repos_url("u"): make_response(200, [{"name": "ok"}, {"name": "broken"}]),
            commits_url("u", "ok"): make_response(200, [{}] * 5),
            commits_url("u", "broken"): make_response(500, {"message": "Server Error"}),
        })
        with self.assertRaisesRegex(ValueError, "500"):
            get_repo_commit_counts("u")

    def test_unknown_user_raises(self, mock_get):
        mock_get.side_effect = serve({repos_url("nobody"): make_response(404, {"message": "Not Found"})})
        with self.assertRaisesRegex(ValueError, "404"):
            get_repo_commit_counts("nobody")

    def test_rate_limit_raises(self, mock_get):
        mock_get.side_effect = serve({
            repos_url("u"): make_response(403, {"message": "API rate limit exceeded"}),
        })
        with self.assertRaisesRegex(ValueError, "rate limit"):
            get_repo_commit_counts("u")

    def test_network_error_is_not_hidden(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("network is down")
        with self.assertRaises(requests.exceptions.ConnectionError):
            get_repo_commit_counts("u")

    def test_blank_user_id_raises_without_calling_github(self, mock_get):
        with self.assertRaises(ValueError):
            get_repo_commit_counts("   ")
        mock_get.assert_not_called()

    def test_non_string_user_id_raises_without_calling_github(self, mock_get):
        with self.assertRaises(ValueError):
            get_repo_commit_counts(None)
        mock_get.assert_not_called()

    def test_user_id_whitespace_is_stripped(self, mock_get):
        mock_get.side_effect = serve({repos_url("u"): make_response(200, [])})
        self.assertEqual(get_repo_commit_counts("  u  "), [])
        self.assertEqual(requested_urls(mock_get), [repos_url("u")])


@mock.patch("github_api.requests.get")
class TestGetAllPages(unittest.TestCase):

    def test_single_page(self, mock_get):
        mock_get.return_value = make_response(200, [1, 2, 3])
        self.assertEqual(get_all_pages("a"), [1, 2, 3])

    def test_error_with_non_json_body(self, mock_get):
        mock_get.return_value = make_response(500, text="<html>Server Error</html>")
        with self.assertRaisesRegex(ValueError, "500"):
            get_all_pages("a")

    def test_success_status_with_non_list_body_raises(self, mock_get):
        mock_get.return_value = make_response(200, {"message": "not a list"})
        with self.assertRaisesRegex(ValueError, "unexpected response"):
            get_all_pages("a")


@mock.patch("github_api.requests.get")
class TestFetchJson(unittest.TestCase):

    def test_parses_body_and_next_link(self, mock_get):
        mock_get.return_value = make_response(200, [{"name": "x"}], next_url="page2")
        self.assertEqual(fetch_json("url"), (200, [{"name": "x"}], "page2"))

    def test_invalid_json_gives_none_body(self, mock_get):
        mock_get.return_value = make_response(502, text="<html>")
        self.assertEqual(fetch_json("url"), (502, None, None))


class TestFormatResults(unittest.TestCase):
    """format_results does no network calls, so nothing needs mocking."""

    def test_format_matches_assignment_example(self):
        self.assertEqual(
            format_results([("Triangle567", 10), ("Square567", 27)]),
            [
                "Repo: Triangle567 Number of commits: 10",
                "Repo: Square567 Number of commits: 27",
            ],
        )

    def test_format_empty(self):
        self.assertEqual(format_results([]), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
