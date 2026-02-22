"""Core tracker: orchestrates repo processing, time calc & framework detection."""
import logging
import time as time_mod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────
SESSION_GAP = timedelta(hours=2)
BASE_MINUTES = 30  # base time per isolated commit


def calculate_coding_time(commits: list) -> float:
    """Calculate coding hours from commit timestamps using session detection."""
    if not commits:
        return 0.0

    times = []
    for c in commits:
        try:
            dt = datetime.strptime(
                c["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=timezone.utc)
            times.append(dt)
        except (KeyError, ValueError):
            continue

    if len(times) < 2:
        return len(times) * (BASE_MINUTES / 60)

    times.sort()
    total = 0.0
    for i in range(len(times) - 1):
        diff = times[i + 1] - times[i]
        total += diff.total_seconds() if diff < SESSION_GAP else BASE_MINUTES * 60

    total += BASE_MINUTES * 60  # last commit
    return total / 3600


def is_valid_commit(commit: dict) -> bool:
    """Filter out merge/bot commits."""
    try:
        msg = commit["commit"]["message"].lower()
    except (KeyError, TypeError):
        return False
    skip = ["merge", "automated", "bot", "auto-update", "bump version",
            "update readme", "prettier", "eslint fix"]
    return not any(p in msg for p in skip)


def process_single_repo(service, username: str, repo: dict,
                         since_iso: str, until_iso: str, fw_maps: dict) -> dict:
    """Process one repository: languages, commits, frameworks."""
    name = repo["name"]
    result = {"name": name, "langs": {}, "frameworks": set(), "hours": 0.0}

    try:
        # 1. Languages
        langs = service.get_languages(username, name)
        if not langs:
            return result
        result["langs"] = langs

        # 2. Commits
        commits = service.get_commits(username, name, username, since_iso, until_iso)
        valid = [c for c in commits if is_valid_commit(c)]
        result["hours"] = calculate_coding_time(valid)

        # 3. Frameworks
        primary = repo.get("language", "")
        result["frameworks"] = service.detect_frameworks(
            username, name, primary, fw_maps
        )
    except Exception as e:
        logger.error(f"Error processing {name}: {e}")

    return result


def run_tracker(service, username: str, period_days: int,
                fw_maps: dict, max_repos: int = 50) -> dict:
    """
    Main entry: fetch repos, process in parallel, aggregate results.
    Returns {langs: {name: hours}, frameworks: {name: hours}, total_hours, repo_count}.
    """
    start_time = time_mod.time()
    deadline = start_time + 8.5  # stay under Vercel 10s limit

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=period_days)
    since_iso = since.isoformat()
    until_iso = now.isoformat()

    # Fetch repos
    repos = service.get_repos(username, max_repos)
    if not repos:
        return {"langs": {}, "frameworks": {}, "total_hours": 0, "repo_count": 0}

    lang_hours = defaultdict(float)
    fw_hours = defaultdict(float)
    processed = 0

    # Parallel processing
    workers = min(8, len(repos))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(
                process_single_repo, service, username, repo,
                since_iso, until_iso, fw_maps
            ): repo
            for repo in repos
        }

        for future in as_completed(futures):
            # Check deadline
            if time_mod.time() > deadline:
                logger.warning("Approaching timeout, returning partial results")
                break

            try:
                r = future.result(timeout=5)
            except Exception as e:
                logger.error(f"Future error: {e}")
                continue

            if r["hours"] <= 0:
                continue

            processed += 1
            total_bytes = sum(r["langs"].values()) or 1

            # Distribute time across languages
            for lang, byte_count in r["langs"].items():
                lang_hours[lang] += r["hours"] * (byte_count / total_bytes)

            # Each framework gets full repo time
            for fw in r["frameworks"]:
                fw_hours[fw] += r["hours"]

    total = sum(lang_hours.values())

    return {
        "langs": dict(sorted(lang_hours.items(), key=lambda x: x[1], reverse=True)),
        "frameworks": dict(sorted(fw_hours.items(), key=lambda x: x[1], reverse=True)),
        "total_hours": round(total, 2),
        "repo_count": processed,
        "period_days": period_days,
        "username": username,
    }
