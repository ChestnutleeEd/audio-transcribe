from __future__ import annotations

import unittest

from app.services.model_registry import capabilities_for_name


class ModelRegistryCapabilitiesTest(unittest.TestCase):
    def test_mlx_gemma4_supports_audio_and_text(self) -> None:
        capabilities = capabilities_for_name("gemma4-e4b-qat-4bit", "mlx")

        self.assertTrue(capabilities.audio)
        self.assertTrue(capabilities.text)

    def test_mlx_qwen2_audio_supports_audio_and_text(self) -> None:
        capabilities = capabilities_for_name("Qwen2-Audio-7B-Instruct-4bit", "mlx")

        self.assertTrue(capabilities.audio)
        self.assertTrue(capabilities.text)


if __name__ == "__main__":
    unittest.main()
