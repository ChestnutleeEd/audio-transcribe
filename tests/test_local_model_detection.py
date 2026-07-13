from __future__ import annotations

import unittest
from unittest.mock import patch

from app.schemas import LocalModelProviderStatus
from app.services.local_model_detection import LocalModelProvider, detect_local_models


class LocalModelDetectionTest(unittest.TestCase):
    def test_detect_local_models_preserves_provider_order_and_isolates_errors(self) -> None:
        def ok(provider: LocalModelProvider) -> LocalModelProviderStatus:
            return LocalModelProviderStatus(
                id=provider.id,
                name=provider.name,
                type=provider.type,
                url=provider.url,
                online=True,
                message=f"{provider.name} online",
            )

        def broken(provider: LocalModelProvider) -> LocalModelProviderStatus:
            raise RuntimeError("boom")

        providers = [
            LocalModelProvider("first", "First", "custom", "http://first", ok),
            LocalModelProvider("second", "Second", "custom", "http://second", broken),
            LocalModelProvider("third", "Third", "custom", "http://third", ok),
        ]

        with patch("app.services.local_model_detection.provider_registry", return_value=providers):
            status = detect_local_models()

        self.assertEqual(["first", "second", "third"], [provider.id for provider in status.providers])
        self.assertEqual(3, status.providers_checked)
        self.assertEqual(2, status.providers_online)
        self.assertFalse(status.providers[1].online)
        self.assertIn("boom", status.providers[1].error or "")


if __name__ == "__main__":
    unittest.main()
