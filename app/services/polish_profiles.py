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
    PolishProfileDefinition(
        id="repair",
        label="Repair / 文本修复",
        description="自动清理噪声 + 修正错误转录。",
        instruction=(
            "执行语义修复：删除无意义内容、明显口误和识别噪声，修正错别字、听错词和明显 ASR 错误。"
            "优化句子连贯性，但不得编造事实、人物、日期、数字或原文没有的信息。"
            "不总结，不扩写，不改变说话者意图。"
        ),
    ),
    PolishProfileDefinition(
        id="speaker_diarization",
        label="说话人识别",
        description="根据分段时间、问答关系和语言逻辑，为文本补充统一说话人标签。",
        instruction=(
            "执行说话人识别和轻度文本整理。根据每段 start/end 时间、停顿、问答关系、称谓、语气、话题延续和上下文逻辑，"
            "推断同一说话人的连续发言，并给每段文本添加统一说话人前缀。"
            "说话人命名必须使用“说话人 1：”“说话人 2：”“说话人 3：”这种格式，从 1 开始连续编号。"
            "同一位说话人在全文中必须保持同一个编号；不能使用主持人、嘉宾、客户、Speaker A 等其他命名。"
            "如果无法可靠区分新说话人，沿用最可能的上一位说话人；不要编造姓名、身份、职位或未出现的信息。"
            "可补充必要标点和自然断句，但不要总结、翻译、合并 segments 或新增 segments。"
        ),
    ),
)


def profile_options() -> list[PolishProfile]:
    return [
        PolishProfile(
            id=item.id,
            label=item.label,
            description=item.description,
            default_prompt=item.instruction,
            prompt_preview=item.instruction,
        )
        for item in POLISH_PROFILES
    ]


def get_profile(profile_id: str | None) -> PolishProfileDefinition:
    selected = profile_id or POLISH_PROFILES[0].id
    if selected == "repair_mode":
        selected = "repair"
    for profile in POLISH_PROFILES:
        if profile.id == selected:
            return profile
    return POLISH_PROFILES[0]


def get_profiles(profile_ids: str | None) -> list[PolishProfileDefinition]:
    selected_ids = [
        item.strip()
        for item in (profile_ids or POLISH_PROFILES[0].id).split(",")
        if item.strip()
    ]
    profiles: list[PolishProfileDefinition] = []
    seen: set[str] = set()
    for profile_id in selected_ids:
        profile = get_profile(profile_id)
        if profile.id not in seen:
            profiles.append(profile)
            seen.add(profile.id)
    return profiles or [POLISH_PROFILES[0]]


def build_profile_prompt(profile: PolishProfileDefinition, segments: list[TranscriptSegment]) -> str:
    from app.services.ollama_provider import build_polish_prompt

    return build_polish_prompt(segments, profile.instruction)


def combine_instruction(profile: PolishProfileDefinition, custom_instruction: str | None) -> str:
    custom = (custom_instruction or "").strip()
    if not custom:
        return profile.instruction
    override_marker = "__OVERRIDE_PROMPT__"
    if custom.startswith(override_marker):
        return custom.removeprefix(override_marker).strip() or profile.instruction
    return f"{profile.instruction}\n追加用户指令：{custom}"


def combine_profiles_instruction(profiles: list[PolishProfileDefinition], custom_instruction: str | None) -> str:
    if len(profiles) <= 1:
        return combine_instruction(profiles[0], custom_instruction)
    custom = (custom_instruction or "").strip()
    override_marker = "__OVERRIDE_PROMPT__"
    if custom.startswith(override_marker):
        return custom.removeprefix(override_marker).strip() or profiles[0].instruction
    base = "\n\n".join(f"{index}. {profile.label}\n{profile.instruction}" for index, profile in enumerate(profiles, start=1))
    if not custom:
        return base
    return f"{base}\n追加用户指令：{custom}"
