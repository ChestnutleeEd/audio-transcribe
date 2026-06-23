from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.services.qwen_audio.qwen_infer import qwen_audio_model_supported


class QwenAudioModelSupportTest(unittest.TestCase):
    def test_local_qwen2_audio_config_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory)
            (model_dir / "config.json").write_text(json.dumps({"model_type": "qwen2_audio"}), encoding="utf-8")

            self.assertTrue(qwen_audio_model_supported(str(model_dir)))

    def test_local_gemma_config_is_not_supported_by_qwen_audio_stt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory)
            (model_dir / "config.json").write_text(json.dumps({"model_type": "gemma4"}), encoding="utf-8")

            self.assertFalse(qwen_audio_model_supported(str(model_dir)))


if __name__ == "__main__":
    unittest.main()
