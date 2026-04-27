#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.lib.linkedin_posts import (  # noqa: E402
    archive_key_for_date,
    existing_archive_index,
    load_warn_rows,
    select_post,
    write_post_archive,
)

DEFAULT_WORKBOOK = REPO_ROOT / "data" / "warn_report.xlsx"
DEFAULT_ARCHIVE_ROOT = REPO_ROOT / "social" / "linkedin-posts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic LinkedIn post archive from California WARN data."
    )
    parser.add_argument("--date", default=date.today().isoformat(), help="Publish date in YYYY-MM-DD format.")
    parser.add_argument(
        "--workbook",
        default=str(DEFAULT_WORKBOOK),
        help="Path to the WARN workbook.",
    )
    parser.add_argument(
        "--archive-root",
        default=str(DEFAULT_ARCHIVE_ROOT),
        help="Directory where dated LinkedIn post archives are stored.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting an existing archive for the requested date.",
    )
    return parser.parse_args()


def set_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def main() -> int:
    args = parse_args()
    publish_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    workbook_path = Path(args.workbook).resolve()
    archive_root = Path(args.archive_root).resolve()

    rows = load_warn_rows(workbook_path)
    if not rows:
        raise SystemExit("No valid WARN rows were parsed from the workbook.")

    archive_index = existing_archive_index(archive_root)
    archive_key = archive_key_for_date(publish_date)

    if not args.force and archive_key in archive_index["archive_keys"]:
        print(f"Archive {archive_key} already exists. Skipping generation.")
        set_output("status", "exists")
        set_output("archive_key", archive_key)
        return 0

    candidate = select_post(rows, publish_date, archive_index["fingerprints"])
    if candidate is None:
        print("No new unique LinkedIn post candidate is available from the current workbook.")
        set_output("status", "skipped")
        set_output("archive_key", "")
        return 0

    archive_key, output_dir = write_post_archive(
        archive_root=archive_root,
        publish_date=publish_date,
        workbook_path=workbook_path.relative_to(REPO_ROOT),
        rows=rows,
        candidate=candidate,
    )

    print(f"Created LinkedIn post archive {archive_key} at {output_dir}.")
    print(candidate["linkedin"])
    set_output("status", "created")
    set_output("archive_key", archive_key)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
