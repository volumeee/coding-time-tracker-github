"""GitHub API service for fetching repository, commit, and framework data."""
import base64
import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

logger = logging.getLogger(__name__)


class GitHubService:
    """Handles all GitHub API interactions."""

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodeStats-Tracker/1.0",
        }

    def _request(self, url: str, params: dict = None) -> Optional[any]:
        """Make an authenticated GitHub API request."""
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 404:
                logger.error(f"HTTP {e.code}: {url}")
            return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

    def get_repos(self, username: str, max_repos: int = 50) -> list:
        """Fetch public repos sorted by most recently pushed."""
        repos, page = [], 1
        while True:
            data = self._request(
                f"https://api.github.com/users/{username}/repos",
                {"page": page, "per_page": 100, "sort": "pushed", "direction": "desc"},
            )
            if not data or not isinstance(data, list):
                break
            repos.extend(data)
            if len(data) < 100:
                break
            page += 1
        return repos[:max_repos]

    def get_languages(self, owner: str, repo: str) -> dict:
        """Get language byte-count breakdown for a repo."""
        data = self._request(f"https://api.github.com/repos/{owner}/{repo}/languages")
        return data if isinstance(data, dict) else {}

    def get_commits(self, owner: str, repo: str, author: str,
                    since: str, until: str) -> list:
        """Fetch commits for a repo within a date range."""
        all_commits, page = [], 1
        while True:
            data = self._request(
                f"https://api.github.com/repos/{owner}/{repo}/commits",
                {"author": author, "since": since, "until": until,
                 "page": page, "per_page": 100},
            )
            if not data or not isinstance(data, list):
                break
            all_commits.extend(data)
            if len(data) < 100:
                break
            page += 1
        return all_commits

    def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get decoded file content from a repository."""
        data = self._request(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        )
        if data and isinstance(data, dict) and "content" in data:
            try:
                return base64.b64decode(data["content"]).decode("utf-8")
            except Exception:
                pass
        return None

    def detect_frameworks(self, owner: str, repo: str,
                          primary_lang: str, fw_maps: dict) -> set:
        """Detect frameworks based on config files relevant to primary language."""
        frameworks = set()
        lang = (primary_lang or "").lower()

        # Determine which files to check
        checks = []
        if lang in ("javascript", "typescript", "vue", "svelte", "html", "css", ""):
            checks.append(("package.json", "json", fw_maps.get("package_json", {})))
        if lang in ("python", "jupyter notebook", ""):
            checks.append(("requirements.txt", "text", fw_maps.get("requirements", {})))
        if lang in ("php", ""):
            checks.append(("composer.json", "json_composer", fw_maps.get("composer", {})))
        if lang in ("go", ""):
            checks.append(("go.mod", "text", fw_maps.get("go_mod", {})))
        if lang in ("java", "kotlin", ""):
            checks.append(("build.gradle", "text", fw_maps.get("build", {})))
            checks.append(("pom.xml", "text", fw_maps.get("build", {})))
        if lang in ("dart", ""):
            checks.append(("pubspec.yaml", "text", {"flutter": "Flutter"}))
        if lang in ("ruby", ""):
            checks.append(("Gemfile", "text", {"rails": "Rails", "sinatra": "Sinatra"}))

        if not checks:
            checks.append(("package.json", "json", fw_maps.get("package_json", {})))

        for file_path, parse_mode, mapping in checks:
            content = self.get_file_content(owner, repo, file_path)
            if not content:
                continue

            if parse_mode == "json":
                try:
                    pkg = json.loads(content)
                    deps = {**pkg.get("dependencies", {}),
                            **pkg.get("devDependencies", {})}
                    for key, name in mapping.items():
                        if key in deps:
                            frameworks.add(name)
                except (json.JSONDecodeError, AttributeError):
                    pass

            elif parse_mode == "json_composer":
                try:
                    pkg = json.loads(content)
                    deps = {**pkg.get("require", {}),
                            **pkg.get("require-dev", {})}
                    for key, name in mapping.items():
                        if key in deps:
                            frameworks.add(name)
                except (json.JSONDecodeError, AttributeError):
                    pass

            elif parse_mode == "text":
                lower = content.lower()
                for key, name in mapping.items():
                    if key in lower:
                        frameworks.add(name)
                # Special: Android SDK
                if file_path == "build.gradle":
                    if "com.android.application" in lower:
                        frameworks.add("Android SDK")

        return frameworks
