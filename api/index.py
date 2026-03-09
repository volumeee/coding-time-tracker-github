"""CodeStats API — FastAPI entry point for Vercel serverless deployment."""
import hashlib
import logging
import os
import sys

# Ensure api/ directory is on the Python path for Vercel
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx
from config import (
    BUILD_FW,
    CACHE_TTL,
    COMPOSER_FW,
    GITHUB_TOKEN,
    GO_MOD_FW,
    PACKAGE_JSON_FW,
    REQUIREMENTS_FW,
)
from fastapi import FastAPI, HTTPException, Query, Request
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


def get_etag(data_str: str) -> str:
    """Generate ETag from string content."""
    return hashlib.md5(data_str.encode("utf-8")).hexdigest()


@app.get("/api")
async def get_stats(
    request: Request,
    username: str = Query(..., description="GitHub username"),
    theme: str = Query("dark", description="Theme: dark, light, radical, tokyonight"),
    layout: str = Query("landscape", description="Layout: landscape or portrait"),
    width: int = Query(0, ge=0, le=1200, description="Card width in px (0=auto)"),
    langs_count: int = Query(8, ge=1, le=20, description="Max languages to show"),
    period: int = Query(365, ge=7, le=3650, description="Period in days"),
    max_repos: int = Query(200, ge=1, le=500, description="Max repos to scan"),
    ignore_langs: str = Query("", description="Comma-separated languages to ignore"),
    show_frameworks: bool = Query(True, description="Show frameworks section"),
    show_languages: bool = Query(True, description="Show languages section"),
    show_title: bool = Query(True, description="Show title/header"),
    show_footer: bool = Query(True, description="Show footer"),
    no_cache: bool = Query(False, description="Force refresh data"),
):
    """Generate an SVG coding stats card for the given username."""
    client_ip = request.client.host if request.client else "unknown"
    if not cache.check_rate_limit(f"req:{client_ip}", limit=30, window=60):
        svg = generate_error_svg("Rate limit exceeded (30 req/min). Please try again later.", theme)
        return Response(content=svg, media_type="image/svg+xml", headers=SVG_HEADERS)

    if not GITHUB_TOKEN:
        svg = generate_error_svg("GITHUB_TOKEN not configured on server.", theme)
        return Response(content=svg, media_type="image/svg+xml", headers=SVG_HEADERS)

    # Normalize ignored languages string for cache and passing
    ignored_list = [lang.strip().lower() for lang in ignore_langs.split(",") if lang.strip()]
    data_cache_key = f"codestats_data:{username}:{period}:{max_repos}:{'|'.join(ignored_list)}"

    data = None
    if not no_cache and cache.available:
        data = cache.get(data_cache_key)

    if not data:
        logger.info(f"Processing stats for {username} (period={period}d, repos={max_repos})")
        try:
            async with httpx.AsyncClient() as client:
                service = GitHubService(token=GITHUB_TOKEN, client=client)
                data = await run_tracker(service, username, period, FW_MAPS, max_repos, ignored_list)

            if data["total_hours"] == 0 and data["repo_count"] == 0:
                svg = generate_error_svg(f"No coding activity found for '{username}' in the last {period} days.", theme)
                return Response(content=svg, media_type="image/svg+xml", headers=SVG_HEADERS)

            if cache.available:
                cache.set(data_cache_key, data, CACHE_TTL)
                logger.info(f"Cached results for {username}")

        except Exception as e:
            logger.error(f"Error processing {username}: {e}")
            svg = generate_error_svg(f"Processing error: {str(e)[:80]}", theme)
            return Response(content=svg, media_type="image/svg+xml", headers=SVG_HEADERS)

    # Re-render SVG without re-fetching API if parameters like theme vary
    svg = generate_svg(
        data, theme, langs_count, show_frameworks,
        layout, width, show_title, show_footer, show_languages,
    )

    etag = get_etag(svg)
    if_none_match = request.headers.get("if-none-match")
    if if_none_match == etag:
        return Response(status_code=304)

    headers = dict(SVG_HEADERS)
    headers["ETag"] = etag
    return Response(content=svg, media_type="image/svg+xml", headers=headers)


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "cache": "connected" if cache.available else "unavailable",
        "token": "configured" if GITHUB_TOKEN else "missing",
    }


@app.get("/api/json")
async def get_json(
    request: Request,
    username: str = Query(..., description="GitHub username"),
    period: int = Query(365, ge=7, le=3650),
    max_repos: int = Query(200, ge=1, le=500),
    ignore_langs: str = Query(""),
    no_cache: bool = Query(False),
):
    """Return raw JSON stats (for programmatic use)."""
    client_ip = request.client.host if request.client else "unknown"
    if not cache.check_rate_limit(f"req:{client_ip}", limit=30, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded (30 req/min)")

    if not GITHUB_TOKEN:
        return {"error": "GITHUB_TOKEN not configured"}

    ignored_list = [lang.strip().lower() for lang in ignore_langs.split(",") if lang.strip()]
    data_cache_key = f"codestats_data:{username}:{period}:{max_repos}:{'|'.join(ignored_list)}"

    if not no_cache and cache.available:
        data = cache.get(data_cache_key)
        if data:
            return data

    async with httpx.AsyncClient() as client:
        service = GitHubService(token=GITHUB_TOKEN, client=client)
        data = await run_tracker(service, username, period, FW_MAPS, max_repos, ignored_list)

    if cache.available:
        cache.set(data_cache_key, data, CACHE_TTL)

    return data


@app.get("/api/code")
async def get_code(
    request: Request,
    username: str = Query(..., description="GitHub username"),
    langs_count: int = Query(10, ge=1, le=20),
    period: int = Query(365, ge=7, le=3650),
    max_repos: int = Query(200, ge=1, le=500),
    ignore_langs: str = Query(""),
    show_frameworks: bool = Query(True),
    no_cache: bool = Query(False),
):
    """Return text-based code block stats (for README markdown)."""
    client_ip = request.client.host if request.client else "unknown"
    if not cache.check_rate_limit(f"req:{client_ip}", limit=30, window=60):
        return Response(content="Error: Rate limit exceeded (30 req/min). Please try again later.", media_type="text/plain")

    if not GITHUB_TOKEN:
        return Response(content="Error: GITHUB_TOKEN not configured", media_type="text/plain")

    ignored_list = [lang.strip().lower() for lang in ignore_langs.split(",") if lang.strip()]
    data_cache_key = f"codestats_data:{username}:{period}:{max_repos}:{'|'.join(ignored_list)}"
    data = None

    if not no_cache and cache.available:
        data = cache.get(data_cache_key)

    if not data:
        async with httpx.AsyncClient() as client:
            service = GitHubService(token=GITHUB_TOKEN, client=client)
            data = await run_tracker(service, username, period, FW_MAPS, max_repos, ignored_list)
        if cache.available:
            cache.set(data_cache_key, data, CACHE_TTL)

    code = generate_code_block(data, langs_count, show_frameworks)
    
    etag = get_etag(code)
    if_none_match = request.headers.get("if-none-match")
    if if_none_match == etag:
        return Response(status_code=304)

    return Response(
        content=code, 
        media_type="text/plain",
        headers={"Cache-Control": "public, max-age=7200", "ETag": etag}
    )
