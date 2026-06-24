from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services.exporters import TranscriptSegment
from app.services.mlx_vlm_polish import generate_text, polish_segments_with_mlx_vlm
from app.services.polish_router import PolishModelRef, polish_segments, validate_polish_model


class MLXVlmPolishTest(unittest.TestCase):
    def test_generate_text_uses_text_only_mlx_vlm_generate(self) -> None:
        commands = []

        class CompletedProcess:
            returncode = 0

            def poll(self):
                return 0

            def communicate(self, timeout=None):
                del timeout
                return ('{"segments":[{"index":0,"text":"整理后文本。"}]}', "")

        def popen(command, **kwargs):
            del kwargs
            commands.append(command)
            return CompletedProcess()

        with patch("app.services.mlx_vlm_polish.subprocess.Popen", side_effect=popen):
            text = generate_text("/models/gemma4", "整理这段文本", "python")

        self.assertEqual('{"segments":[{"index":0,"text":"整理后文本。"}]}', text)
        self.assertIn("mlx_vlm.generate", commands[0])
        self.assertIn("--prompt", commands[0])
        self.assertNotIn("--audio", commands[0])
        self.assertIn("--no-verbose", commands[0])

    def test_polish_segments_with_mlx_vlm_parses_json_response(self) -> None:
        segments = [TranscriptSegment(start=0.0, end=1.0, text="原始文本")]
        events = []

        with (
            patch("app.services.mlx_vlm_polish.mlx_vlm_audio_status") as status_mock,
            patch("app.services.mlx_vlm_polish.generate_text") as generate_mock,
        ):
            status_mock.return_value.available = True
            status_mock.return_value.python_executable = "python"
            generate_mock.return_value = json.dumps(
                {"segments": [{"index": 0, "text": "整理后文本。"}]},
                ensure_ascii=False,
            )

            result = polish_segments_with_mlx_vlm(
                segments,
                "/models/gemma4",
                "修正标点",
                on_event=lambda message, level="info": events.append((message, level)),
            )

        self.assertTrue(result.success)
        self.assertEqual([TranscriptSegment(start=0.0, end=1.0, text="整理后文本。")], result.segments)
        self.assertEqual(1, result.success_batches)
        self.assertTrue(any("MLX VLM 文本整理分批完成" in message for message, _level in events))

    def test_polish_router_accepts_local_gemma4_mlx_model(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            model_dir = Path(directory)
            (model_dir / "config.json").write_text(json.dumps({"model_type": "gemma4"}), encoding="utf-8")
            model_ref = PolishModelRef(
                provider="mlx",
                model_id=f"mlx:{model_dir}",
                path_or_id=str(model_dir),
            )
            segments = [TranscriptSegment(start=0.0, end=1.0, text="原始文本")]

            with (
                patch("app.services.polish_router.mlx_vlm_audio_status") as status_mock,
                patch("app.services.polish_router.polish_segments_with_mlx_vlm") as polish_mock,
            ):
                status_mock.return_value.available = True
                polish_mock.return_value.success = True
                polish_mock.return_value.segments = [TranscriptSegment(start=0.0, end=1.0, text="整理后文本。")]
                polish_mock.return_value.warnings = []
                polish_mock.return_value.success_batches = 1
                polish_mock.return_value.failed_batches = 0

                validate_polish_model(model_ref)
                result = polish_segments(segments, model_ref, "修正标点")

        self.assertTrue(result.success)
        self.assertEqual("整理后文本。", result.segments[0].text)
        polish_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
