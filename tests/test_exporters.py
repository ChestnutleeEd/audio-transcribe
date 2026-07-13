from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.services.exporters import MAX_FILENAME_PART_LENGTH, TranscriptSegment, export_srt, safe_filename_part


class ExportersTest(unittest.TestCase):
    def test_export_srt_writes_expected_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transcript.srt"

            export_srt(
                path,
                [
                    TranscriptSegment(start=0.0, end=1.25, text="第一段"),
                    TranscriptSegment(start=1.25, end=2.5, text="第二段"),
                ],
            )

            self.assertEqual(
                "1\n00:00:00,000 --> 00:00:01,250\n第一段\n\n"
                "2\n00:00:01,250 --> 00:00:02,500\n第二段\n\n",
                path.read_text(encoding="utf-8"),
            )

    def test_safe_filename_part_caps_long_values(self) -> None:
        value = safe_filename_part("a" * (MAX_FILENAME_PART_LENGTH + 50))

        self.assertEqual(MAX_FILENAME_PART_LENGTH, len(value))


if __name__ == "__main__":
    unittest.main()
