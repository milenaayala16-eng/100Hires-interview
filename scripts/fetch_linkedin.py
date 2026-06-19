#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch the 3 most recent LinkedIn posts for each profile via the Apify API.

Strategy to minimize API usage
-------------------------------
The URLs in research/sources.md are post-level URLs (e.g., /posts/handle_...).
We extract the author handle from each URL and reconstruct the canonical profile
URL (https://www.linkedin.com/in/<handle>/).

We then send ALL profile URLs in a SINGLE Apify actor run (batch mode) with
resultsLimit=3.  This means we pay for ONE actor run instead of one per profile.

Usage
-----
  # Step 1 – dry-run with 1 profile to verify the JSON schema
  python scripts/fetch_linkedin.py --test-only

  # Step 2 – process all profiles
  python scripts/fetch_linkedin.py

  # Optional: limit to N profiles (debug)
  python scripts/fetch_linkedin.py --limit 3

Requirements
------------
  Set environment variable APIFY_API_TOKEN before running.
  Output files are written to research/linkedin-posts/.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Primary actor – accepts multiple profileUrls in a single run.
# Change here if Apify Store offers a better actor in the future.
ACTOR_ID = "apimaestro~linkedin-profile-posts"

APIFY_BASE = "https://api.apify.com/v2/acts"

# How many recent posts to request per profile.
POSTS_PER_PROFILE = 3

# Seconds to wait for the synchronous Apify response (actor timeout included).
REQUEST_TIMEOUT_SECONDS = 300


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SourceEntry:
    display_name: str   # e.g. "Kevin Indig"
    source_url: str     # e.g. "https://www.linkedin.com/posts/kevinindig_..."
    handle: str | None = field(default=None, init=False)
    profile_url: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.handle = _extract_handle(self.source_url)
        self.profile_url = (
            f"https://www.linkedin.com/in/{self.handle}/"
            if self.handle
            else self.source_url
        )


@dataclass
class Post:
    text: str
    date: str


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_sources_md(path: Path) -> list[SourceEntry]:
    """Parse research/sources.md and return one SourceEntry per valid line."""
    pattern = re.compile(r"^(.+?)\s+(https?://\S+)$")
    entries: list[SourceEntry] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = pattern.match(line)
        if not m:
            print(f"[WARN] Línea ignorada (formato inválido): {line!r}", flush=True)
            continue
        entries.append(SourceEntry(display_name=m.group(1).strip(), source_url=m.group(2).strip()))
    return entries


def _extract_handle(url: str) -> str | None:
    """Extract the LinkedIn public handle from a post or profile URL.

    Handles:
      /posts/<handle>_<activity-id>-...
      /in/<handle>/
    """
    # Post URL: linkedin.com/posts/handle_...
    m = re.search(r"linkedin\.com/posts/([^_/?#]+)", url, re.IGNORECASE)
    if m:
        h = m.group(1).strip().strip("/")
        return h or None
    # Profile URL: linkedin.com/in/handle/
    m = re.search(r"linkedin\.com/in/([^/?#]+)", url, re.IGNORECASE)
    if m:
        h = m.group(1).strip().strip("/")
        return h or None
    return None


def slugify(name: str) -> str:
    """Convert a display name to a safe filename stem."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "perfil"


# ---------------------------------------------------------------------------
# Apify API call
# ---------------------------------------------------------------------------

def call_apify_actor(token: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    """POST to Apify run-sync-get-dataset-items and return the dataset as a list."""
    endpoint = f"{APIFY_BASE}/{ACTOR_ID}/run-sync-get-dataset-items"
    qs = urllib.parse.urlencode({"token": token, "format": "json"})
    url = f"{endpoint}?{qs}"

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} al llamar a Apify: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Error de red al llamar a Apify: {exc.reason}") from exc

    parsed = json.loads(raw)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return [parsed]
    raise RuntimeError("Respuesta inesperada de Apify (ni lista ni objeto JSON).")


# ---------------------------------------------------------------------------
# Post extraction helpers
# ---------------------------------------------------------------------------

def _first(item: dict[str, Any], *keys: str) -> str | None:
    for k in keys:
        v = item.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _normalize_post(raw: dict[str, Any]) -> Post | None:
    text = _first(raw, "text", "postText", "content", "description", "caption")
    if not text:
        return None
    date = _first(raw, "date", "postedAt", "publishedAt", "createdAt", "timestamp", "time") or "N/D"
    return Post(text=text, date=date)


def _author_url_for_item(item: dict[str, Any]) -> str:
    return _first(item, "authorProfileUrl", "profileUrl", "linkedinUrl", "url") or ""


def _posts_from_items(
    items: list[dict[str, Any]],
    entry: SourceEntry,
    limit: int = POSTS_PER_PROFILE,
) -> list[Post]:
    """Extract posts that belong to *entry* from the actor response."""
    handle_norm = entry.handle.lower() if entry.handle else ""
    found: list[Post] = []
    seen: set[str] = set()

    for item in items:
        # Case A: item has a nested list of posts.
        for nest_key in ("posts", "recentPosts", "latestPosts", "activity"):
            nested = item.get(nest_key)
            if not isinstance(nested, list):
                continue
            for raw_post in nested:
                if not isinstance(raw_post, dict):
                    continue
                if handle_norm:
                    author_url = _author_url_for_item(raw_post) or _author_url_for_item(item)
                    if handle_norm not in author_url.lower():
                        continue
                post = _normalize_post(raw_post)
                if post and post.text not in seen:
                    seen.add(post.text)
                    found.append(post)
            break  # only one nested key per item
        else:
            # Case B: the item itself is a post (flat structure).
            author_url = _author_url_for_item(item)
            if handle_norm and handle_norm not in author_url.lower():
                continue
            post = _normalize_post(item)
            if post and post.text not in seen:
                seen.add(post.text)
                found.append(post)

        if len(found) >= limit:
            break

    return found[:limit]


# ---------------------------------------------------------------------------
# Batch strategy (single API call for all profiles)
# ---------------------------------------------------------------------------

def batch_fetch_all(
    token: str,
    entries: list[SourceEntry],
) -> dict[str, list[Post]]:
    """Fetch posts for ALL profiles in ONE Apify actor run.

    Returns a mapping {entry.display_name -> list[Post]}.
    Falls back to per-profile calls only for entries that returned no posts.
    """
    profile_urls = [e.profile_url for e in entries]

    print(f"\n[BATCH] Enviando {len(profile_urls)} perfiles en una sola llamada a Apify...", flush=True)
    payload = {
        "profileUrls": profile_urls,
        "resultsLimit": POSTS_PER_PROFILE,
    }

    items = call_apify_actor(token=token, payload=payload)
    print(f"[BATCH] Respuesta recibida: {len(items)} items en el dataset.", flush=True)

    results: dict[str, list[Post]] = {}
    for entry in entries:
        posts = _posts_from_items(items, entry)
        results[entry.display_name] = posts

    return results


def per_profile_fallback(
    token: str,
    entry: SourceEntry,
) -> list[Post]:
    """Single-profile fallback. Tries profile URL first, then the raw post URL."""
    for payload in [
        {"profileUrls": [entry.profile_url], "resultsLimit": POSTS_PER_PROFILE},
        {"startUrls": [{"url": entry.profile_url}], "resultsLimit": POSTS_PER_PROFILE},
        {"urls": [entry.source_url], "resultsLimit": POSTS_PER_PROFILE},
    ]:
        try:
            items = call_apify_actor(token=token, payload=payload)
            posts = _posts_from_items(items, entry)
            if posts:
                return posts
        except RuntimeError as exc:
            print(f"  [WARN] Payload alternativo falló: {exc}", flush=True)
    return []


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_output(output_dir: Path, entry: SourceEntry, posts: list[Post]) -> Path:
    """Write a .txt file for the given entry."""
    filename = f"{slugify(entry.display_name)}.txt"
    out_path = output_dir / filename

    output_parts: list[str] = [
        f"Nombre: {entry.display_name}",
        f"Perfil: {entry.profile_url}"
    ]

    for idx, post in enumerate(posts, start=1):
        # Collapse multiple empty lines inside the post text
        body_text = post.text.strip()
        body_text = re.sub(r'\n{3,}', '\n\n', body_text)
        
        separator = "=" * 80
        title = f"POST {idx} — [{post.date}]"
        
        post_block = f"{separator}\n{title}\n{separator}\n\n{body_text}"
        output_parts.append(post_block)

    out_path.write_text("\n\n".join(output_parts) + "\n", encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Test mode (single profile, shows raw JSON)
# ---------------------------------------------------------------------------

def run_test(token: str, entry: SourceEntry) -> None:
    """Single-profile test: prints the raw JSON from Apify for inspection."""
    print(f"\n[TEST] Perfil: {entry.display_name}")
    print(f"[TEST] URL de perfil derivada: {entry.profile_url}")
    payload = {"profileUrls": [entry.profile_url], "resultsLimit": POSTS_PER_PROFILE}
    print(f"[TEST] Payload enviado:\n{json.dumps(payload, indent=2, ensure_ascii=False)}\n")

    items = call_apify_actor(token=token, payload=payload)

    print("[TEST] ─── JSON crudo de Apify ───────────────────────────────────")
    print(json.dumps(items, indent=2, ensure_ascii=False))
    print("[TEST] ─────────────────────────────────────────────────────────────\n")

    posts = _posts_from_items(items, entry)
    if posts:
        print(f"[TEST] Posts extraídos ({len(posts)}):")
        for i, p in enumerate(posts, 1):
            print(f"  POST {i} [{p.date}] — {p.text[:80]}...")
    else:
        print("[TEST] ⚠ No se extrajeron posts. Revisá el JSON crudo de arriba y ajustá los field-keys si es necesario.")


# ---------------------------------------------------------------------------
# Full run
# ---------------------------------------------------------------------------

def run_full(token: str, entries: list[SourceEntry], output_dir: Path) -> None:
    """Process all profiles using the batch strategy + per-profile fallback."""

    # Step 1: single batch call for everyone.
    try:
        batch_results = batch_fetch_all(token=token, entries=entries)
    except RuntimeError as exc:
        print(f"[ERROR] Llamada batch falló: {exc}. Cambiando a modo individual.", flush=True)
        batch_results = {e.display_name: [] for e in entries}

    processed = 0
    failed = 0

    for entry in entries:
        posts = batch_results.get(entry.display_name, [])

        # Step 2: fallback only if batch returned nothing for this profile.
        if not posts:
            print(f"[FALLBACK] {entry.display_name} — sin resultados en batch, intentando llamada individual...", flush=True)
            try:
                posts = per_profile_fallback(token=token, entry=entry)
            except RuntimeError as exc:
                print(f"[ERROR] {entry.display_name}: {exc}", flush=True)
                failed += 1
                continue

        if not posts:
            print(f"[ERROR] {entry.display_name}: no se encontraron posts (perfil privado o sin actividad pública).", flush=True)
            failed += 1
            continue

        out = write_output(output_dir=output_dir, entry=entry, posts=posts)
        print(f"[OK] {entry.display_name} → {out.name}  ({len(posts)} posts)", flush=True)
        processed += 1

    print(f"\n{'─'*50}")
    print(f"Perfiles procesados correctamente : {processed}")
    print(f"Perfiles con error / sin posts    : {failed}")
    print(f"Archivos guardados en             : {output_dir}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extrae los 3 posts más recientes de perfiles LinkedIn via Apify.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--test-only",
        action="store_true",
        help="Corre solo la prueba con el primer perfil y muestra el JSON crudo. No guarda archivos.",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Procesar solo los primeros N perfiles (útil para debug).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    # Token must come from environment — never hardcode credentials.
    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not token:
        print("[FATAL] La variable de entorno APIFY_API_TOKEN no está definida.", file=sys.stderr)
        print("        Ejecutá:  $env:APIFY_API_TOKEN='apify_api_XXXX'  (PowerShell)", file=sys.stderr)
        return 1

    root = Path(__file__).resolve().parents[1]
    sources_path = root / "research" / "sources.md"
    output_dir = root / "research" / "linkedin-posts"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not sources_path.exists():
        print(f"[FATAL] No se encontró el archivo: {sources_path}", file=sys.stderr)
        return 1

    entries = parse_sources_md(sources_path)
    if args.limit is not None:
        entries = entries[: max(args.limit, 0)]

    if not entries:
        print("[FATAL] No se encontraron entradas válidas en research/sources.md", file=sys.stderr)
        return 1

    # Force UTF-8 on Windows consoles that default to cp1252.
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    print(f"[INFO] {len(entries)} perfiles cargados desde sources.md")
    for e in entries:
        print(f"  * {e.display_name:<20}  handle={e.handle}  ->  {e.profile_url}")

    if args.test_only:
        run_test(token=token, entry=entries[0])
        print("[INFO] Modo --test-only finalizado. Revisá el JSON crudo antes de correr sin ese flag.")
        return 0

    run_full(token=token, entries=entries, output_dir=output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
