from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.schemas import OutputFormat


@dataclass(frozen=True)
class TranscriptSegment:
    start: float
    end: float
    text: str


def format_timestamp(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def timed_line(segment: TranscriptSegment) -> str:
    return f"[{format_timestamp(segment.start)} -> {format_timestamp(segment.end)}] {segment.text}"


def export_txt(path: Path, segments: list[TranscriptSegment], include_timestamps: bool) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for segment in segments:
            handle.write((timed_line(segment) if include_timestamps else segment.text) + "\n\n")


def export_md(path: Path, title: str, segments: list[TranscriptSegment], include_timestamps: bool) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write(f"# {title}\n\n")
        for segment in segments:
            if include_timestamps:
                handle.write(f"- **{format_timestamp(segment.start)} -> {format_timestamp(segment.end)}** {segment.text}\n")
            else:
                handle.write(segment.text + "\n\n")


def export_docx(path: Path, title: str, segments: list[TranscriptSegment], include_timestamps: bool) -> None:
    from docx import Document

    doc = Document()
    doc.add_heading(title, 0)
    for segment in segments:
        paragraph = doc.add_paragraph()
        if include_timestamps:
            run = paragraph.add_run(f"[{format_timestamp(segment.start)} -> {format_timestamp(segment.end)}] ")
            run.bold = True
        paragraph.add_run(segment.text)
    doc.save(path)


def export_transcript(
    output_dir: Path,
    base_name: str,
    formats: list[OutputFormat],
    segments: list[TranscriptSegment],
    include_timestamps: bool,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    title = f"{base_name} 转录结果"
    writers = {
        OutputFormat.txt: lambda path: export_txt(path, segments, include_timestamps),
        OutputFormat.md: lambda path: export_md(path, title, segments, include_timestamps),
        OutputFormat.docx: lambda path: export_docx(path, title, segments, include_timestamps),
    }

    paths: list[Path] = []
    suffix = "timed" if include_timestamps else "plain"
    for fmt in formats:
        path = output_dir / f"{base_name}_{suffix}.{fmt.value}"
        writers[fmt](path)
        paths.append(path)
    return paths
