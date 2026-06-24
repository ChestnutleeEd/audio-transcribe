from __future__ import annotations

import unittest

from app.services.polish_profiles import profile_options


class PolishProfilesTest(unittest.TestCase):
    def test_repair_profile_is_first_option(self) -> None:
        profiles = profile_options()

        self.assertEqual("repair", profiles[0].id)
        self.assertIn("文本修复", profiles[0].label)

    def test_repair_profile_removes_no_audio_placeholders(self) -> None:
        repair = profile_options()[0]

        self.assertIn("我没有收到任何音频", repair.default_prompt)
        self.assertIn("返回空文本", repair.default_prompt)


if __name__ == "__main__":
    unittest.main()
