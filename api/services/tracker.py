"""Core tracker: orchestrates repo processing, time calc & framework detection."""
import logging
import time as time_mod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────
SESSION_GAP = timedelta(hours=2)
MIN_SESSION = 15  # minutes — base time for isolated commits
MAX_SESSION = 4   # hours — cap per single session to avoid unrealistic gaps


def calculate_coding_time(commits: list) -> float:
    """Calculate coding hours from commit timestamps using session detection.

    Algorithm:
    - Sort commits by time
    - Group into sessions: commits within SESSION_GAP of each other
    - Each session: sum of gaps between commits (capped) + MIN_SESSION for last
    - Single commit = MIN_SESSION minutes
    """
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

    if not times:
        return 0.0

    if len(times) == 1:
        return MIN_SESSION / 60

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

    # Calculate time of day (using UTC for now, or user tz)
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


def process_single_repo(service, username: str, repo: dict,
                         since_iso: str, until_iso: str, fw_maps: dict, ignore_langs: list) -> dict:
    """Process one repository: languages, commits, frameworks."""
    name = repo["name"]
    owner = repo.get("owner", {}).get("login", username)
    result = {"name": name, "langs": {}, "frameworks": set(), "hours": 0.0, "hours_dist": {"night": 0, "morning": 0, "daytime": 0, "evening": 0}}

    try:
        # Skip empty repos
        if repo.get("size", 0) == 0:
            return result

        # 1. Languages
        langs = service.get_languages(owner, name)
        if ignore_langs and langs:
            langs = {k: v for k, v in langs.items() if k.lower() not in ignore_langs}
        if not langs:
            return result
        result["langs"] = langs

        # 2. Commits — try both username formats for accuracy
        commits = service.get_commits(owner, name, username, since_iso, until_iso)

        # Also try with GitHub email if we have different owner
        if not commits and owner.lower() != username.lower():
            commits = service.get_commits(owner, name, owner, since_iso, until_iso)

        valid = [c for c in commits if is_valid_commit(c)]
        if valid:
            hours_calc, hours_dist = calculate_coding_time(valid)
            result["hours"] = hours_calc
            result["hours_dist"] = hours_dist

        # 3. Frameworks
        primary = repo.get("language", "")
        result["frameworks"] = service.detect_frameworks(
            owner, name, primary, fw_maps
        )
    except Exception as e:
        logger.error(f"Error processing {name}: {e}")

    return result


def run_tracker(service, username: str, period_days: int,
                fw_maps: dict, max_repos: int = 200, ignore_langs: list = None) -> dict:
    """
    Main entry: fetch ALL repos, process in parallel, aggregate results.
    Returns {langs, frameworks, total_hours, repo_count, period_days, username}.
    """
    start_time = time_mod.time()
    deadline = start_time + 55  # Vercel Pro = 60s, Free = 10s — be safe

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=period_days)
    since_iso = since.isoformat()
    until_iso = now.isoformat()

    # Fetch ALL repos (public + private + forks)
    repos = service.get_repos(username, max_repos, include_forks=True)
    if not repos:
        return {
            "langs": {}, "frameworks": {}, "total_hours": 0,
            "repo_count": 0, "period_days": period_days, "username": username,
            "prs": 0, "issues": 0, "busiest_time": "Daytime",
        }

    # Filter: only repos pushed within the period
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
    processed = 0

    # Fetch PRs and Issues in background
    prs_future = None
    issues_future = None

    # Parallel processing with more workers
    workers = min(12, len(repos_in_period) + 2)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        # Submit repo jobs
        futures = {
            pool.submit(
                process_single_repo, service, username, repo,
                since_iso, until_iso, fw_maps, ignore_langs or []
            ): repo
            for repo in repos_in_period
        }
        
        # Submit PR and Issue count jobs
        prs_future = pool.submit(service.get_user_prs, username)
        issues_future = pool.submit(service.get_user_issues, username)

        for future in as_completed(futures):
            # Check deadline
            if time_mod.time() > deadline:
                logger.warning("Approaching timeout, returning partial results")
                break

            try:
                r = future.result(timeout=8)
            except Exception as e:
                logger.error(f"Future error: {e}")
                continue

            if r["hours"] <= 0:
                continue

            processed += 1
            total_bytes = sum(r["langs"].values()) or 1

            # Distribute time across languages by byte proportion
            for lang, byte_count in r["langs"].items():
                lang_hours[lang] += r["hours"] * (byte_count / total_bytes)

            # Time of day dist
            for k, v in r.get("hours_dist", {}).items():
                total_hours_dist[k] += v

    total = sum(lang_hours.values())
    
    # Extract PRs and Issues safely
    prs = 0
    issues = 0
    try:
        if prs_future:
            prs = prs_future.result(timeout=2)
        if issues_future:
            issues = issues_future.result(timeout=2)
    except Exception:
        pass

    # Determine Busiest Time
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
