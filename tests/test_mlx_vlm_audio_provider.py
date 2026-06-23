from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.mlx_vlm_audio_provider import mlx_vlm_audio_status, parse_mlx_vlm_generate_output


class MLXVlmAudioProviderTest(unittest.TestCase):
    def test_parse_generate_output_extracts_model_text(self) -> None:
        stdout = """==========
Files: ['/tmp/audio.wav']

Prompt: <bos><|turn>user
请准确转写这段音频，只输出转写文本。<|audio|><turn|>
<|turn>model

这是转写文本。
==========
Prompt: 10 tokens
Generation: 4 tokens
"""

        self.assertEqual("这是转写文本。", parse_mlx_vlm_generate_output(stdout))

    def test_status_accepts_local_gemma4_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory)
            (model_dir / "config.json").write_text(json.dumps({"model_type": "gemma4"}), encoding="utf-8")

            with (
                patch("app.services.mlx_vlm_audio_provider.python_available", return_value=True),
                patch("app.services.mlx_vlm_audio_provider.dependency_available", return_value=True),
                patch("app.services.mlx_vlm_audio_provider.ffmpeg_available", return_value=True),
                patch("app.services.mlx_vlm_audio_provider.is_macos", return_value=True),
                patch("app.services.mlx_vlm_audio_provider.is_apple_silicon", return_value=True),
            ):
                status = mlx_vlm_audio_status(str(model_dir))

        self.assertTrue(status.available)
        self.assertEqual("gemma4", status.model_type)


if __name__ == "__main__":
    unittest.main()
