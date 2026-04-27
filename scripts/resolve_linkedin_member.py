#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib import error, request

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()
    if not token:
        raise SystemExit("Missing required environment variable: LINKEDIN_ACCESS_TOKEN")

    req = request.Request(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )

    try:
        with request.urlopen(req) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise SystemExit(f"LinkedIn userinfo request failed with {exc.code}: {exc.read().decode('utf-8', errors='replace')}") from exc

    member_id = str(payload.get("sub", "")).strip()
    if not member_id:
        raise SystemExit("LinkedIn userinfo response did not include `sub`.")

    author_urn = f"urn:li:person:{member_id}"
    print(json.dumps({"author_urn": author_urn, "profile": payload}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
