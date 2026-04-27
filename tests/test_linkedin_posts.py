from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.lib.linkedin_posts import WarnRow, existing_archive_index, select_post, write_post_archive


def make_row(
    *,
    company: str,
    county: str,
    effective_date: date,
    employees: int,
    address: str,
    industry: str = "Technology",
) -> WarnRow:
    return WarnRow(
        county=county,
        county_normalized=county.replace(" County", ""),
        notice_date=None,
        processed_date=None,
        effective_date=effective_date,
        company=company,
        layoff_closure="Layoff Permanent",
        employees=employees,
        address=address,
        industry=industry,
    )


class LinkedInPostSelectionTests(unittest.TestCase):
    def test_selects_earliest_upcoming_event_first(self) -> None:
        rows = [
            make_row(
                company="Later Co",
                county="Alameda County",
                effective_date=date(2026, 5, 5),
                employees=10,
                address="1 Later St",
            ),
            make_row(
                company="Soon Co",
                county="Los Angeles County",
                effective_date=date(2026, 4, 28),
                employees=25,
                address="2 Soon St",
            ),
        ]

        candidate = select_post(rows, date(2026, 4, 27), set())

        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate["post_type"], "next_event")
        self.assertEqual(candidate["event"]["company"], "Soon Co")

    def test_skips_duplicate_event_and_uses_distinct_location(self) -> None:
        rows = [
            make_row(
                company="Riot Games",
                county="Los Angeles County",
                effective_date=date(2026, 4, 27),
                employees=26,
                address="123 Main St",
            ),
            make_row(
                company="Riot Games",
                county="Los Angeles County",
                effective_date=date(2026, 4, 27),
                employees=18,
                address="456 Second St",
            ),
        ]

        first = select_post(rows, date(2026, 4, 27), set())
        self.assertIsNotNone(first)
        assert first is not None

        second = select_post(rows, date(2026, 4, 27), {first["fingerprint"]})
        self.assertIsNotNone(second)
        assert second is not None
        self.assertEqual(second["post_type"], "next_event")
        self.assertEqual(second["event"]["address"], "456 Second St")

    def test_falls_back_to_summary_when_upcoming_events_are_exhausted(self) -> None:
        rows = [
            make_row(
                company="Riot Games",
                county="Los Angeles County",
                effective_date=date(2026, 4, 27),
                employees=26,
                address="123 Main St",
            )
        ]

        first = select_post(rows, date(2026, 4, 27), set())
        self.assertIsNotNone(first)
        assert first is not None

        second = select_post(rows, date(2026, 4, 27), {first["fingerprint"]})
        self.assertIsNotNone(second)
        assert second is not None
        self.assertIn(second["post_type"], {"next_day_summary", "total_layoffs", "county_impact"})

    def test_existing_archive_index_reads_fingerprint(self) -> None:
        rows = [
            make_row(
                company="Riot Games",
                county="Los Angeles County",
                effective_date=date(2026, 4, 27),
                employees=26,
                address="123 Main St",
            )
        ]
        candidate = select_post(rows, date(2026, 4, 27), set())
        self.assertIsNotNone(candidate)
        assert candidate is not None

        with tempfile.TemporaryDirectory() as tempdir:
            archive_root = Path(tempdir)
            write_post_archive(
                archive_root=archive_root,
                publish_date=date(2026, 4, 27),
                workbook_path=Path("data/warn_report.xlsx"),
                rows=rows,
                candidate=candidate,
            )

            archive_index = existing_archive_index(archive_root)
            self.assertIn(candidate["fingerprint"], archive_index["fingerprints"])
            self.assertIn("2026-04-27", archive_index["archive_keys"])


if __name__ == "__main__":
    unittest.main()
