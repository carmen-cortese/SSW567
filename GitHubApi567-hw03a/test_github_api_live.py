"""Tests that call the real GitHub API.

Commit counts grow whenever someone pushes, so these tests check things that stay
true over time (known repos are listed, counts are at least what they are today)
rather than exact numbers. Exact behavior is covered in test_github_api.py.
"""
import unittest

from github_api import format_results, get_repo_commit_counts

USER = "carmen-cortese"


class TestLiveGitHubApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Call the API once and share the result, to stay under GitHub's
        # 60 requests/hour limit for unauthenticated clients
        cls.results = dict(get_repo_commit_counts(USER))

    # SSW567 is the repo this code is submitted in, so it is the one repo
    # guaranteed to keep existing

    def test_course_repo_is_listed(self):
        self.assertIn("SSW567", self.results)

    def test_every_repo_has_commits(self):
        for repo, count in self.results.items():
            self.assertIsInstance(count, int, repo)
            self.assertGreaterEqual(count, 1, repo)

    def test_course_repo_commit_count(self):
        # 8 commits when this test was written; pushes only add more
        self.assertGreaterEqual(self.results["SSW567"], 8)

    def test_output_format(self):
        lines = format_results(self.results.items())
        self.assertEqual(len(lines), len(self.results))
        self.assertIn(
            f"Repo: SSW567 Number of commits: {self.results['SSW567']}", lines
        )

    def test_real_user_with_no_repos(self):
        self.assertEqual(get_repo_commit_counts("CarmenCorteseBTP"), [])

    def test_nonexistent_user_raises(self):
        with self.assertRaisesRegex(ValueError, "404"):
            get_repo_commit_counts("this-user-does-not-exist-ssw567-hw03a")


if __name__ == "__main__":
    unittest.main(verbosity=2)
