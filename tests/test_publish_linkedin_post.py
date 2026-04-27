from __future__ import annotations

import unittest

from scripts.publish_linkedin_post import is_inactive_version_error, linkedin_version_candidates


class PublishLinkedInPostTests(unittest.TestCase):
    def test_explicit_version_wins(self) -> None:
        self.assertEqual(linkedin_version_candidates("202604"), ["202604"])

    def test_version_fallback_includes_two_candidates(self) -> None:
        versions = linkedin_version_candidates("")
        self.assertGreaterEqual(len(versions), 1)
        self.assertRegex(versions[0], r"^\d{6}$")

    def test_inactive_version_detection(self) -> None:
        self.assertTrue(is_inactive_version_error("NONEXISTENT_VERSION: version is inactive"))
        self.assertFalse(is_inactive_version_error("some other error"))


if __name__ == "__main__":
    unittest.main()
