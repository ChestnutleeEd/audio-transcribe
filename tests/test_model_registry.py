from __future__ import annotations

import unittest
from unittest.mock import patch

from app.schemas import AudioModelTestRequest, ModelCapabilities
from app.services import model_registry as registry_module
from app.services.model_registry import capabilities_for_name, model_registry, test_audio_model as run_audio_model_test, unified_model


class ModelRegistryCapabilitiesTest(unittest.TestCase):
    def tearDown(self) -> None:
        registry_module.invalidate_model_registry_cache()

    def test_mlx_gemma4_supports_audio_and_text(self) -> None:
        capabilities = capabilities_for_name("gemma4-e4b-qat-4bit", "mlx")

        self.assertTrue(capabilities.audio)
        self.assertTrue(capabilities.text)

    def test_mlx_qwen2_audio_supports_audio_and_text(self) -> None:
        capabilities = capabilities_for_name("Qwen2-Audio-7B-Instruct-4bit", "mlx")

        self.assertTrue(capabilities.audio)
        self.assertTrue(capabilities.text)

    def test_model_registry_reuses_short_lived_cache(self) -> None:
        model = unified_model(
            name="Qwen2-Audio",
            provider="mlx",
            path_or_id="/models/qwen2-audio",
            capabilities=ModelCapabilities(audio=True, text=True),
        )
        with patch.object(registry_module, "_run_registry_detectors", return_value=([model], [])) as detectors:
            first = model_registry(force_refresh=True)
            second = model_registry()

        self.assertIs(first, second)
        self.assertEqual(1, detectors.call_count)

    def test_audio_model_test_force_refreshes_registry(self) -> None:
        model = unified_model(
            name="Qwen2-Audio",
            provider="mlx",
            path_or_id="/models/qwen2-audio",
            capabilities=ModelCapabilities(audio=True, text=True),
        )
        request = AudioModelTestRequest(model_id=model.id, provider="mlx", path_or_id=model.path_or_id)
        with patch.object(registry_module, "_run_registry_detectors", return_value=([model], [])) as detectors:
            result = run_audio_model_test(request)

        self.assertTrue(result.success)
        self.assertEqual(1, detectors.call_count)

    def test_model_registry_keeps_partial_results_when_detector_raises(self) -> None:
        model = unified_model(
            name="Qwen2-Audio",
            provider="mlx",
            path_or_id="/models/qwen2-audio",
            capabilities=ModelCapabilities(audio=True, text=True),
        )
        with (
            patch.object(registry_module, "discover_ollama", side_effect=RuntimeError("boom")),
            patch.object(registry_module, "discover_mlx", return_value=([model], [])),
            patch.object(registry_module, "discover_huggingface_cache", return_value=([], [])),
            patch.object(registry_module, "discover_llamacpp", return_value=([], [])),
            patch.object(registry_module, "discover_custom", return_value=([], [])),
        ):
            status = model_registry(force_refresh=True)

        self.assertEqual([model.id], [item.id for item in status.models])
        self.assertTrue(any("boom" in error for error in status.errors))


if __name__ == "__main__":
    unittest.main()
