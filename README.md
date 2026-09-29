# SSW567_classify_triangle

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/carmen-cortese/SSW567_classify_triangle/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/carmen-cortese/SSW567_classify_triangle/tree/main)

## HW 02: Triangle classification

- `classify_triangle.py`: classifies a triangle as equilateral, isosceles or scalene, and says whether it is a right triangle
- `test_classify_triangle.py`: unit tests

```
python -m unittest -v test_classify_triangle.py
```

## HW 03a: GitHub API ([`GitHubApi567-hw03a/`](GitHubApi567-hw03a))

Given a GitHub user ID, lists each of the user's repositories and how many commits it has:

```
cd GitHubApi567-hw03a
pip install -r requirements.txt
python github_api.py richkempinski
```

```
Repo: hellogitworld Number of commits: 50
Repo: helloworld Number of commits: 6
...
```

Run the tests (they use fake API responses, so they need no network access and don't count against GitHub's rate limit):

```
python -m unittest -v test_github_api.py
```
