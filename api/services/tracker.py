"""Core tracker: orchestrates repo processing, time calc & framework detection."""
import asyncio
import logging
import time as time_mod
from collections import defaultdict
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────
SESSION_GAP = timedelta(hours=2)
MIN_SESSION = 15  # minutes — base time for isolated commits
MAX_SESSION = 4   # hours — cap per single session to avoid unrealistic gaps


def calculate_coding_time(commits: list) -> float:
    """Calculate coding hours from commit timestamps using session detection."""
    if not commits:
        return 0.0, {"night": 0, "morning": 0, "daytime": 0, "evening": 0}

    times = []
    for c in commits:
        try:
            dt = datetime.strptime(
                c["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=timezone.utc)
            times.append(dt)
        except (KeyError, ValueError, TypeError):
            continue

    if not times:
        return 0.0, {"night": 0, "morning": 0, "daytime": 0, "evening": 0}

    if len(times) == 1:
        hours_dist = {"night": 0, "morning": 0, "daytime": 0, "evening": 0}
        h = times[0].hour
        if 0 <= h < 6:
            hours_dist["night"] = 1
        elif 6 <= h < 12:
            hours_dist["morning"] = 1
        elif 12 <= h < 18:
            hours_dist["daytime"] = 1
        else:
            hours_dist["evening"] = 1
        return MIN_SESSION / 60, hours_dist

    times.sort()
    total_secs = 0.0

    for i in range(len(times) - 1):
        diff = times[i + 1] - times[i]
        secs = diff.total_seconds()

        if diff < SESSION_GAP:
            total_secs += min(secs, MAX_SESSION * 3600)
        else:
            total_secs += MIN_SESSION * 60

    total_secs += MIN_SESSION * 60

    hours_dist = {"night": 0, "morning": 0, "daytime": 0, "evening": 0}
    for t in times:
        h = t.hour
        if 0 <= h < 6:
            hours_dist["night"] += 1
        elif 6 <= h < 12:
            hours_dist["morning"] += 1
        elif 12 <= h < 18:
            hours_dist["daytime"] += 1
        else:
            hours_dist["evening"] += 1

    return total_secs / 3600, hours_dist


def is_valid_commit(commit: dict) -> bool:
    """Filter out merge/bot/auto commits."""
    try:
        msg = commit["commit"]["message"].lower()
    except (KeyError, TypeError):
        return False
    skip = [
        "merge pull request", "merge branch", "merge remote",
        "automated", "[bot]", "auto-update", "bump version",
        "update readme", "prettier", "eslint fix",
        "initial commit", "auto commit",
    ]
    return not any(p in msg for p in skip)


async def process_single_repo(service, username: str, repo: dict,
                         since_iso: str, until_iso: str, fw_maps: dict, ignore_langs: list, sem: asyncio.Semaphore) -> dict:
    """Process one repository: languages, commits, frameworks, throttled by semaphore."""
    async with sem:
        name = repo["name"]
        owner = repo.get("owner", {}).get("login", username)
    result = {"name": name, "langs": {}, "frameworks": set(), "hours": 0.0, "hours_dist": {"night": 0, "morning": 0, "daytime": 0, "evening": 0}}

    try:
        if repo.get("size", 0) == 0:
            return result

        # 1. Languages
        langs = await service.get_languages(owner, name)
        if ignore_langs and langs:
            langs = {k: v for k, v in langs.items() if k.lower() not in ignore_langs}
        if not langs:
            return result
        result["langs"] = langs

        # 2. Commits — try both username formats concurrently
        tasks = [
            service.get_commits(owner, name, username, since_iso, until_iso),
        ]
        if owner.lower() != username.lower():
            tasks.append(service.get_commits(owner, name, owner, since_iso, until_iso))

        commit_results = await asyncio.gather(*tasks, return_exceptions=True)
        commits = []
        for res in commit_results:
            if isinstance(res, list):
                commits.extend(res)

        valid = [c for c in commits if is_valid_commit(c)]
        if valid:
            hours_calc, hours_dist = calculate_coding_time(valid)
            result["hours"] = hours_calc
            result["hours_dist"] = hours_dist

        # 3. Frameworks
        primary = repo.get("language", "")
        result["frameworks"] = await service.detect_frameworks(
            owner, name, primary, fw_maps
        )
    except Exception as e:
        logger.error(f"Error processing {name}: {e}")

    return result


async def run_tracker(service, username: str, period_days: int,
                fw_maps: dict, max_repos: int = 200, ignore_langs: list = None) -> dict:
    start_time = time_mod.time()

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=period_days)
    since_iso = since.isoformat()
    until_iso = now.isoformat()

    # Fetch ALL repos
    repos = await service.get_repos(username, max_repos, include_forks=True)
    if not repos:
        return {
            "langs": {}, "frameworks": {}, "total_hours": 0,
            "repo_count": 0, "period_days": period_days, "username": username,
            "prs": 0, "issues": 0, "busiest_time": "Daytime",
        }

    repos_in_period = []
    for r in repos:
        pushed = r.get("pushed_at", "")
        if pushed:
            try:
                pushed_dt = datetime.strptime(
                    pushed, "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=timezone.utc)
                if pushed_dt >= since:
                    repos_in_period.append(r)
            except ValueError:
                repos_in_period.append(r)
        else:
            repos_in_period.append(r)

    logger.info(f"Processing {len(repos_in_period)}/{len(repos)} repos "
                f"pushed within {period_days} days for {username}")

    lang_hours = defaultdict(float)
    fw_hours = defaultdict(float)
    total_hours_dist = {"night": 0, "morning": 0, "daytime": 0, "evening": 0}

    # Parallel processing of all repositories with a concurrency limit
    # GitHub secondary rate limit triggers if doing too many simultaneous calls. Max 15 safe.
    sem = asyncio.Semaphore(15)
    repo_tasks = [
        process_single_repo(service, username, repo, since_iso, until_iso, fw_maps, ignore_langs or [], sem)
        for repo in repos_in_period
    ]
    
    # Also fetch PRs and Issues simultaneously
    extra_tasks = [
        service.get_user_prs(username),
        service.get_user_issues(username)
    ]

    all_results = await asyncio.gather(*repo_tasks, *extra_tasks, return_exceptions=True)
    
    repo_results = all_results[:-2]
    extra_results = all_results[-2:]
    
    prs = extra_results[0] if not isinstance(extra_results[0], Exception) else 0
    issues = extra_results[1] if not isinstance(extra_results[1], Exception) else 0

    processed = 0
    for r in repo_results:
        if isinstance(r, Exception):
            logger.error(f"Future error: {r}")
            continue

        if r["hours"] <= 0:
            continue

        processed += 1
        total_bytes = sum(r["langs"].values()) or 1

        for lang, byte_count in r["langs"].items():
            lang_hours[lang] += r["hours"] * (byte_count / total_bytes)

        for k, v in r.get("hours_dist", {}).items():
            total_hours_dist[k] += v
            
        for fw in r.get("frameworks", set()):
            fw_hours[fw] += r["hours"]

    total = sum(lang_hours.values())
    
    busiest_time = "Daytime"
    if sum(total_hours_dist.values()) > 0:
        busiest_time_key = max(total_hours_dist, key=total_hours_dist.get)
        busiest_map = {"night": "Night Owl", "morning": "Early Bird", "daytime": "Day Worker", "evening": "Evening Coder"}
        busiest_time = busiest_map.get(busiest_time_key, "Daytime")

    elapsed = time_mod.time() - start_time
    logger.info(f"Processed {processed} repos in {elapsed:.1f}s — {total:.1f} hrs, {prs} PRs, pattern: {busiest_time}")

    return {
        "langs": dict(sorted(lang_hours.items(), key=lambda x: x[1], reverse=True)),
        "frameworks": dict(sorted(fw_hours.items(), key=lambda x: x[1], reverse=True)),
        "total_hours": round(total, 2),
        "repo_count": processed,
        "period_days": period_days,
        "username": username,
        "prs": prs,
        "issues": issues,
        "busiest_time": busiest_time,
    }
