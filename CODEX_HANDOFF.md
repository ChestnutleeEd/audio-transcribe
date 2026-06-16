# Codex Handoff: audio-transcribe upgrade-codex

## Current branch
upgrade-codex

## Baseline status
- Project runs locally with FastAPI.
- Start command:
  .venv/bin/uvicorn app.main:app --reload
- Whisper-only real test passed:
  - file: test.m4a
  - Whisper model: small
  - duration: about 47s
  - status: completed
  - no server error

## Existing commits
- fix: update ctranslate2 version constraint
- feat: add explicit ollama transcription workflow
- chore: ignore macOS system files

## Product design
Two-axis design:
1. transcription_engine controls ASR only
   - whisper
   - ollama_audio
2. enable_polish / polish_model_id controls post-processing only

Rules:
- If user chooses Whisper, use Whisper for ASR.
- If user chooses Gemma direct audio, use Ollama direct audio.
- If Gemma direct audio fails, task fails. Do not fallback to Whisper.
- Polish is optional and independent.
- Polish failure should not fail the whole task. Return original transcription for failed polish parts.
- Preserve Whisper timestamps and export formats.

## Ollama models
- Main model target: gemma4:12b or gemma4:12b-it-qat
- Lightweight polish model: gemma3:1b
- gemma3:1b is installed and can return simple structured JSON with Ollama /api/generate format schema.
- gemma4 download is still in progress / unstable due to network.

## Current uncommitted Codex fix
Codex added batch polish:
- gemma3:1b default batch size = 5
- gemma4:12b default batch size = 10
- other models default batch size = 8
- env override: OLLAMA_POLISH_BATCH_SIZE
- batch failures keep original segments for that batch
- other batches continue
- final job remains completed

Changed files:
- README.md
- app/config.py
- app/main.py
- app/services/ollama_client.py
- app/services/ollama_provider.py

## Latest real test after batch polish
Test:
- Whisper small + gemma3:1b polish + test.m4a

Result:
- Task completed
- Export generated
- 17 polish batches
- 13 succeeded
- 4 failed

Failure examples:
- Polish batch failed: 1/17, segments 0-4, reason: Ollama polish 第 3 项时间戳被修改.
- Polish batch failed: 2/17, segments 5-9, reason: Ollama polish 第 3 项时间戳被修改.
- Polish batch failed: 6/17, segments 25-29, reason: Ollama polish 返回 segment 数量不一致.
- Polish batch failed: 17/17, segments 80-81, reason: Ollama polish 第 1 项时间戳被修改.

## Next fix needed
Only fix polish schema and validation.

Problem:
- Polish model should only modify text.
- The model should not be asked to return start/end.
- Asking small models to echo timestamps causes unnecessary failures.

Required change:
- Ollama polish structured output schema should return only:
  {
    "segments": [
      {"index": 0, "text": "..."}
    ]
  }
- Backend should preserve original start/end from input segments.
- Validation should check:
  - output segment count == input batch count
  - output index matches input index
  - text is non-empty string
- Do not validate start/end from model output because model should not return them.
- Prompt and few-shot should be updated:
  - input may contain index/start/end/text
  - output must contain only index/text
  - no markdown, no explanation
  - do not return start/end

Constraints:
- Do not change the two-axis design.
- Do not change transcription_engine logic.
- Do not add fallback from Gemma direct audio to Whisper.
- Do not break Whisper-only.
- Do not break txt/md/docx exports.
- Do not add new dependencies.

Validation:
- python -m compileall app
- node --check static/app.js
- Real test:
  - Whisper small + gemma3:1b polish + test.m4a
  - Expect no “时间戳被修改” warnings.
  - Some batch failures due to segment count are acceptable for now.
  - Task must complete and export files.
