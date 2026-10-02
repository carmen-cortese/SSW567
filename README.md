# SSW567

[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/Nfiy1BJX4J3rurg1SduVdY/HLSKNaioAcMATPAZDKFXRQ/tree/main.svg?style=svg&circle-token=CCIPRJ_M6bj2tCkFkySC7Hw81114j_6c0854352dfb9bbf11f49f0567db55cc712a5e7f)](https://dl.circleci.com/status-badge/redirect/circleci/Nfiy1BJX4J3rurg1SduVdY/HLSKNaioAcMATPAZDKFXRQ/tree/main)

## HW 02: Triangle classification ([`triangle_testing/`](triangle_testing))

- `classify_triangle.py`: classifies a triangle as equilateral, isosceles or scalene, and says whether it is a right triangle
- `test_classify_triangle.py`: unit tests

```
cd triangle_testing
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

Run the tests:

```
python -m unittest -v test_github_api.py
python -m unittest -v test_github_api_live.py
```

- `test_github_api_live.py` calls the real GitHub API for `carmen-cortese` (repos with commits), `CarmenCorteseBTP` (a real user with no repos) and a user that doesn't exist.
- `test_github_api.py` uses fake API responses for cases that can't be set up reliably on a real account: exact commit counts, results split across several pages, empty repos and rate-limit errors.
