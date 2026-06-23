from __future__ import annotations

import unittest

from app.main import diagnose_error


class ErrorDiagnosticTest(unittest.TestCase):
    def test_gemma_stt_error_is_classified_as_unsupported_audio_model(self) -> None:
        diagnostic = diagnose_error("Model type gemma4 not supported for stt.")

        self.assertEqual("AUDIO_MODEL_UNSUPPORTED", diagnostic.code)

    def test_mlx_audio_stt_error_is_classified_as_unsupported_audio_model(self) -> None:
        diagnostic = diagnose_error("当前 MLX Audio STT 后端不支持 gemma4 模型。")

        self.assertEqual("AUDIO_MODEL_UNSUPPORTED", diagnostic.code)

    def test_mlx_vlm_error_is_classified(self) -> None:
        diagnostic = diagnose_error("Gemma4 MLX VLM Audio 转录失败：missing dependency")

        self.assertEqual("MLX_VLM_AUDIO_UNAVAILABLE", diagnostic.code)


if __name__ == "__main__":
    unittest.main()
