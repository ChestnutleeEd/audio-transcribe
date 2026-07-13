from __future__ import annotations

import unittest
from unittest.mock import patch

from app.config import SUPPORTED_MODELS
from app.services import model_manager


class ModelManagerStatusTest(unittest.TestCase):
    def test_model_status_reuses_resolved_model_paths_for_options(self) -> None:
        with patch.object(model_manager, "resolve_model_path", return_value=None) as resolver:
            status = model_manager.model_status()

        self.assertEqual(len(SUPPORTED_MODELS), resolver.call_count)
        self.assertEqual(len(SUPPORTED_MODELS), len(status.models))


if __name__ == "__main__":
    unittest.main()
