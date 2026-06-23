from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.main import route_transcription_engine
from app.schemas import TranscriptionEngine


class TranscriptionEngineRoutingTest(unittest.TestCase):
    def test_gemma4_model_submitted_as_qwen_routes_to_mlx_vlm_audio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory)
            (model_dir / "config.json").write_text(json.dumps({"model_type": "gemma4"}), encoding="utf-8")

            engine = route_transcription_engine(TranscriptionEngine.qwen_audio, str(model_dir))

        self.assertEqual(TranscriptionEngine.mlx_vlm_audio, engine)

    def test_qwen2_audio_model_stays_on_qwen_audio(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory)
            (model_dir / "config.json").write_text(json.dumps({"model_type": "qwen2_audio"}), encoding="utf-8")

            engine = route_transcription_engine(TranscriptionEngine.qwen_audio, str(model_dir))

        self.assertEqual(TranscriptionEngine.qwen_audio, engine)


if __name__ == "__main__":
    unittest.main()
