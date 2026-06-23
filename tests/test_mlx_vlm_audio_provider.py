from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.exporters import TranscriptSegment
from app.services.mlx_vlm_audio_provider import (
    clean_transcript_text,
    is_mlx_vlm_audio_model,
    mlx_vlm_audio_status,
    parse_mlx_vlm_generate_output,
    transcribe_with_mlx_vlm_audio,
)


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

    def test_gemma4_path_is_mlx_vlm_audio_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory)
            (model_dir / "config.json").write_text(json.dumps({"model_type": "gemma4"}), encoding="utf-8")

            self.assertTrue(is_mlx_vlm_audio_model(str(model_dir)))

    def test_clean_transcript_text_converts_common_traditional_chinese(self) -> None:
        self.assertEqual("这是测试内容。", clean_transcript_text("「這是測試內容。」"))

    def test_transcribe_with_mlx_vlm_audio_uses_chunked_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audio_path = root / "input.wav"
            audio_path.write_bytes(b"fake")
            model_dir = root / "gemma"
            model_dir.mkdir()
            (model_dir / "config.json").write_text(json.dumps({"model_type": "gemma4"}), encoding="utf-8")
            partials = []

            with (
                patch("app.services.mlx_vlm_audio_provider.mlx_vlm_audio_status") as status_mock,
                patch("app.services.mlx_vlm_audio_provider.audio_duration_seconds", return_value=40.0),
                patch("app.services.chunked_audio.prepare_audio_chunks") as chunks_mock,
                patch("app.services.mlx_vlm_audio_provider._run_mlx_vlm_generate") as infer_mock,
            ):
                status_mock.return_value.available = True
                status_mock.return_value.python_executable = "python"
                chunks_mock.return_value = [
                    {"chunk_id": 1, "start": 0.0, "end": 20.0, "audio_path": str(root / "chunk_1.wav")},
                    {"chunk_id": 2, "start": 19.0, "end": 40.0, "audio_path": str(root / "chunk_2.wav")},
                ]
                infer_mock.side_effect = ["第一段内容", "第二段内容"]

                result = transcribe_with_mlx_vlm_audio(
                    audio_path,
                    str(model_dir),
                    work_dir=root / "work",
                    on_partial=partials.append,
                )

            self.assertEqual([TranscriptSegment(start=0.0, end=20.0, text="第一段内容"), TranscriptSegment(start=20.0, end=40.0, text="第二段内容")], result.segments)
            self.assertEqual("第一段内容\n\n第二段内容", result.raw_text)
            self.assertEqual(2, len(partials))
            self.assertEqual("mlx_vlm_audio", chunks_mock.call_args.kwargs["namespace"])
            self.assertEqual(2, len(result.metadata["partial_results"]))


if __name__ == "__main__":
    unittest.main()
