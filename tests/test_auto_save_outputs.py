from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app, auto_save_output_files, build_output_files
from app.schemas import OutputFormat
from app.services.jobs import job_store


class AutoSaveOutputsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        with job_store._lock:
            self.previous_jobs = dict(job_store._jobs)
            job_store._jobs = {}

    def tearDown(self) -> None:
        with job_store._lock:
            job_store._jobs = self.previous_jobs

    def create_job(
        self,
        work_dir: Path,
        source_dir: Path | None,
        auto_save_outputs: bool,
        auto_save_dir: Path | None = None,
    ) -> None:
        job_store.create(
            "job-1",
            work_dir,
            "audio.wav",
            None,
            "auto",
            None,
            None,
            "large-v3",
            "large-v3",
            [OutputFormat.txt],
            True,
            source_dir=source_dir,
            auto_save_outputs=auto_save_outputs,
            auto_save_dir=auto_save_dir,
        )

    def test_auto_save_disabled_keeps_outputs_manual_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work_dir = root / "work"
            source_dir = root / "source"
            work_dir.mkdir()
            source_dir.mkdir()
            output_path = work_dir / "audio.txt"
            output_path.write_text("transcript", encoding="utf-8")
            self.create_job(work_dir, source_dir, auto_save_outputs=False)

            saved_paths = auto_save_output_files("job-1", [output_path])
            outputs = build_output_files("job-1", [output_path], saved_paths)

            self.assertEqual({}, saved_paths)
            self.assertIsNone(outputs[0].saved_path)
            self.assertFalse((source_dir / "转录结果").exists())

    def test_auto_save_without_custom_dir_uses_source_transcript_folder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work_dir = root / "work"
            source_dir = root / "source"
            work_dir.mkdir()
            source_dir.mkdir()
            output_path = work_dir / "audio.txt"
            output_path.write_text("transcript", encoding="utf-8")
            self.create_job(work_dir, source_dir, auto_save_outputs=True)

            saved_paths = auto_save_output_files("job-1", [output_path])

            target_path = source_dir / "转录结果" / output_path.name
            self.assertEqual(target_path, saved_paths[output_path.name])
            self.assertEqual("transcript", target_path.read_text(encoding="utf-8"))
            self.assertEqual(source_dir / "转录结果", job_store.get("job-1").auto_save_dir)

    def test_auto_save_with_custom_dir_uses_custom_dir(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work_dir = root / "work"
            source_dir = root / "source"
            custom_dir = root / "custom-output"
            work_dir.mkdir()
            source_dir.mkdir()
            output_path = work_dir / "audio.txt"
            output_path.write_text("transcript", encoding="utf-8")
            self.create_job(work_dir, source_dir, auto_save_outputs=True, auto_save_dir=custom_dir)

            saved_paths = auto_save_output_files("job-1", [output_path])

            target_path = custom_dir / output_path.name
            self.assertEqual(target_path, saved_paths[output_path.name])
            self.assertEqual("transcript", target_path.read_text(encoding="utf-8"))
            self.assertFalse((source_dir / "转录结果").exists())

    def test_url_auto_save_requires_custom_dir(self) -> None:
        response = self.client.post(
            "/api/jobs",
            data={
                "source_url": "https://example.com/video",
                "formats": "txt",
                "transcription_engine": "whisper",
                "whisper_model_id": "tiny",
                "auto_save_outputs": "true",
            },
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual("视频链接任务开启自动存储时，请先指定存储文件夹", response.json()["detail"])

    def test_media_output_directory_picker_accepts_post(self) -> None:
        with patch("app.main.pick_directory", return_value={"path": "/tmp/transcripts"}) as picker:
            response = self.client.post("/api/media/pick-directory")

        self.assertEqual(200, response.status_code)
        self.assertEqual({"path": "/tmp/transcripts"}, response.json())
        picker.assert_called_once_with("选择转录文件存储文件夹")


if __name__ == "__main__":
    unittest.main()
