import unittest
from unittest import mock

from github_api import (
    API_URL,
    fetch_json,
    format_results,
    get_all_pages,
    get_repo_commit_counts,
)


def fake_api(pages):
    """Build a fake fetch function from a dict of {url: (status, body, next_url)}."""
    def fetch(url):
        return pages[url]
    return fetch


def repos_url(user):
    return f"{API_URL}/users/{user}/repos?per_page=100"


def commits_url(user, repo):
    return f"{API_URL}/repos/{user}/{repo}/commits?per_page=100"


class TestGetRepoCommitCounts(unittest.TestCase):

    def test_two_repos(self):
        fetch = fake_api({
            repos_url("John567"): (200, [{"name": "Triangle567"}, {"name": "Square567"}], None),
            commits_url("John567", "Triangle567"): (200, [{}] * 10, None),
            commits_url("John567", "Square567"): (200, [{}] * 27, None),
        })
        self.assertEqual(
            get_repo_commit_counts("John567", fetch),
            [("Triangle567", 10), ("Square567", 27)],
        )

    def test_user_with_no_repos(self):
        fetch = fake_api({repos_url("empty"): (200, [], None)})
        self.assertEqual(get_repo_commit_counts("empty", fetch), [])

    def test_empty_repo_has_zero_commits(self):
        fetch = fake_api({
            repos_url("u"): (200, [{"name": "blank"}], None),
            commits_url("u", "blank"): (409, {"message": "Git Repository is empty."}, None),
        })
        self.assertEqual(get_repo_commit_counts("u", fetch), [("blank", 0)])

    def test_commits_over_multiple_pages_are_all_counted(self):
        page2 = commits_url("u", "big") + "&page=2"
        fetch = fake_api({
            repos_url("u"): (200, [{"name": "big"}], None),
            commits_url("u", "big"): (200, [{}] * 100, page2),
            page2: (200, [{}] * 35, None),
        })
        self.assertEqual(get_repo_commit_counts("u", fetch), [("big", 135)])

    def test_unknown_user_raises(self):
        fetch = fake_api({repos_url("nobody"): (404, {"message": "Not Found"}, None)})
        with self.assertRaisesRegex(ValueError, "404"):
            get_repo_commit_counts("nobody", fetch)

    def test_rate_limit_raises(self):
        fetch = fake_api({repos_url("u"): (403, {"message": "API rate limit exceeded"}, None)})
        with self.assertRaisesRegex(ValueError, "rate limit"):
            get_repo_commit_counts("u", fetch)

    def test_blank_user_id_raises(self):
        with self.assertRaises(ValueError):
            get_repo_commit_counts("   ")

    def test_non_string_user_id_raises(self):
        with self.assertRaises(ValueError):
            get_repo_commit_counts(None)

    def test_user_id_whitespace_is_stripped(self):
        fetch = fake_api({repos_url("u"): (200, [], None)})
        self.assertEqual(get_repo_commit_counts("  u  ", fetch), [])


class TestGetAllPages(unittest.TestCase):

    def test_single_page(self):
        fetch = fake_api({"a": (200, [1, 2, 3], None)})
        self.assertEqual(get_all_pages("a", fetch), [1, 2, 3])

    def test_error_with_non_json_body(self):
        fetch = fake_api({"a": (500, None, None)})
        with self.assertRaisesRegex(ValueError, "500"):
            get_all_pages("a", fetch)


class TestFormatResults(unittest.TestCase):

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


class TestFetchJson(unittest.TestCase):
    """fetch_json is the only code that talks to requests; mock it here."""

    @mock.patch("github_api.requests.get")
    def test_parses_body_and_next_link(self, mock_get):
        mock_get.return_value = mock.Mock(
            status_code=200, text='[{"name": "x"}]', links={"next": {"url": "page2"}}
        )
        self.assertEqual(fetch_json("url"), (200, [{"name": "x"}], "page2"))

    @mock.patch("github_api.requests.get")
    def test_invalid_json_gives_none_body(self, mock_get):
        mock_get.return_value = mock.Mock(status_code=502, text="<html>", links={})
        self.assertEqual(fetch_json("url"), (502, None, None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
