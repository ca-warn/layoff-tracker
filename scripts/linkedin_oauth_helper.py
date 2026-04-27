#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from pathlib import Path
from urllib import error
from urllib import parse, request

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


DEFAULT_REDIRECT_URI = "https://oauth.pstmn.io/v1/callback"
DEFAULT_SCOPES = ["openid", "profile", "w_member_social"]


def env_first(*names: str) -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return ""


def require_client_id() -> str:
    value = env_first("LINKEDIN_CLIENT_ID", "CLIENT_ID")
    if not value:
        raise SystemExit("Missing client id. Set LINKEDIN_CLIENT_ID or CLIENT_ID.")
    return value


def require_client_secret() -> str:
    value = env_first("LINKEDIN_CLIENT_SECRET", "PRIMARY_CLIENT_SECRET")
    if not value:
        raise SystemExit("Missing client secret. Set LINKEDIN_CLIENT_SECRET or PRIMARY_CLIENT_SECRET.")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Helpers for LinkedIn OAuth setup.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_parser = subparsers.add_parser("authorize-url", help="Print a LinkedIn OAuth authorization URL.")
    auth_parser.add_argument("--redirect-uri", default=DEFAULT_REDIRECT_URI)
    auth_parser.add_argument("--state", default="", help="Optional explicit state value.")
    auth_parser.add_argument(
        "--scope",
        action="append",
        dest="scopes",
        help="Scope to request. Repeat for multiple scopes. Defaults to openid, profile, w_member_social.",
    )

    exchange_parser = subparsers.add_parser("exchange-code", help="Exchange an authorization code for an access token.")
    exchange_parser.add_argument("--code", required=True)
    exchange_parser.add_argument("--redirect-uri", default=DEFAULT_REDIRECT_URI)

    return parser


def authorize_url(redirect_uri: str, state: str, scopes: list[str]) -> dict[str, str]:
    client_id = require_client_id()
    actual_state = state or secrets.token_urlsafe(24)
    requested_scopes = scopes or DEFAULT_SCOPES
    query = parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": actual_state,
            "scope": " ".join(requested_scopes),
        }
    )
    url = f"https://www.linkedin.com/oauth/v2/authorization?{query}"
    return {"authorization_url": url, "state": actual_state}


def exchange_code(code: str, redirect_uri: str) -> dict[str, object]:
    client_id = require_client_id()
    client_secret = require_client_secret()
    payload = parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        }
    ).encode("utf-8")

    req = request.Request(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        message = [
            f"LinkedIn token exchange failed with HTTP {exc.code}.",
            f"Response body: {details or '<empty>'}",
            "",
            "Most common causes:",
            "- The authorization code was already used or expired.",
            "- The redirect URI does not exactly match the one used in the authorize step.",
            "- CLIENT_ID or PRIMARY_CLIENT_SECRET is incorrect for this app.",
        ]
        raise SystemExit("\n".join(message)) from exc


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "authorize-url":
        result = authorize_url(args.redirect_uri, args.state, args.scopes or [])
    elif args.command == "exchange-code":
        result = exchange_code(args.code, args.redirect_uri)
    else:
        raise SystemExit(f"Unknown command: {args.command}")

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
