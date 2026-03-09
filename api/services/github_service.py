"""GitHub API service for fetching repository, commit, and framework data."""
import asyncio
import base64
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class GitHubService:
    """Handles all GitHub API interactions (Async)."""

    def __init__(self, token: str, client: httpx.AsyncClient):
        self.token = token
        self.client = client

    async def _request(self, url: str, params: dict = None) -> Optional[any]:
        """Make an authenticated GitHub API request."""
        try:
            resp = await self.client.get(url, params=params, timeout=12.0)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code != 404:
                logger.error(f"HTTP {resp.status_code}: {url}")
            return None
        except Exception as e:
            logger.error(f"Request error for {url}: {e}")
            return None

    async def _paginate(self, url: str, params: dict, max_items: int = 0) -> list:
        """Paginate through all pages of a GitHub API endpoint concurrently."""
        items = []
        # First request to get total pages and first page items
        p = {**(params or {}), "page": 1, "per_page": 100}
        resp = await self.client.get(url, params=p, timeout=15.0)
        
        if resp.status_code != 200:
            return items
            
        data = resp.json()
        if not isinstance(data, list):
            return items
            
        items.extend(data)
        if len(data) < 100:
            return items if max_items == 0 else items[:max_items]
            
        # Parallel pagination if more than 1 page (we limit to max 10 pages for safety)
        tasks = []
        for page in range(2, 11):
            tasks.append(self._request(url, {**(params or {}), "page": page, "per_page": 100}))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, list):
                items.extend(res)
                if len(res) < 100:
                    break # Stop looking at further pages if this one is short
                    
        return items if max_items == 0 else items[:max_items]

    async def get_repos(self, username: str, max_repos: int = 200,
                  include_forks: bool = False) -> list:
        """Fetch ALL repos (public + private if token has access)."""
        repos = await self._paginate(
            "https://api.github.com/user/repos",
            {"sort": "pushed", "direction": "desc",
             "affiliation": "owner", "visibility": "all"},
            max_items=max_repos,
        )

        if repos:
            repos = [r for r in repos
                     if r.get("owner", {}).get("login", "").lower() == username.lower()]

        if not repos:
            repos = await self._paginate(
                f"https://api.github.com/users/{username}/repos",
                {"sort": "pushed", "direction": "desc"},
                max_items=max_repos,
            )

        if not include_forks:
            repos = [r for r in repos if not r.get("fork", False)]

        logger.info(f"Fetched {len(repos)} repos for {username}")
        return repos[:max_repos]

    async def get_languages(self, owner: str, repo: str) -> dict:
        """Get language byte-count breakdown for a repo."""
        data = await self._request(f"https://api.github.com/repos/{owner}/{repo}/languages")
        return data if isinstance(data, dict) else {}

    async def get_commits(self, owner: str, repo: str, author: str,
                    since: str, until: str) -> list:
        """Fetch all commits for a repo within a date range."""
        return await self._paginate(
            f"https://api.github.com/repos/{owner}/{repo}/commits",
            {"author": author, "since": since, "until": until},
        )

    async def get_repo_root_files(self, owner: str, repo: str) -> list:
        """Get names of all files in the root of the repository to detect tools quickly."""
        data = await self._request(f"https://api.github.com/repos/{owner}/{repo}/contents")
        if isinstance(data, list):
            return [str(item.get("name", "")).lower() for item in data]
        return []

    async def has_github_actions(self, owner: str, repo: str) -> bool:
        """Check if .github/workflows exists."""
        data = await self._request(f"https://api.github.com/repos/{owner}/{repo}/contents/.github")
        if isinstance(data, list):
            return any(item.get("name") == "workflows" for item in data)
        return False

    async def get_user_prs(self, username: str) -> int:
        """Fetch total merged/created PRs by the user."""
        data = await self._request("https://api.github.com/search/issues", {"q": f"author:{username} type:pr"})
        return data.get("total_count", 0) if isinstance(data, dict) else 0

    async def get_user_issues(self, username: str) -> int:
        """Fetch total issues created by the user."""
        data = await self._request("https://api.github.com/search/issues", {"q": f"author:{username} type:issue"})
        return data.get("total_count", 0) if isinstance(data, dict) else 0

    async def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get decoded file content from a repository."""
        data = await self._request(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        )
        if data and isinstance(data, dict) and "content" in data:
            try:
                return base64.b64decode(data["content"]).decode("utf-8")
            except Exception:
                pass
        return None

    async def detect_frameworks(self, owner: str, repo: str,
                          primary_lang: str, fw_maps: dict) -> set:
        """Detect frameworks based on config files relevant to primary language."""
        frameworks = set()
        lang = (primary_lang or "").lower()

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

        root_files = await self.get_repo_root_files(owner, repo)
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
        if "prisma" in root_files: 
            frameworks.add("Prisma")
        if any(f.endswith(".k8s.yaml") or f.endswith("deployment.yaml") for f in root_files):
            frameworks.add("Kubernetes")

        if ".github" in root_files and await self.has_github_actions(owner, repo):
            frameworks.add("GitHub Actions")

        # Fetch all config files concurrently
        fetch_tasks = [self.get_file_content(owner, repo, ch[0]) for ch in checks]
        contents = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        for i, (file_path, parse_mode, mapping) in enumerate(checks):
            content = contents[i]
            if not content or isinstance(content, Exception):
                continue

            import json
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
