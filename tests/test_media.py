from __future__ import annotations

import sys
import unittest

from app.services.media import MAX_SAFE_STEM_LENGTH, OperationCanceled, run_command_with_env, safe_stem


class MediaCommandTest(unittest.TestCase):
    def test_run_command_with_env_raises_on_timeout(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "下载超时"):
            run_command_with_env(
                [sys.executable, "-c", "import time; time.sleep(5)"],
                is_canceled=lambda: False,
                timeout_seconds=0.01,
            )

    def test_run_command_with_env_raises_on_cancel(self) -> None:
        with self.assertRaisesRegex(OperationCanceled, "任务已停止"):
            run_command_with_env(
                [sys.executable, "-c", "import time; time.sleep(5)"],
                is_canceled=lambda: True,
            )

    def test_safe_stem_caps_long_values(self) -> None:
        value = safe_stem(f"{'a' * (MAX_SAFE_STEM_LENGTH + 50)}.wav")

        self.assertEqual(MAX_SAFE_STEM_LENGTH, len(value))


if __name__ == "__main__":
    unittest.main()
