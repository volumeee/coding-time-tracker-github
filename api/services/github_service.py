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
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 404:
                logger.error(f"HTTP {e.code}: {url}")
            return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

    def _paginate(self, url: str, params: dict, max_items: int = 0) -> list:
        """Paginate through all pages of a GitHub API endpoint."""
        items, page = [], 1
        while True:
            p = {**params, "page": page, "per_page": 100}
            data = self._request(url, p)
            if not data or not isinstance(data, list):
                break
            items.extend(data)
            if len(data) < 100:
                break
            page += 1
            # Safety: GitHub API has limits
            if page > 20:
                break
        if max_items > 0:
            return items[:max_items]
        return items

    def get_repos(self, username: str, max_repos: int = 200,
                  include_forks: bool = False) -> list:
        """Fetch ALL repos (public + private if token has access).

        Uses /user/repos (authenticated) to include private repos,
        falls back to /users/{username}/repos if that fails.
        """
        # Try authenticated endpoint first — includes private repos
        repos = self._paginate(
            "https://api.github.com/user/repos",
            {"sort": "pushed", "direction": "desc",
             "affiliation": "owner", "visibility": "all"},
            max_items=max_repos,
        )

        # Filter to only repos owned by username
        if repos:
            repos = [r for r in repos
                     if r.get("owner", {}).get("login", "").lower() == username.lower()]

        # Fallback to public endpoint if authenticated didn't work
        if not repos:
            repos = self._paginate(
                f"https://api.github.com/users/{username}/repos",
                {"sort": "pushed", "direction": "desc"},
                max_items=max_repos,
            )

        # Optionally filter out forks
        if not include_forks:
            repos = [r for r in repos if not r.get("fork", False)]

        logger.info(f"Fetched {len(repos)} repos for {username}")
        return repos[:max_repos]

    def get_languages(self, owner: str, repo: str) -> dict:
        """Get language byte-count breakdown for a repo."""
        data = self._request(f"https://api.github.com/repos/{owner}/{repo}/languages")
        return data if isinstance(data, dict) else {}

    def get_commits(self, owner: str, repo: str, author: str,
                    since: str, until: str) -> list:
        """Fetch all commits for a repo within a date range."""
        return self._paginate(
            f"https://api.github.com/repos/{owner}/{repo}/commits",
            {"author": author, "since": since, "until": until},
        )

    def get_commit_detail(self, owner: str, repo: str, sha: str) -> Optional[dict]:
        """Get detailed commit info including stats (additions/deletions)."""
        return self._request(
            f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
        )

    def get_repo_root_files(self, owner: str, repo: str) -> list:
        """Get names of all files in the root of the repository to detect tools quickly."""
        data = self._request(f"https://api.github.com/repos/{owner}/{repo}/contents")
        if isinstance(data, list):
            return [str(item.get("name", "")).lower() for item in data]
        return []

    def has_github_actions(self, owner: str, repo: str) -> bool:
        """Check if .github/workflows exists."""
        data = self._request(f"https://api.github.com/repos/{owner}/{repo}/contents/.github")
        if isinstance(data, list):
            return any(item.get("name") == "workflows" for item in data)
        return False

    def get_user_prs(self, username: str) -> int:
        """Fetch total merged/created PRs by the user."""
        data = self._request("https://api.github.com/search/issues", {"q": f"author:{username} type:pr"})
        return data.get("total_count", 0) if isinstance(data, dict) else 0

    def get_user_issues(self, username: str) -> int:
        """Fetch total issues created by the user."""
        data = self._request("https://api.github.com/search/issues", {"q": f"author:{username} type:issue"})
        return data.get("total_count", 0) if isinstance(data, dict) else 0

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

        # Fast Tool Detection via Root Files (No need to download entire files)
        root_files = self.get_repo_root_files(owner, repo)
        if "dockerfile" in root_files or "docker-compose.yml" in root_files or "docker-compose.yaml" in root_files:
            frameworks.add("Docker")
        if "tailwind.config.js" in root_files or "tailwind.config.ts" in root_files:
            frameworks.add("Tailwind CSS")
        if "next.config.js" in root_files or "next.config.ts" in root_files or "next.config.mjs" in root_files:
            frameworks.add("Next.js")
        if "svelte.config.js" in root_files:
            frameworks.add("SvelteKit")
        if "astro.config.mjs" in root_files or "astro.config.js" in root_files:
            frameworks.add("Astro")
        if "prisma" in root_files: # folder
            frameworks.add("Prisma")
        if any(f.endswith(".k8s.yaml") or f.endswith("deployment.yaml") for f in root_files):
            frameworks.add("Kubernetes")

        # Github Actions Check
        if ".github" in root_files and self.has_github_actions(owner, repo):
            frameworks.add("GitHub Actions")

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
                if file_path == "build.gradle":
                    if "com.android.application" in lower:
                        frameworks.add("Android SDK")

        return frameworks
