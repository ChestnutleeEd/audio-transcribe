from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import JobState, OutputFormat
from app.services.jobs import job_store


class JobRecordRoutesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        with job_store._lock:
            self.previous_jobs = dict(job_store._jobs)
            job_store._jobs = {}

    def tearDown(self) -> None:
        with job_store._lock:
            job_store._jobs = self.previous_jobs

    def test_delete_missing_history_record_is_idempotent(self) -> None:
        response = self.client.delete("/api/jobs/history/missing-job")

        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.json())

    def test_delete_terminal_history_record_removes_job(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            job_store.create(
                "completed-job",
                Path(directory),
                "audio.wav",
                None,
                "auto",
                None,
                None,
                "large-v3",
                "large-v3",
                [OutputFormat.txt],
                True,
            )
            job_store.update("completed-job", state=JobState.completed, progress=100)

            response = self.client.delete("/api/jobs/history/completed-job")

        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.json())
        self.assertIsNone(job_store.get("completed-job"))

    def test_delete_active_history_record_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            job_store.create(
                "queued-job",
                Path(directory),
                "audio.wav",
                None,
                "auto",
                None,
                None,
                "large-v3",
                "large-v3",
                [OutputFormat.txt],
                True,
            )

            response = self.client.delete("/api/jobs/history/queued-job")

        self.assertEqual(409, response.status_code)
        self.assertIsNotNone(job_store.get("queued-job"))


if __name__ == "__main__":
    unittest.main()
