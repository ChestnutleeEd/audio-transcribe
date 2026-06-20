from __future__ import annotations

from dataclasses import dataclass

from app.schemas import PolishProfile
from app.services.exporters import TranscriptSegment


@dataclass(frozen=True)
class PolishProfileDefinition:
    id: str
    label: str
    description: str
    instruction: str


POLISH_PROFILES: tuple[PolishProfileDefinition, ...] = (
    PolishProfileDefinition(
        id="punctuation",
        label="标点修复",
        description="只补标点和自然断句，尽量不改原文。",
        instruction=(
            "只补充标点、大小写、空格和自然断句。"
            "尽量保持原词、原语序和原语气，不删除信息，不总结，不翻译。"
        ),
    ),
    PolishProfileDefinition(
        id="conservative_cleanup",
        label="保守清理",
        description="去除明显口癖、重复和识别噪声，不改核心语义。",
        instruction=(
            "清理明显口癖、重复词、无意义填充词和识别噪声。"
            "不要改变事实、语气、人物关系和核心语义。不要扩写，不总结，不翻译。"
        ),
    ),
    PolishProfileDefinition(
        id="ja_natural_breaks",
        label="日语自然断句",
        description="适合日语新闻、访谈和视频字幕。",
        instruction=(
            "按日语新闻、访谈和字幕的阅读习惯补充标点与自然断句。"
            "保留日语原文，不翻译，不总结，不添加原文没有的信息。"
        ),
    ),
    PolishProfileDefinition(
        id="zh_meeting_minutes",
        label="中文会议纪要",
        description="把中文转录整理成结构化纪要。",
        instruction=(
            "在不改变事实的前提下，把中文转录整理为清晰的会议纪要表达。"
            "可使用简短标题、要点和行动项，但不要编造参会人、日期、结论或未出现的信息。"
            "如果输入不足以形成结构化内容，保持保守整理。"
        ),
    ),
    PolishProfileDefinition(
        id="bilingual_translation",
        label="双语翻译",
        description="保留原文，并补充中文或英文翻译。",
        instruction=(
            "保留原文含义并补充翻译。"
            "如果原文主要是中文，给出英文翻译；否则给出中文翻译。"
            "每段输出应同时包含原文整理版和译文，避免总结和扩写。"
        ),
    ),
)


def profile_options() -> list[PolishProfile]:
    return [
        PolishProfile(
            id=item.id,
            label=item.label,
            description=item.description,
            prompt_preview=item.instruction,
        )
        for item in POLISH_PROFILES
    ]


def get_profile(profile_id: str | None) -> PolishProfileDefinition:
    selected = profile_id or POLISH_PROFILES[0].id
    for profile in POLISH_PROFILES:
        if profile.id == selected:
            return profile
    return POLISH_PROFILES[0]


def build_profile_prompt(profile: PolishProfileDefinition, segments: list[TranscriptSegment]) -> str:
    from app.services.ollama_provider import build_polish_prompt

    return build_polish_prompt(segments, profile.instruction)


def combine_instruction(profile: PolishProfileDefinition, custom_instruction: str | None) -> str:
    custom = (custom_instruction or "").strip()
    if not custom:
        return profile.instruction
    return f"{profile.instruction}\n追加用户指令：{custom}"
