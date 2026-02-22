"""CodeStats API — FastAPI entry point for Vercel serverless deployment."""
import logging
import os
import sys

# Ensure api/ directory is on the Python path for Vercel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    BUILD_FW,
    CACHE_TTL,
    COMPOSER_FW,
    GITHUB_TOKEN,
    GO_MOD_FW,
    PACKAGE_JSON_FW,
    REQUIREMENTS_FW,
)
from fastapi import FastAPI, Query
from fastapi.responses import Response
from services.cache import CacheService
from services.github_service import GitHubService
from services.svg_generator import generate_code_block, generate_error_svg, generate_svg
from services.tracker import run_tracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CodeStats API",
    description="Generate beautiful coding statistics cards for your GitHub/GitLab profile.",
    version="1.0.0",
)

cache = CacheService()

# Pre-built framework detection maps
FW_MAPS = {
    "package_json": PACKAGE_JSON_FW,
    "requirements": REQUIREMENTS_FW,
    "composer": COMPOSER_FW,
    "go_mod": GO_MOD_FW,
    "build": BUILD_FW,
}

SVG_HEADERS = {
    "Content-Type": "image/svg+xml",
    "Cache-Control": "public, max-age=7200, s-maxage=7200, stale-while-revalidate=3600",
}


@app.get("/api")
def get_stats(
    username: str = Query(..., description="GitHub username"),
    theme: str = Query("dark", description="Theme: dark, light, radical, tokyonight"),
    layout: str = Query("landscape", description="Layout: landscape or portrait"),
    width: int = Query(0, ge=0, le=1200, description="Card width in px (0=auto)"),
    langs_count: int = Query(8, ge=1, le=20, description="Max languages to show"),
    period: int = Query(365, ge=7, le=3650, description="Period in days"),
    max_repos: int = Query(200, ge=1, le=500, description="Max repos to scan"),
    show_frameworks: bool = Query(True, description="Show frameworks section"),
    show_languages: bool = Query(True, description="Show languages section"),
    show_title: bool = Query(True, description="Show title/header"),
    show_footer: bool = Query(True, description="Show footer"),
    no_cache: bool = Query(False, description="Force refresh data"),
):
    """Generate an SVG coding stats card for the given username."""
    if not GITHUB_TOKEN:
        svg = generate_error_svg("GITHUB_TOKEN not configured on server.", theme)
        return Response(content=svg, media_type="image/svg+xml", headers=SVG_HEADERS)

    cache_key = f"codestats:{username}:{period}:{max_repos}"

    # Try cache first
    if not no_cache and cache.available:
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {username}")
            svg = generate_svg(
                cached, theme, langs_count, show_frameworks,
                layout, width, show_title, show_footer, show_languages,
            )
            return Response(content=svg, media_type="image/svg+xml", headers=SVG_HEADERS)

    # Process live
    logger.info(f"Processing stats for {username} (period={period}d, repos={max_repos})")
    try:
        service = GitHubService(token=GITHUB_TOKEN)
        data = run_tracker(service, username, period, FW_MAPS, max_repos)

        if data["total_hours"] == 0 and data["repo_count"] == 0:
            svg = generate_error_svg(
                f"No coding activity found for '{username}' in the last {period} days.",
                theme,
            )
            return Response(content=svg, media_type="image/svg+xml", headers=SVG_HEADERS)

        # Cache results
        if cache.available:
            cache.set(cache_key, data, CACHE_TTL)
            logger.info(f"Cached results for {username}")

        svg = generate_svg(
            data, theme, langs_count, show_frameworks,
            layout, width, show_title, show_footer, show_languages,
        )
        return Response(content=svg, media_type="image/svg+xml", headers=SVG_HEADERS)

    except Exception as e:
        logger.error(f"Error processing {username}: {e}")
        svg = generate_error_svg(f"Processing error: {str(e)[:80]}", theme)
        return Response(content=svg, media_type="image/svg+xml", headers=SVG_HEADERS)


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "cache": "connected" if cache.available else "unavailable",
        "token": "configured" if GITHUB_TOKEN else "missing",
    }


@app.get("/api/json")
def get_json(
    username: str = Query(..., description="GitHub username"),
    period: int = Query(365, ge=7, le=3650),
    max_repos: int = Query(200, ge=1, le=500),
    no_cache: bool = Query(False),
):
    """Return raw JSON stats (for programmatic use)."""
    if not GITHUB_TOKEN:
        return {"error": "GITHUB_TOKEN not configured"}

    cache_key = f"codestats:{username}:{period}:{max_repos}"

    if not no_cache and cache.available:
        cached = cache.get(cache_key)
        if cached:
            return cached

    service = GitHubService(token=GITHUB_TOKEN)
    data = run_tracker(service, username, period, FW_MAPS, max_repos)

    if cache.available:
        cache.set(cache_key, data, CACHE_TTL)

    return data

@app.get("/api/code")
def get_code(
    username: str = Query(..., description="GitHub username"),
    langs_count: int = Query(10, ge=1, le=20),
    period: int = Query(365, ge=7, le=3650),
    max_repos: int = Query(200, ge=1, le=500),
    show_frameworks: bool = Query(True),
    no_cache: bool = Query(False),
):
    """Return text-based code block stats (for README markdown)."""
    if not GITHUB_TOKEN:
        return Response(content="Error: GITHUB_TOKEN not configured", media_type="text/plain")

    cache_key = f"codestats:{username}:{period}:{max_repos}"
    data = None

    if not no_cache and cache.available:
        data = cache.get(cache_key)

    if not data:
        service = GitHubService(token=GITHUB_TOKEN)
        data = run_tracker(service, username, period, FW_MAPS, max_repos)
        if cache.available:
            cache.set(cache_key, data, CACHE_TTL)

    code = generate_code_block(data, langs_count, show_frameworks)
    return Response(content=code, media_type="text/plain",
                    headers={"Cache-Control": "public, max-age=7200"})
