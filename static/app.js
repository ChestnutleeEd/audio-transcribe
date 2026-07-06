const form = document.querySelector("#job-form");
const resetButton = document.querySelector("#reset-button");
const fileInput = document.querySelector("#file-input");
const fileLabel = document.querySelector("#file-label");
const sourcePathInput = document.querySelector("#source-path-input");
const sourcePathLabel = document.querySelector("#source-path-label");
const pickSourceFileButton = document.querySelector("#pick-source-file-button");
const autoSaveOutputsInput = document.querySelector("#auto-save-outputs");
const submitButton = form.querySelector(".primary");
const startTimeInput = form.querySelector('input[name="start_time"]');
const endTimeInput = form.querySelector('input[name="end_time"]');
const jobsList = document.querySelector("#jobs-list");
const jobSummary = document.querySelector("#job-summary");
const jobCountTotal = document.querySelector("#job-count-total");
const jobCountActive = document.querySelector("#job-count-active");
const jobCountCompleted = document.querySelector("#job-count-completed");
const jobCountFailed = document.querySelector("#job-count-failed");
const jobsRefreshButton = document.querySelector("#jobs-refresh-button");
const jobsCleanupButton = document.querySelector("#jobs-cleanup-button");
const jobsCleanupStatus = document.querySelector("#jobs-cleanup-status");
const jobsNavButton = document.querySelector('[data-side-view="jobs"]');
const headerOpenJobsButton = document.querySelector("#header-open-jobs-button");
const modelSelect = document.querySelector("#model-select");
const modelMessage = document.querySelector("#model-message");
const modelDevice = document.querySelector("#model-device");
const modelPath = document.querySelector("#model-path");
const whisperModelPath = document.querySelector("#whisper-model-path");
const pickWhisperModelFolderButton = document.querySelector("#pick-whisper-model-folder-button");
const bindWhisperModelPathButton = document.querySelector("#bind-whisper-model-path-button");
const unbindWhisperModelPathButton = document.querySelector("#unbind-whisper-model-path-button");
const whisperModelPathMessage = document.querySelector("#whisper-model-path-message");
const modelDownloadButton = document.querySelector("#model-download-button");
const modelDownloadLabel = document.querySelector("#model-download-label");
const modelCancelButton = document.querySelector("#model-cancel-button");
const modelCancelLabel = document.querySelector("#model-cancel-label");
const modelProgress = document.querySelector("#model-progress");
const modelProgressFill = document.querySelector("#model-progress-fill");
const modelProgressLabel = document.querySelector("#model-progress-label");
const modelRefreshButton = document.querySelector("#model-refresh-button");
const modelRefreshLabel = document.querySelector("#model-refresh-label");
const modelInfoButton = document.querySelector("#model-info-button");
const modelInfoPopover = document.querySelector("#model-info-popover");
const modelDescription = document.querySelector("#model-description");
const mockBanner = document.querySelector("#mock-banner");
const enablePolishInput = document.querySelector("#enable-polish");
const polishModelSelect = document.querySelector("#polish-model-select");
const polishField = document.querySelector("#polish-field");
const localModelTools = document.querySelector("#local-model-tools");
const localModelDetectButton = document.querySelector("#local-model-detect-button");
const localModelDetectLabel = document.querySelector("#local-model-detect-label");
const localProviderSelect = document.querySelector("#local-provider-select");
const localModelSelect = document.querySelector("#local-model-select");
const localModelMessage = document.querySelector("#local-model-message");
const localModelResults = document.querySelector("#local-model-results");
const polishProfileField = document.querySelector("#polish-profile-field");
const polishProfileSelect = document.querySelector("#polish-profile-select");
const polishProfileList = document.querySelector("#polish-profile-list");
const polishProfileDescription = document.querySelector("#polish-profile-description");
const polishCustomInstruction = document.querySelector("#polish-custom-instruction");
const clearPolishCustomButton = document.querySelector("#clear-polish-custom-button");
const promptPreviewText = document.querySelector("#prompt-preview-text");
const srtFormatInput = document.querySelector("#srt-format");
const includeTimestampsInput = form.querySelector('input[name="include_timestamps"]');
const ollamaMessage = document.querySelector("#ollama-message");
const ollamaServicePill = document.querySelector("#ollama-service-pill");
const ollamaTranscriptionModelSelect = document.querySelector("#ollama-transcription-model-select");
const ollamaManagedModelSelect = document.querySelector("#ollama-managed-model-select");
const ollamaRefreshButton = document.querySelector("#ollama-refresh-button");
const ollamaRefreshLabel = document.querySelector("#ollama-refresh-label");
const ollamaDownloadButton = document.querySelector("#ollama-download-button");
const ollamaDownloadLabel = document.querySelector("#ollama-download-label");
const ollamaCancelButton = document.querySelector("#ollama-cancel-button");
const ollamaCancelLabel = document.querySelector("#ollama-cancel-label");
const ollamaModelPath = document.querySelector("#ollama-model-path");
const ollamaProgress = document.querySelector("#ollama-progress");
const ollamaProgressFill = document.querySelector("#ollama-progress-fill");
const ollamaProgressLabel = document.querySelector("#ollama-progress-label");
const loadedModelSummary = document.querySelector("#loaded-model-summary");
const loadedAudioCount = document.querySelector("#loaded-audio-count");
const loadedTextCount = document.querySelector("#loaded-text-count");
const ollamaLocalCount = document.querySelector("#ollama-local-count");
const localModelInventory = document.querySelector("#local-model-inventory");
const healthMessage = document.querySelector("#health-message");
const healthList = document.querySelector("#health-list");
const healthRefreshButton = document.querySelector("#health-refresh-button");
const healthRefreshLabel = document.querySelector("#health-refresh-label");
const diagnosticCard = document.querySelector("#diagnostic-card");
const historyList = document.querySelector("#history-list");
const historyMessage = document.querySelector("#history-message");
const historyClearButton = document.querySelector("#history-clear-button");
const mlxModelField = document.querySelector("#mlx-model-field");
const mlxModelPathOrRepo = document.querySelector("#mlx-model-path-or-repo");
const mlxModelHelp = document.querySelector("#mlx-model-help");
const qwenModelField = document.querySelector("#qwen-model-field");
const qwenModelPathOrRepo = document.querySelector("#qwen-model-path-or-repo");
const qwenModelHelp = document.querySelector("#qwen-model-help");
const audioModelSelect = document.querySelector("#audio-model-select");
const audioModelHelp = document.querySelector("#audio-model-help");
const audioModelMeta = document.querySelector("#audio-model-meta");
const localAudioLlmField = document.querySelector("#local-audio-llm-field");
const whisperModelField = document.querySelector("#whisper-model-field");
const whisperModeStatus = document.querySelector("#whisper-mode-status");
const mlxModeStatus = document.querySelector("#mlx-mode-status");
const localAudioModeStatus = document.querySelector("#local-audio-mode-status");
const registryRefreshButton = document.querySelector("#registry-refresh-button");
const registryRefreshLabel = document.querySelector("#registry-refresh-label");
const audioTestButton = document.querySelector("#audio-test-button");
const audioTestLabel = document.querySelector("#audio-test-label");
const environmentSummary = document.querySelector("#environment-summary");
const environmentStatusGrid = document.querySelector("#environment-status-grid");
const environmentAdvice = document.querySelector("#environment-advice");
const modelDetectionList = document.querySelector("#model-detection-list");
const jobsCollapseButton = document.querySelector("#jobs-collapse-button");
const jobsRegion = document.querySelector("#jobs-region");
const editPromptButton = document.querySelector("#edit-prompt-button");
const promptModal = document.querySelector("#prompt-modal");
const promptModalTitle = document.querySelector("#prompt-modal-title");
const promptEditor = document.querySelector("#prompt-editor");
const savePromptButton = document.querySelector("#save-prompt-button");
const restorePromptButton = document.querySelector("#restore-prompt-button");
const fixAllButton = document.querySelector("#fix-all-button");
const fixModal = document.querySelector("#fix-modal");
const mirrorSourceToggle = document.querySelector("#mirror-source-toggle");
const fixPlan = document.querySelector("#fix-plan");
const customModelPath = document.querySelector("#custom-model-path");
const customModelProvider = document.querySelector("#custom-model-provider");
const customModelCapability = document.querySelector("#custom-model-capability");
const pickCustomModelFolderButton = document.querySelector("#pick-custom-model-folder-button");
const addCustomModelButton = document.querySelector("#add-custom-model-button");
const customModelMessage = document.querySelector("#custom-model-message");
const tutorialButton = document.querySelector("#tutorial-button");
const tutorialModal = document.querySelector("#tutorial-modal");
const settingsTemplateSelect = document.querySelector("#settings-template-select");
const settingsTemplateNameInput = document.querySelector("#settings-template-name");
const saveSettingsTemplateButton = document.querySelector("#save-settings-template-button");
const deleteSettingsTemplateButton = document.querySelector("#delete-settings-template-button");
const settingsMemoryMessage = document.querySelector("#settings-memory-message");
const completionToast = document.querySelector("#completion-toast");
const themeToggleButtons = Array.from(document.querySelectorAll("[data-theme-toggle]"));
const configModals = {
  engine: document.querySelector("#engine-settings-modal"),
  polish: document.querySelector("#polish-settings-modal"),
  export: document.querySelector("#export-settings-modal"),
  clip: document.querySelector("#clip-settings-modal"),
};
const configSummary = {
  engineTitle: document.querySelector("#engine-summary-title"),
  engineDetail: document.querySelector("#engine-summary-detail"),
  polishTitle: document.querySelector("#polish-summary-title"),
  polishDetail: document.querySelector("#polish-summary-detail"),
  exportTitle: document.querySelector("#export-summary-title"),
  exportDetail: document.querySelector("#export-summary-detail"),
  clipTitle: document.querySelector("#clip-summary-title"),
  clipDetail: document.querySelector("#clip-summary-detail"),
};

const HISTORY_KEY = "audio-transcribe:recent-jobs:v1";
const CUSTOM_INSTRUCTION_KEY = "audio-transcribe:polish-custom-instruction:v1";
const PROMPT_OVERRIDES_KEY = "audio-transcribe:polish-prompts:v1";
const JOBS_COLLAPSED_KEY = "audio-transcribe:jobs-collapsed:v1";
const JOB_DETAIL_COLLAPSED_KEY = "audio-transcribe:job-detail-collapsed:v1";
const JOB_DIAGNOSTIC_DETAIL_OPEN_KEY = "audio-transcribe:job-diagnostic-detail-open:v1";
const JOB_COMPARE_EXPANDED_KEY = "audio-transcribe:job-compare-expanded:v1";
const TASK_SETTINGS_KEY = "audio-transcribe:task-settings:last:v1";
const TASK_PRESETS_KEY = "audio-transcribe:task-settings-presets:v1";
const THEME_KEY = "audio-transcribe:theme:v1";
const HISTORY_LIMIT = 5;
const HISTORY_TEXT_LIMIT = 12000;

let jobsPollTimer = null;
let modelPollTimer = null;
let ollamaPollTimer = null;
let lastModelStatus = null;
let lastOllamaStatus = null;
let lastMlxStatus = null;
let lastQwenStatus = null;
let lastMlxVlmStatus = null;
let lastLocalModelDetection = null;
let lastModelRegistry = null;
let lastJobs = [];
let jobElements = new Map();
let selectedHistoryJobId = null;
let polishProfiles = [];
let submittingJob = false;
let clipDefaultsReady = false;
let clipRangeTouched = false;
let customModelProbeTimer = null;
let collapsedJobIds = loadStoredIdSet(JOB_DETAIL_COLLAPSED_KEY);
let openDiagnosticDetailJobIds = loadStoredIdSet(JOB_DIAGNOSTIC_DETAIL_OPEN_KEY);
let compareExpandedJobIds = loadStoredIdSet(JOB_COMPARE_EXPANDED_KEY);
let jobStateSnapshot = new Map();
let jobCompletionTrackerReady = false;
let watchedCompletionJobIds = new Set();
let notifiedCompletionJobIds = new Set();
let unreadCompletedJobs = 0;
let completionToastTimer = null;
let pendingDeletePresetId = "";

initThemeToggle();
refreshPolishProfiles();
loadSavedCustomInstruction();
renderSettingsTemplates();
applyStoredTaskSettings(loadLastTaskSettings(), { silent: true });
restoreJobsCollapsedState();
renderHistory(loadHistory());
refreshModelRegistry();
refreshModelStatus();
refreshMlxStatus();
refreshQwenStatus();
refreshOllamaStatus();
refreshHealth();
refreshJobs();
refreshCleanupStatus();
startJobsPolling();
updateEngineControls();
updatePolishControls();
updateFormatControls();
initCompletionNotificationBadges();
updateWorkbenchSummaries();

jobsRefreshButton.addEventListener("click", refreshJobs);
jobsCleanupButton.addEventListener("click", cleanupJobWorkFiles);
jobsCollapseButton.addEventListener("click", toggleJobsCollapsed);
jobsNavButton?.addEventListener("click", clearCompletionNotifications);
headerOpenJobsButton?.addEventListener("click", clearCompletionNotifications);
themeToggleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(nextTheme, { persist: true });
  });
});
registryRefreshButton.addEventListener("click", refreshModelRegistry);
audioModelSelect.addEventListener("change", () => {
  applySelectedAudioModelToForm();
  renderSelectedAudioModel();
  updateEngineControls();
});
audioTestButton.addEventListener("click", quickTestSelectedAudioModel);
addCustomModelButton?.addEventListener("click", registerCustomModel);
pickCustomModelFolderButton?.addEventListener("click", pickCustomModelFolder);
customModelPath?.addEventListener("input", scheduleCustomModelProbe);
customModelProvider?.addEventListener("change", scheduleCustomModelProbe);
customModelCapability?.addEventListener("change", scheduleCustomModelProbe);
enablePolishInput.addEventListener("change", updatePolishControls);
polishProfileSelect.addEventListener("change", () => {
  updatePolishProfileDescription();
  updatePromptPreview();
});
settingsTemplateSelect?.addEventListener("change", applySelectedSettingsTemplate);
saveSettingsTemplateButton?.addEventListener("click", saveCurrentSettingsTemplate);
deleteSettingsTemplateButton?.addEventListener("click", deleteSelectedSettingsTemplate);
document.querySelector("#open-engine-settings-button")?.addEventListener("click", () => openConfigModal("engine"));
document.querySelector("#open-polish-settings-button")?.addEventListener("click", () => openConfigModal("polish"));
document.querySelector("#open-export-settings-button")?.addEventListener("click", () => openConfigModal("export"));
document.querySelector("#open-clip-settings-button")?.addEventListener("click", () => openConfigModal("clip"));
document.querySelectorAll("[data-close-config-modal]").forEach((button) => {
  button.addEventListener("click", () => button.closest("dialog")?.close());
});
Object.values(configModals).forEach((modal) => {
  modal?.addEventListener("click", (event) => {
    if (event.target === modal) modal.close();
  });
});
form.addEventListener("change", updateWorkbenchSummaries);
form.addEventListener("input", updateWorkbenchSummaries);

function initThemeToggle() {
  const initialTheme = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
  applyTheme(initialTheme, { persist: false });
}

function applyTheme(theme, { persist = false } = {}) {
  const nextTheme = theme === "dark" ? "dark" : "light";
  document.documentElement.dataset.theme = nextTheme;
  document.documentElement.style.colorScheme = nextTheme;
  if (persist) {
    try {
      localStorage.setItem(THEME_KEY, nextTheme);
    } catch {
      // Theme persistence is optional; the visual state still updates.
    }
  }
  syncThemeButtons(nextTheme);
}

function syncThemeButtons(theme) {
  const isDark = theme === "dark";
  themeToggleButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(isDark));
    button.title = isDark ? "切换浅色模式" : "切换深色模式";
    button.setAttribute("aria-label", button.title);
    const label = button.querySelector("span");
    if (label) label.textContent = isDark ? "浅色模式" : "深色模式";
  });
}

/* Template popover toggle */
const templatePopoverBtn = document.querySelector("#header-open-template-button");
const templatePopoverPanel = document.querySelector("#template-popover-panel");
if (templatePopoverBtn && templatePopoverPanel) {
  templatePopoverBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isHidden = templatePopoverPanel.hidden;
    templatePopoverPanel.hidden = !isHidden;
    templatePopoverBtn.classList.toggle("active", isHidden);
  });
  document.addEventListener("click", (e) => {
    if (!templatePopoverPanel.hidden &&
        !templatePopoverPanel.contains(e.target) &&
        !templatePopoverBtn.contains(e.target)) {
      templatePopoverPanel.hidden = true;
      templatePopoverBtn.classList.remove("active");
    }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !templatePopoverPanel.hidden) {
      templatePopoverPanel.hidden = true;
      templatePopoverBtn.classList.remove("active");
    }
  });
}

tutorialButton.addEventListener("click", () => tutorialModal.showModal());
polishCustomInstruction.addEventListener("input", () => {
  localStorage.setItem(CUSTOM_INSTRUCTION_KEY, polishCustomInstruction.value);
  updatePromptPreview();
});
clearPolishCustomButton.addEventListener("click", () => {
  polishCustomInstruction.value = "";
  localStorage.removeItem(CUSTOM_INSTRUCTION_KEY);
  updatePromptPreview();
});
editPromptButton.addEventListener("click", openPromptEditor);
savePromptButton.addEventListener("click", savePromptOverride);
restorePromptButton.addEventListener("click", restorePromptDefault);
fixAllButton.addEventListener("click", openFixModal);
mirrorSourceToggle.addEventListener("change", renderFixPlan);
includeTimestampsInput.addEventListener("change", updateFormatControls);
historyClearButton.addEventListener("click", async () => {
  if (!window.confirm("清空最近 5 条历史记录？运行中的任务不会被清除。")) return;
  historyClearButton.disabled = true;
  try {
    const response = await fetch("/api/jobs/history", { method: "DELETE" });
    const jobs = await response.json().catch(() => []);
    if (!response.ok) {
      throw new Error(jobs.detail || "清空历史失败");
    }
    localStorage.removeItem(HISTORY_KEY);
    selectedHistoryJobId = null;
    renderHistory([]);
    renderJobs(Array.isArray(jobs) ? jobs : []);
  } catch (error) {
    showDiagnostic(diagnoseClientError(error.message));
  } finally {
    historyClearButton.disabled = false;
  }
});
healthRefreshButton.addEventListener("click", async () => {
  healthRefreshButton.disabled = true;
  healthRefreshLabel.textContent = "检查中";
  await refreshHealth();
  healthRefreshButton.disabled = false;
  healthRefreshLabel.textContent = "重新检查";
});
form.querySelectorAll('input[name="transcription_engine"]').forEach((input) => {
  input.addEventListener("change", updateEngineControls);
});
mlxModelPathOrRepo.addEventListener("input", () => {
  window.clearTimeout(mlxModelPathOrRepo._refreshTimer);
  mlxModelPathOrRepo._refreshTimer = window.setTimeout(() => refreshMlxStatus(), 350);
});
qwenModelPathOrRepo.addEventListener("input", () => {
  window.clearTimeout(qwenModelPathOrRepo._refreshTimer);
  qwenModelPathOrRepo._refreshTimer = window.setTimeout(() => refreshQwenStatus(), 350);
});
ollamaManagedModelSelect.addEventListener("change", refreshSelectedOllamaModel);
ollamaTranscriptionModelSelect.addEventListener("change", applyDetailAudioModelSelection);
modelInfoButton.addEventListener("click", () => {
  modelInfoPopover.hidden = !modelInfoPopover.hidden;
  renderSelectedWhisperModelMeta();
});
document.addEventListener("click", (event) => {
  if (modelInfoPopover.hidden) return;
  if (modelInfoPopover.contains(event.target) || modelInfoButton.contains(event.target)) return;
  modelInfoPopover.hidden = true;
});
localModelDetectButton.addEventListener("click", refreshLocalModelDetection);
localProviderSelect.addEventListener("change", renderLocalModelChoices);
localModelSelect.addEventListener("change", applyDetectedLocalModelSelection);

modelSelect.addEventListener("change", async () => {
  if (!modelSelect.value) {
    modelMessage.textContent = "请选择 Whisper 模型";
    renderSelectedWhisperModelMeta();
    return;
  }
  modelSelect.disabled = true;
  modelMessage.textContent = `正在检查 ${modelSelect.value} 模型`;
  let status = null;
  try {
    const response = await fetch("/api/model/select", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelSelect.value }),
    });
    status = await response.json();
    if (!response.ok) {
      throw new Error(status.detail || "模型切换失败");
    }
    renderModelStatus(status);
    modelInfoPopover.hidden = true;
  } catch (error) {
    modelMessage.textContent = `模型切换失败：${error.message}`;
  } finally {
    modelSelect.disabled = status?.download_state === "downloading";
  }
});

modelRefreshButton.addEventListener("click", async () => {
  modelRefreshButton.disabled = true;
  modelRefreshLabel.textContent = "检测中";
  modelMessage.textContent = `正在重新检测 ${modelSelect.value || "当前"} 模型`;
  await refreshModelStatus();
  modelRefreshButton.disabled = false;
  modelRefreshLabel.textContent = "重新检测";
});

pickWhisperModelFolderButton.addEventListener("click", pickWhisperModelFolder);
bindWhisperModelPathButton.addEventListener("click", bindSelectedWhisperModelPath);
unbindWhisperModelPathButton.addEventListener("click", unbindSelectedWhisperModelPath);

modelDownloadButton.addEventListener("click", async () => {
  const selectedLabel = modelSelect.selectedOptions[0]?.textContent || modelSelect.value || "当前模型";
  const approved = window.confirm(
    `${selectedLabel} 模型文件可能较大，会下载到项目的 models 目录。确认开始下载吗？`,
  );
  if (!approved) return;

  modelDownloadButton.disabled = true;
  modelMessage.textContent = "正在提交模型下载任务";
  try {
    await fetch("/api/model/download", { method: "POST" });
    startModelPolling();
  } catch (error) {
    modelMessage.textContent = `模型下载任务启动失败：${error.message}`;
    modelDownloadButton.disabled = false;
  }
});

modelCancelButton.addEventListener("click", async () => {
  modelCancelButton.disabled = true;
  modelCancelLabel.textContent = "取消中";
  modelMessage.textContent = "正在取消模型下载并清理已下载内容";
  try {
    await fetch("/api/model/download/cancel", { method: "POST" });
    startModelPolling();
  } catch (error) {
    modelMessage.textContent = `取消模型下载失败：${error.message}`;
    modelCancelButton.disabled = false;
    modelCancelLabel.textContent = "取消下载";
  }
});

ollamaRefreshButton.addEventListener("click", async () => {
  ollamaRefreshButton.disabled = true;
  ollamaRefreshLabel.textContent = "检测中";
  await refreshOllamaStatus();
  ollamaRefreshButton.disabled = false;
  ollamaRefreshLabel.textContent = "重新检测";
});

ollamaDownloadButton.addEventListener("click", async () => {
  const modelId = ollamaManagedModelSelect.value;
  await confirmAndStartOllamaDownload(modelId);
});

ollamaCancelButton.addEventListener("click", async () => {
  const modelId = ollamaManagedModelSelect.value;
  ollamaCancelButton.disabled = true;
  ollamaCancelLabel.textContent = "取消中";
  try {
    await fetch("/api/ollama/models/pull/cancel", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId }),
    });
    startOllamaPolling(modelId);
  } catch (error) {
    ollamaMessage.textContent = `取消 Ollama 下载失败：${error.message}`;
    ollamaCancelButton.disabled = false;
    ollamaCancelLabel.textContent = "取消下载";
  }
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  fileLabel.textContent = file?.name || "选择本地音频或视频";
  if (file) {
    sourcePathInput.value = "";
    sourcePathLabel.textContent = "浏览器上传不会暴露原始目录；自动存储请改用“选择系统文件”。";
  }
  clipDefaultsReady = false;
  clipRangeTouched = false;
  setClipRange("00:00:00", "00:00:00");
  if (file) {
    loadMediaDuration(file);
  }
});

resetButton.addEventListener("click", () => {
  form.reset();
  loadSavedCustomInstruction();
  applyStoredTaskSettings(loadLastTaskSettings(), { silent: true });
  updatePolishControls();
  updateFormatControls();
  updatePromptPreview();
  fileLabel.textContent = "选择本地音频或视频";
  sourcePathInput.value = "";
  sourcePathLabel.textContent = "自动存储需要通过系统文件选择器提交本地文件。";
  clipDefaultsReady = false;
  clipRangeTouched = false;
  setClipRange("00:00:00", "00:00:00");
});

pickSourceFileButton?.addEventListener("click", pickSourceFile);

startTimeInput.addEventListener("change", () => {
  clipRangeTouched = true;
});

endTimeInput.addEventListener("change", () => {
  clipRangeTouched = true;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (submittingJob) {
    return;
  }
  const mode = selectedAudioMode();
  if (!mode) {
    showDiagnostic({
      code: "AUDIO_MODE_REQUIRED",
      title: "未选择转录引擎",
      message: "请选择 Whisper、MLX Whisper 或本地音频大模型。",
      action: "三种模式互相独立；检测失败只会提示需要配置，不会隐藏选项。",
      technical_detail: "transcription_engine is empty",
    });
    return;
  }
  if (mode === "local_audio_llm") {
    const selectedAudio = selectedAudioModel();
    if (!selectedAudio) {
      showDiagnostic({
        code: "AUDIO_MODEL_REQUIRED",
        title: "未选择本地音频大模型",
        message: "请选择已检测到的音频模型，或先在“模型检测”绑定本地目录。",
        action: "点击“检测模型”刷新模型池，也可以手动绑定模型目录。",
        technical_detail: "audio_model_id is empty",
      });
      return;
    }
    const modelApplied = applySelectedAudioModelToForm();
    if (!modelApplied) return;
  }
  if (mode === "whisper" && !modelSelect.value) {
    showDiagnostic({
      code: "WHISPER_MODEL_REQUIRED",
      title: "未选择 Whisper 模型",
      message: "请选择一个检测到或可下载的 faster-whisper 模型。",
      action: "Whisper 模式独立于本地音频大模型，不会自动选择模型。",
      technical_detail: "whisper_model_id is empty",
    });
    return;
  }
  const ready = await ensureSelectedOllamaModelsReady();
  if (!ready) return;
  const mlxReady = await ensureSelectedMlxReady();
  if (!mlxReady) return;
  const qwenReady = await ensureSelectedQwenReady();
  if (!qwenReady) return;
  const mlxVlmReady = await ensureSelectedMlxVlmReady();
  if (!mlxVlmReady) return;

  const data = new FormData(form);
  const selectedFormats = [...form.querySelectorAll('input[name="formats"]:checked')].map((input) => input.value);
  if (!selectedFormats.length) {
    showDiagnostic(diagnoseClientError("请至少选择 TXT、Markdown、JSON、SRT 或 Word 中的一种导出格式。", "EXPORT_FORMAT_MISSING"));
    return;
  }
  data.set("formats", selectedFormats.join(","));
  data.set("include_timestamps", includeTimestampsInput.checked ? "true" : "false");
  data.set("transcription_engine", selectedTranscriptionEngine());
  data.set("whisper_model_id", modelSelect.value || "");
  data.set("transcription_model_id", ollamaTranscriptionModelSelect.value || "");
  data.set("mlx_model_path_or_repo", mlxModelPathOrRepo.value.trim());
  data.set("qwen_model_path_or_repo", qwenModelPathOrRepo.value.trim());
  data.set("enable_polish", enablePolishInput.checked ? "true" : "false");
  data.set("export_scope", form.querySelector('input[name="export_scope"]:checked')?.value || "raw");
  data.set("polish_custom_instruction", effectivePolishInstructionValue());
  data.set("polish_profile_id", selectedPolishProfileIds().join(","));
  if (!enablePolishInput.checked) {
    data.delete("polish_model_id");
    data.delete("polish_profile_id");
    data.delete("polish_custom_instruction");
  }
  if (!clipDefaultsReady && !clipRangeTouched) {
    data.delete("start_time");
    data.delete("end_time");
  }
  for (const fieldName of ["start_time", "end_time"]) {
    if (!data.get(fieldName)) {
      data.delete(fieldName);
    }
  }

  if (!fileInput.files.length) {
    data.delete("file");
  }
  if (fileInput.files.length) {
    data.delete("source_path");
  }
  data.set("auto_save_outputs", autoSaveOutputsInput?.checked ? "true" : "false");

  submittingJob = true;
  submitButton.disabled = true;
  try {
    const submittedSettings = collectTaskSettings();
    const response = await fetch("/api/jobs", { method: "POST", body: data });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "任务创建失败");
    }
    if (payload.id) watchedCompletionJobIds.add(payload.id);
    saveLastTaskSettings(submittedSettings);
    form.reset();
    loadSavedCustomInstruction();
    applyStoredTaskSettings(submittedSettings, { silent: true });
    updatePolishControls();
    updateFormatControls();
    updatePromptPreview();
    renderSettingsTemplates();
    fileLabel.textContent = "选择本地音频或视频";
    sourcePathInput.value = "";
    sourcePathLabel.textContent = "自动存储需要通过系统文件选择器提交本地文件。";
    clipDefaultsReady = false;
    clipRangeTouched = false;
    setClipRange("00:00:00", "00:00:00");
    await refreshJobs();
  } catch (error) {
    showDiagnostic(diagnoseClientError(error.message));
  } finally {
    submittingJob = false;
    submitButton.disabled = false;
  }
});

function collectTaskSettings() {
  return {
    version: 1,
    updated_at: new Date().toISOString(),
    language: form.querySelector('[name="language"]')?.value || "auto",
    transcription_engine: selectedAudioMode(),
    audio_model_id: audioModelSelect.value || "",
    whisper_model_id: modelSelect.value || "",
    ollama_transcription_model_id: ollamaTranscriptionModelSelect.value || "",
    mlx_model_path_or_repo: mlxModelPathOrRepo.value.trim(),
    qwen_model_path_or_repo: qwenModelPathOrRepo.value.trim(),
    enable_polish: enablePolishInput.checked,
    polish_model_id: polishModelSelect.value || "",
    polish_profile_ids: selectedPolishProfileIds(),
    polish_custom_instruction: polishCustomInstruction.value,
    include_timestamps: includeTimestampsInput.checked,
    formats: [...form.querySelectorAll('input[name="formats"]:checked')].map((input) => input.value),
    export_scope: form.querySelector('input[name="export_scope"]:checked')?.value || "raw",
    auto_save_outputs: autoSaveOutputsInput?.checked || false,
  };
}

function applyStoredTaskSettings(settings, options = {}) {
  if (!settings || typeof settings !== "object") return false;
  setSelectValue(form.querySelector('[name="language"]'), settings.language || "auto");
  if (settings.transcription_engine) {
    selectAudioMode(settings.transcription_engine);
  }
  setSelectValue(audioModelSelect, settings.audio_model_id, "已保存的音频模型");
  setSelectValue(modelSelect, settings.whisper_model_id, settings.whisper_model_id);
  setSelectValue(ollamaTranscriptionModelSelect, settings.ollama_transcription_model_id, settings.ollama_transcription_model_id);
  mlxModelPathOrRepo.value = settings.mlx_model_path_or_repo || "";
  qwenModelPathOrRepo.value = settings.qwen_model_path_or_repo || "";
  enablePolishInput.checked = Boolean(settings.enable_polish);
  setSelectValue(polishModelSelect, settings.polish_model_id, settings.polish_model_id);
  setSelectedPolishProfileIds(settings.polish_profile_ids || settings.polish_profile_id || []);
  polishCustomInstruction.value = settings.polish_custom_instruction || "";
  includeTimestampsInput.checked = settings.include_timestamps !== false;
  setCheckedValues('input[name="formats"]', settings.formats?.length ? settings.formats : ["txt"]);
  setCheckedValue('input[name="export_scope"]', settings.export_scope || "raw");
  if (autoSaveOutputsInput) autoSaveOutputsInput.checked = Boolean(settings.auto_save_outputs);
  if (settings.polish_custom_instruction) {
    localStorage.setItem(CUSTOM_INSTRUCTION_KEY, settings.polish_custom_instruction);
  }
  applySelectedAudioModelToForm();
  updatePolishControls();
  updateFormatControls();
  updatePromptPreview();
  renderSelectedAudioModel();
  updateEngineControls();
  if (!options.silent) {
    updateSettingsMemoryMessage(options.message || "已应用任务设置。");
  }
  return true;
}

function setSelectValue(select, value, fallbackLabel = "") {
  if (!select || value === undefined || value === null) return;
  const normalized = String(value);
  if (!normalized) {
    select.value = "";
    return;
  }
  ensureSelectOption(select, normalized, fallbackLabel || normalized);
  select.value = normalized;
}

function setCheckedValues(selector, values) {
  const selected = new Set((Array.isArray(values) ? values : String(values || "").split(",")).map((value) => String(value)));
  const inputs = [...form.querySelectorAll(selector)];
  inputs.forEach((input) => {
    input.checked = selected.has(input.value);
  });
  if (!inputs.some((input) => input.checked) && inputs[0]) {
    inputs[0].checked = true;
  }
}

function setCheckedValue(selector, value) {
  const input = form.querySelector(`${selector}[value="${cssEscape(String(value || ""))}"]`);
  if (input) input.checked = true;
}

async function pickSourceFile() {
  if (!pickSourceFileButton || !sourcePathInput || !sourcePathLabel) return;
  pickSourceFileButton.disabled = true;
  sourcePathLabel.textContent = "正在打开系统文件选择器。";
  try {
    const response = await fetch("/api/media/pick-file", { method: "POST" });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || "选择文件失败");
    }
    sourcePathInput.value = payload.path || "";
    sourcePathLabel.textContent = payload.path || payload.name || "已选择系统文件";
    if (fileInput) fileInput.value = "";
    fileLabel.textContent = payload.name || "已选择系统文件";
    clipDefaultsReady = false;
    clipRangeTouched = false;
    setClipRange("00:00:00", "00:00:00");
  } catch (error) {
    sourcePathLabel.textContent = error.message === "未选择文件" ? "未选择系统文件。" : `选择文件失败：${error.message}`;
  } finally {
    pickSourceFileButton.disabled = false;
  }
}

function setSelectedPolishProfileIds(value) {
  const ids = Array.isArray(value)
    ? value
    : String(value || "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
  polishProfileSelect.value = ids.join(",");
  const selected = new Set(ids);
  const inputs = [...polishProfileList.querySelectorAll('input[type="checkbox"]')];
  inputs.forEach((input) => {
    input.checked = selected.has(input.value);
  });
  if (inputs.length && !inputs.some((input) => input.checked)) {
    inputs[0].checked = true;
  }
  syncPolishProfileValue();
}

function cssEscape(value) {
  if (window.CSS?.escape) return window.CSS.escape(value);
  return value.replace(/["\\]/g, "\\$&");
}

function readStoredJson(key, fallback) {
  try {
    const parsed = JSON.parse(localStorage.getItem(key) || "null");
    return parsed ?? fallback;
  } catch {
    return fallback;
  }
}

function loadLastTaskSettings() {
  return readStoredJson(TASK_SETTINGS_KEY, null);
}

function saveLastTaskSettings(settings) {
  localStorage.setItem(TASK_SETTINGS_KEY, JSON.stringify(settings));
  updateSettingsMemoryMessage("已记住本次模型和参数设置。");
}

function loadTaskPresets() {
  const presets = readStoredJson(TASK_PRESETS_KEY, []);
  return Array.isArray(presets) ? presets.filter((preset) => preset?.id && preset?.settings) : [];
}

function saveTaskPresets(presets) {
  localStorage.setItem(TASK_PRESETS_KEY, JSON.stringify(presets.slice(0, 20)));
}

function renderSettingsTemplates(selectedValue = settingsTemplateSelect?.value || "") {
  if (!settingsTemplateSelect) return;
  const presets = loadTaskPresets();
  const options = [
    new Option(loadLastTaskSettings() ? "自动沿用上次任务" : "自动沿用上次任务（提交后生效）", ""),
    ...presets.map((preset) => new Option(preset.name, `preset:${preset.id}`)),
  ];
  settingsTemplateSelect.replaceChildren(...options);
  settingsTemplateSelect.value = options.some((option) => option.value === selectedValue) ? selectedValue : "";
  updateTemplateDeleteState();
}

function applySelectedSettingsTemplate() {
  const value = settingsTemplateSelect?.value || "";
  pendingDeletePresetId = "";
  updateTemplateDeleteState();
  if (!value) {
    const applied = applyStoredTaskSettings(loadLastTaskSettings(), {
      message: "已应用上次任务配置。",
    });
    if (!applied) updateSettingsMemoryMessage("还没有上次任务配置；提交一次任务后会自动记住。");
    return;
  }
  const presetId = value.replace(/^preset:/, "");
  const preset = loadTaskPresets().find((item) => item.id === presetId);
  if (!preset) return;
  applyStoredTaskSettings(preset.settings, { message: `已应用模板：${preset.name}` });
}

function saveCurrentSettingsTemplate() {
  const name = settingsTemplateNameInput?.value.trim() || `设置模板 ${loadTaskPresets().length + 1}`;
  const presets = loadTaskPresets().filter((preset) => preset.name !== name);
  const preset = {
    id: `preset-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
    name,
    created_at: new Date().toISOString(),
    settings: collectTaskSettings(),
  };
  presets.unshift(preset);
  saveTaskPresets(presets);
  renderSettingsTemplates(`preset:${preset.id}`);
  if (settingsTemplateNameInput) settingsTemplateNameInput.value = "";
  updateSettingsMemoryMessage(`已保存模板：${name}`);
}

function deleteSelectedSettingsTemplate() {
  const value = settingsTemplateSelect?.value || "";
  if (!value.startsWith("preset:")) return;
  const presetId = value.replace(/^preset:/, "");
  const preset = loadTaskPresets().find((item) => item.id === presetId);
  if (!preset) return;
  if (pendingDeletePresetId !== presetId) {
    pendingDeletePresetId = presetId;
    updateTemplateDeleteState();
    updateSettingsMemoryMessage(`再次点击“确认删除”会删除模板：${preset.name}`);
    return;
  }
  saveTaskPresets(loadTaskPresets().filter((item) => item.id !== presetId));
  pendingDeletePresetId = "";
  renderSettingsTemplates("");
  updateSettingsMemoryMessage("已删除模板，当前将自动沿用上次任务配置。");
}

function updateTemplateDeleteState() {
  if (deleteSettingsTemplateButton && settingsTemplateSelect) {
    const presetId = settingsTemplateSelect.value.replace(/^preset:/, "");
    const canDelete = settingsTemplateSelect.value.startsWith("preset:");
    deleteSettingsTemplateButton.disabled = !canDelete;
    deleteSettingsTemplateButton.textContent = canDelete && pendingDeletePresetId === presetId ? "确认删除" : "删除模板";
  }
}

function updateSettingsMemoryMessage(message) {
  if (settingsMemoryMessage) settingsMemoryMessage.textContent = message;
}

function openConfigModal(name) {
  const modal = configModals[name];
  if (!modal) return;
  if (modal.open) {
    modal.close();
    return;
  }
  updateWorkbenchSummaries();
  modal.showModal();
}

function updateWorkbenchSummaries() {
  updateEngineSummary();
  updatePolishSummary();
  updateExportSummary();
  updateClipSummary();
}

function updateEngineSummary() {
  const mode = selectedAudioMode();
  const engine = selectedTranscriptionEngine();
  if (!mode) {
    setSummary(configSummary.engineTitle, configSummary.engineDetail, "未选择", "选择 Whisper、MLX Whisper 或本地音频大模型。");
    return;
  }
  if (mode === "whisper") {
    const label = selectedOptionLabel(modelSelect) || "未选择模型";
    const state = lastModelStatus?.download_state === "downloading"
      ? "模型下载中"
      : lastModelStatus?.available
        ? "模型已就绪"
        : "等待模型配置";
    setSummary(configSummary.engineTitle, configSummary.engineDetail, "Whisper（faster-whisper）", `${label} · ${state}`);
    return;
  }
  if (mode === "mlx-whisper") {
    const modelPath = mlxModelPathOrRepo.value.trim();
    const status = lastMlxStatus?.available ? "已配置" : "未配置";
    setSummary(configSummary.engineTitle, configSummary.engineDetail, "MLX Whisper", `${status}${modelPath ? ` · ${displayModelPath(modelPath)}` : ""}`);
    return;
  }
  const model = selectedAudioModel();
  if (model) {
    setSummary(configSummary.engineTitle, configSummary.engineDetail, transcriptionEngineLabel(engine), `${model.name} · ${providerLabel(model.provider)}`);
    return;
  }
  setSummary(configSummary.engineTitle, configSummary.engineDetail, "本地音频大模型", "未选择模型，可在弹窗中检测或选择。");
}

function updatePolishSummary() {
  if (!enablePolishInput.checked) {
    setSummary(configSummary.polishTitle, configSummary.polishDetail, "未启用", "当前只输出原始转录文本。");
    return;
  }
  const modelLabel = selectedOptionLabel(polishModelSelect) || "未选择 Text 模型";
  const profiles = selectedPolishProfiles();
  const profileLabel = profiles.length ? profiles.map((profile) => profile.label).join(" + ") : "未选择整理配置";
  const custom = polishCustomInstruction.value.trim() ? "含追加指令" : "无追加指令";
  setSummary(configSummary.polishTitle, configSummary.polishDetail, polishModelSelect.value ? "已启用" : "未完成配置", `${modelLabel} · ${profileLabel} · ${custom}`);
}

function updateExportSummary() {
  const formats = checkedInputLabels('input[name="formats"]');
  const scope = checkedInputLabel('input[name="export_scope"]') || "原始文本";
  const timestamp = includeTimestampsInput.checked ? "带时间轴" : "纯文本";
  const title = formats.length ? `${formats.join(" / ")} · ${scope}` : "未选择格式";
  const detail = includeTimestampsInput.checked ? "时间轴已开启，可导出 SRT。" : "时间轴已关闭，SRT 会自动禁用。";
  setSummary(configSummary.exportTitle, configSummary.exportDetail, title, `${timestamp} · ${detail}`);
}

function updateClipSummary() {
  const start = startTimeInput.value || "00:00:00";
  const end = endTimeInput.value || "00:00:00";
  const hasStart = start !== "00:00:00";
  const hasEnd = end !== "00:00:00";
  if (!hasStart && !hasEnd) {
    setSummary(configSummary.clipTitle, configSummary.clipDetail, "未截取", "默认处理完整音视频。");
    return;
  }
  setSummary(configSummary.clipTitle, configSummary.clipDetail, `${hasStart ? start : "开始"} → ${hasEnd ? end : "结束"}`, "只处理指定时间范围。");
}

function setSummary(titleNode, detailNode, title, detail) {
  if (titleNode) titleNode.textContent = title;
  if (detailNode) detailNode.textContent = detail;
}

function selectedOptionLabel(select) {
  const option = select?.selectedOptions?.[0];
  if (!option || !option.value) return "";
  return option.textContent.replace(/（已存在）/g, "").trim();
}

function checkedInputLabels(selector) {
  return [...form.querySelectorAll(`${selector}:checked`)].map((input) => input.closest("label")?.querySelector("span")?.textContent?.trim() || input.value);
}

function checkedInputLabel(selector) {
  return checkedInputLabels(selector)[0] || "";
}

async function refreshModelRegistry(preferred = {}) {
  registryRefreshButton.disabled = true;
  registryRefreshLabel.textContent = "检测中";
  try {
    const response = await fetch("/api/models/registry");
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "模型检测失败");
    renderModelRegistry(payload, preferred);
    return payload;
  } catch (error) {
    audioModelHelp.textContent = `模型检测失败：${error.message}`;
    modelDetectionList?.replaceChildren();
    return null;
  } finally {
    registryRefreshButton.disabled = false;
    registryRefreshLabel.textContent = "检测模型";
  }
}

function renderModelRegistry(payload, preferred = {}) {
  lastModelRegistry = payload;
  const models = payload.models || [];
  const audioModels = models.filter(
    (model) => isLocalAudioLlmModel(model) && audioPipelineForModel(model) && model.metadata?.status === "available",
  );
  const textModels = models.filter((model) => model.capabilities?.text && model.metadata?.status === "available");
  renderAudioModelOptions(audioModels, preferred.audioModelId);
  renderPolishModelOptions(textModels, preferred.polishModelPath);
  renderModelDetection(payload.errors || []);
  renderOllamaOptions(lastOllamaStatus || {});
  refreshSelectedOllamaModel();
  applySelectedAudioModelToForm();
  renderSelectedAudioModel();
  updateEngineControls();
  renderModeStatus();
  renderEnvironmentStatus();
  updateWorkbenchSummaries();
}

function renderAudioModelOptions(models, preferredId = "") {
  const current = preferredId || audioModelSelect.value;
  const options = [
    new Option(models.length ? "请选择支持音频输入的模型" : "未检测到支持音频输入的模型", ""),
    ...models.map((model) => new Option(modelOptionLabel(model), model.id)),
  ];
  audioModelSelect.replaceChildren(...options);
  audioModelSelect.value = models.some((model) => model.id === current) ? current : "";
  audioModelHelp.textContent = models.length
    ? "请选择支持音频输入的模型（系统已自动筛选）。"
    : "未检测到本地大模型";
  audioModelHelp.title = models.length ? "" : "可检测 Ollama、MLX、本地目录和 llama.cpp";
}

function renderPolishModelOptions(models, preferredPath = "") {
  const current = preferredPath || polishModelSelect.value;
  const options = [
    new Option(models.length ? "请选择检测到的 Text 模型" : "未检测到 Text 模型", ""),
    ...models.map((model) => {
      const option = new Option(modelOptionLabel(model), model.path_or_id);
      option.dataset.provider = model.provider;
      option.dataset.modelId = model.id;
      return option;
    }),
  ];
  polishModelSelect.replaceChildren(...options);
  polishModelSelect.value = models.some((model) => model.path_or_id === current) ? current : "";
}

function modelOptionLabel(model) {
  return `${model.name} · ${providerLabel(model.provider)} · ${capabilityLabel(model.capabilities)}`;
}

function selectedAudioModel() {
  const models = lastModelRegistry?.models || [];
  return models.find((model) => model.id === audioModelSelect.value) || null;
}

function selectedPolishModel() {
  const value = polishModelSelect.value;
  const models = lastModelRegistry?.models || [];
  const registryModel = models.find((model) => model.path_or_id === value || model.id === value);
  if (registryModel) return registryModel;
  if (!value) return null;
  return {
    id: value,
    name: value,
    provider: polishModelSelect.selectedOptions[0]?.dataset.provider || "ollama",
    path_or_id: value,
    capabilities: { text: true },
    metadata: { status: "available" },
  };
}

function selectedAudioMode() {
  return form.querySelector('input[name="transcription_engine"]:checked')?.value || "";
}

function selectAudioMode(mode) {
  const input = form.querySelector(`input[name="transcription_engine"][value="${mode}"]`);
  if (input) input.checked = true;
}

function isWhisperLikeModel(model) {
  return /whisper/i.test(`${model.name || ""} ${model.path_or_id || ""}`);
}

function isLocalAudioLlmModel(model) {
  return Boolean(model.capabilities?.audio && !isWhisperLikeModel(model));
}

function isQwenAudioModel(model) {
  const text = `${model?.name || ""} ${model?.path_or_id || ""}`.toLowerCase();
  return text.includes("qwen2-audio") || text.includes("qwen-audio") || text.includes("qwen_audio");
}

function isMlxVlmAudioModel(model) {
  const text = `${model?.name || ""} ${model?.path_or_id || ""}`.toLowerCase();
  return text.includes("gemma4") || text.includes("mlx-vlm") || text.includes("mlx_vlm");
}

function renderSelectedAudioModel() {
  const model = selectedAudioModel();
  audioTestButton.disabled = !model;
  audioModelMeta.replaceChildren();
  if (!model) {
    audioModelMeta.append(metaPill("provider", "未选择"), metaPill("capability", "音频转录"));
    updateWorkbenchSummaries();
    return;
  }
  audioModelMeta.append(
    metaPill("provider", providerLabel(model.provider)),
    metaPill("path", model.path_or_id),
    metaPill("capability", capabilityLabel(model.capabilities)),
  );
  updateWorkbenchSummaries();
}

function metaPill(kind, text) {
  const span = document.createElement("span");
  span.className = `meta-pill meta-${kind}`;
  span.textContent = text || "-";
  span.title = text || "";
  return span;
}

function displayModelPath(path) {
  const value = String(path || "").trim();
  if (!value || value === "未配置" || value === "未检测到") return value || "未记录位置";
  if (!value.includes("/") && !value.includes("\\")) return value;
  const normalized = value.replace(/\\/g, "/");
  const parts = normalized.split("/").filter(Boolean);
  const tail = parts.slice(-2).join("/");
  if (normalized.includes("/audio-transcribe/")) return `项目/${tail}`;
  if (normalized.includes("/models/")) return `models/${tail}`;
  return `.../${tail}`;
}

function renderModelDetection(errors = []) {
  modelDetectionList?.replaceChildren();
  const models = lastModelRegistry?.models || [];
  const groups = [
    ["Whisper / faster-whisper", whisperDetectionRows()],
    ["MLX Whisper", mlxWhisperDetectionRows()],
    ["本地音频大模型", localAudioLlmDetectionRows(models)],
  ];
  for (const [label, group] of groups) {
    modelDetectionList?.append(renderModelDetectionGroup(label, group));
  }
  for (const error of errors.slice(0, 4)) {
    const row = document.createElement("small");
    row.className = "provider-error";
    row.textContent = error;
    modelDetectionList?.append(row);
  }
}

function whisperDetectionRows() {
  const statusModels = lastModelStatus?.models || [];
  if (!statusModels.length) {
    return [
      {
        name: "Whisper model pool",
        exists: false,
        provider: "huggingface",
        path: "models/",
        capability: "音频转录",
        reason: "等待 faster-whisper 模型检测",
      },
    ];
  }
  return statusModels.map((model) => ({
    name: model.label || model.id,
    exists: Boolean(model.available),
    provider: "huggingface",
    path: model.available ? model.managed_path : model.managed_path,
    capability: "音频转录",
    reason: model.available ? "已找到" : "未找到",
  }));
}

function mlxWhisperDetectionRows() {
  return [
    {
      name: "MLX Whisper",
      exists: Boolean(lastMlxStatus?.available),
      provider: "mlx",
      path: lastMlxStatus?.model_path_or_repo || mlxModelPathOrRepo.value.trim() || "未配置",
      capability: "音频转录",
      reason: lastMlxStatus?.available ? "已就绪" : lastMlxStatus?.reason || "未配置",
    },
  ];
}

function localAudioLlmDetectionRows(models) {
  const rows = models.filter(isLocalAudioLlmModel).map((model) => ({
    name: model.name,
    exists: model.metadata?.status === "available",
    provider: model.provider,
    path: model.path_or_id,
    capability: capabilityLabel(model.capabilities),
    reason: model.metadata?.status || "missing",
    canDelete: model.metadata?.source === "user_added",
  }));
  if (rows.length) return rows;
  return [
    {
      name: "本地音频大模型",
      exists: false,
      provider: "Ollama、MLX、本地目录等",
      path: "未检测到",
      capability: "音频转录",
      reason: "未检测到可用模型",
    },
  ];
}

function renderModelDetectionGroup(label, models) {
  const section = document.createElement("section");
  section.className = "detection-group";
  const title = document.createElement("h4");
  const exists = models.some((model) => model.exists);
  const readyCount = models.filter((model) => model.exists).length;
  const titleText = document.createElement("span");
  titleText.textContent = label;
  const summary = document.createElement("small");
  summary.className = "detection-group-summary";
  summary.textContent = `${readyCount}/${models.length} 可用`;
  const groupState = document.createElement("b");
  groupState.className = `detection-group-state ${exists ? "is-ready" : "needs-config"}`;
  groupState.textContent = exists ? "已就绪" : "需配置";
  title.append(titleText, summary, groupState);
  section.append(title);
  for (const model of models.slice(0, 8)) {
    const row = document.createElement("div");
    row.className = `detected-model-row ${model.exists ? "is-available" : "is-missing"}`;
    row.title = [model.name, model.exists ? "已找到" : "未就绪", providerLabel(model.provider), model.capability, model.path, model.reason].filter(Boolean).join(" · ");
    const main = document.createElement("div");
    main.className = "detected-model-main";
    const name = document.createElement("strong");
    name.textContent = model.name;
    name.title = model.name;
    const state = document.createElement("b");
    state.className = "detected-model-state";
    state.textContent = model.exists ? "已找到" : "未就绪";
    main.append(name, state);
    const meta = document.createElement("div");
    meta.className = "detected-model-meta";
    const provider = document.createElement("span");
    provider.textContent = providerLabel(model.provider);
    const capability = document.createElement("span");
    capability.textContent = model.capability;
    meta.append(provider, capability);
    const detail = document.createElement("details");
    detail.className = "detected-model-detail";
    const detailSummary = document.createElement("summary");
    detailSummary.textContent = "详情";
    const detailBody = document.createElement("div");
    detailBody.className = "detected-model-detail-body";
    const path = document.createElement("small");
    path.className = "detected-model-path";
    path.textContent = displayModelPath(model.path);
    path.title = model.path || "";
    const reason = document.createElement("small");
    reason.className = "detected-model-reason";
    reason.textContent = model.reason || "可用";
    detailBody.append(path, reason);
    detail.append(detailSummary, detailBody);
    row.append(main, meta, detail);
    if (model.canDelete) {
      const removeButton = document.createElement("button");
      removeButton.className = "secondary model-cancel detected-model-delete";
      removeButton.type = "button";
      removeButton.textContent = "删除绑定";
      removeButton.addEventListener("click", () => deleteCustomModelBinding(model.provider, model.path));
      row.append(removeButton);
    }
    section.append(row);
  }
  return section;
}

function applySelectedAudioModelToForm() {
  const model = selectedAudioModel();
  if (!model) return false;
  const engine = audioPipelineForModel(model);
  if (engine === "ollama_audio") {
    ensureSelectOption(ollamaTranscriptionModelSelect, model.path_or_id, model.name);
    ollamaTranscriptionModelSelect.value = model.path_or_id;
    return true;
  }
  if (engine === "mlx-whisper") {
    mlxModelPathOrRepo.value = model.path_or_id;
    return true;
  }
  if (engine === "qwen-audio") {
    qwenModelPathOrRepo.value = model.path_or_id;
    return true;
  }
  if (engine === "mlx-vlm-audio") {
    qwenModelPathOrRepo.value = model.path_or_id;
    return true;
  }
  if (engine === "whisper") {
    const whisperId = whisperIdFromDetectedModel(model);
    ensureSelectOption(modelSelect, whisperId, model.name);
    modelSelect.value = whisperId;
    return true;
  }
  showDiagnostic({
    code: "AUDIO_PROVIDER_NOT_CONNECTED",
    title: "模型尚未接入转录流程",
    message: `${providerLabel(model.provider)} / ${model.name} 已检测到，但当前转录适配器无法直接调用该音频模型。`,
    action: "请选择 MLX Whisper、MLX Audio、MLX VLM Audio、Ollama Audio 或项目已管理的 faster-whisper 模型。",
    technical_detail: JSON.stringify(model, null, 2),
  });
  return false;
}

function audioPipelineForModel(model) {
  if (!model?.capabilities?.audio) return "";
  const text = `${model.name || ""} ${model.path_or_id || ""}`.toLowerCase();
  if (model.provider === "ollama") return "ollama_audio";
  if (model.provider === "mlx" && text.includes("whisper")) return "mlx-whisper";
  if (model.provider === "mlx" && isMlxVlmAudioModel(model)) return "mlx-vlm-audio";
  if (model.provider === "mlx" && isQwenAudioModel(model)) return "qwen-audio";
  if ((model.provider === "huggingface" || model.provider === "custom") && whisperIdFromDetectedModel(model)) return "whisper";
  if ((model.provider === "huggingface" || model.provider === "custom") && isMlxVlmAudioModel(model)) return "mlx-vlm-audio";
  if ((model.provider === "huggingface" || model.provider === "custom") && isQwenAudioModel(model)) return "qwen-audio";
  return "";
}

function ensureSelectOption(select, value, label) {
  if ([...select.options].some((option) => option.value === value)) return;
  select.append(new Option(label || value, value));
}

function whisperIdFromDetectedModel(model) {
  const text = `${model.name} ${model.path_or_id}`.toLowerCase();
  const candidates = [
    ["large-v3", /large-v3/],
    ["medium", /medium/],
    ["small", /small/],
    ["base", /base/],
    ["tiny", /tiny/],
  ];
  const found = candidates.find(([, pattern]) => pattern.test(text));
  return found?.[0] || "";
}

async function quickTestSelectedAudioModel() {
  const model = selectedAudioModel();
  if (!model) return;
  audioTestButton.disabled = true;
  audioTestLabel.textContent = "测试中";
  try {
    const response = await fetch("/api/models/audio-test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model_id: model.id,
        provider: model.provider,
        path_or_id: model.path_or_id,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "快速测试失败");
    showDiagnostic({
      code: payload.success ? "AUDIO_MODEL_TEST_OK" : "AUDIO_MODEL_TEST_FAILED",
      title: payload.success ? "快速测试通过" : "快速测试失败",
      message: payload.message,
      action: `latency: ${payload.latency_ms} ms`,
      technical_detail: payload.error || JSON.stringify(model, null, 2),
    });
  } catch (error) {
    showDiagnostic(diagnoseClientError(error.message));
  } finally {
    audioTestButton.disabled = false;
    audioTestLabel.textContent = "快速测试模型";
  }
}

async function registerCustomModel() {
  const pathOrId = customModelPath.value.trim();
  if (!pathOrId) {
    customModelMessage.textContent = "请填写 model path / id。";
    return;
  }
  addCustomModelButton.disabled = true;
  customModelMessage.textContent = "正在注册 custom model";
  try {
    const payload = await postCustomModelRegistration(pathOrId);
    customModelMessage.textContent = `已注册：${payload.name || payload.path_or_id}`;
    await refreshModelRegistry({
      audioModelId: payload.capabilities?.audio ? payload.id : "",
      polishModelPath: payload.capabilities?.text ? payload.path_or_id : "",
    });
    if (payload.capabilities?.audio) {
      selectAudioMode("local_audio_llm");
      applySelectedAudioModelToForm();
      updateEngineControls();
    }
  } catch (error) {
    customModelMessage.textContent = `注册失败：${error.message}`;
  } finally {
    addCustomModelButton.disabled = false;
  }
}

async function deleteCustomModelBinding(provider, pathOrId) {
  const approved = window.confirm(`删除该模型绑定？\n${pathOrId}\n\n不会删除磁盘文件。`);
  if (!approved) return;
  try {
    const params = new URLSearchParams({ provider, path_or_id: pathOrId });
    const response = await fetch(`/api/models/register?${params.toString()}`, { method: "DELETE" });
    const payload = await readJsonResponse(response);
    if (!response.ok) throw new Error(payload.detail || "删除绑定失败");
    customModelMessage.textContent = "已删除模型绑定。";
    await refreshModelRegistry();
  } catch (error) {
    customModelMessage.textContent = `删除绑定失败：${error.message}`;
  }
}

async function postCustomModelRegistration(pathOrId) {
  const modelPayload = customModelPayload(pathOrId);
  const response = await fetch("/api/models/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(modelPayload),
  });
  let payload = await readJsonResponse(response);
  if (response.status !== 405) {
    if (!response.ok) throw new Error(payload.detail || "custom model 注册失败");
    return payload;
  }

  const params = new URLSearchParams({
    provider: modelPayload.provider,
    path_or_id: modelPayload.path_or_id,
    audio: modelPayload.capabilities.audio ? "true" : "false",
    text: modelPayload.capabilities.text ? "true" : "false",
  });
  const retry = await fetch(`/api/models/register?${params.toString()}`, { method: "GET" });
  payload = await readJsonResponse(retry);
  if (!retry.ok) throw new Error(payload.detail || "custom model 注册失败");
  return payload;
}

function scheduleCustomModelProbe() {
  clearTimeout(customModelProbeTimer);
  const pathOrId = customModelPath.value.trim();
  if (!pathOrId) {
    customModelMessage.textContent = "请填写本地模型目录；系统只记录绑定，不自动下载。";
    return;
  }
  customModelMessage.textContent = "正在检测输入的 model path / id";
  customModelProbeTimer = setTimeout(probeCustomModelInput, 350);
}

async function probeCustomModelInput() {
  const pathOrId = customModelPath.value.trim();
  if (!pathOrId) return;
  try {
    const response = await fetch("/api/models/probe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(customModelPayload(pathOrId)),
    });
    const payload = await readJsonResponse(response);
    if (!response.ok) throw new Error(payload.detail || "模型路径检测失败");
    customModelMessage.textContent = customModelProbeMessage(payload);
  } catch (error) {
    customModelMessage.textContent = `检测失败：${error.message}`;
  }
}

function customModelPayload(pathOrId) {
  const capability = customModelCapability.value;
  return {
    provider: customModelProvider.value,
    path_or_id: pathOrId,
    capabilities: {
      audio: capability === "audio" || capability === "audio_text",
      text: capability === "text" || capability === "audio_text",
    },
  };
}

function customModelProbeMessage(model) {
  const exists = model.metadata?.status === "available";
  const capability = capabilityLabel(model.capabilities);
  const engine = audioPipelineForModel(model);
  const audioNote = !exists
    ? "路径不存在，不能用于转录"
    : model.capabilities?.audio
    ? engine
      ? `可用于 ${transcriptionEngineLabel(engine)}`
      : "当前来源暂未接入音频转录"
    : "不含音频能力";
  return `${exists ? "已找到" : "未找到"} · ${providerLabel(model.provider)} · ${capability} · ${audioNote}`;
}

async function pickCustomModelFolder() {
  pickCustomModelFolderButton.disabled = true;
  customModelMessage.textContent = "正在打开文件夹选择器";
  try {
    const path = await pickDirectoryPath();
    if (!path) throw new Error("未选择文件夹");
    customModelPath.value = path;
    customModelPath.dispatchEvent(new Event("input", { bubbles: true }));
    customModelMessage.textContent = "已选择模型文件夹。";
  } catch (error) {
    customModelMessage.textContent = `选择文件夹失败：${error.message}`;
  } finally {
    pickCustomModelFolderButton.disabled = false;
  }
}

async function pickWhisperModelFolder() {
  pickWhisperModelFolderButton.disabled = true;
  whisperModelPathMessage.textContent = "正在打开文件夹选择器";
  try {
    const path = await pickDirectoryPath();
    if (!path) throw new Error("未选择文件夹");
    whisperModelPath.value = path;
    whisperModelPathMessage.textContent = "已选择 Whisper 模型目录。";
  } catch (error) {
    whisperModelPathMessage.textContent = `选择文件夹失败：${error.message}`;
  } finally {
    pickWhisperModelFolderButton.disabled = false;
  }
}

async function bindSelectedWhisperModelPath() {
  const modelId = modelSelect.value;
  const path = whisperModelPath.value.trim();
  if (!modelId) {
    whisperModelPathMessage.textContent = "请先选择 Whisper 模型。";
    return;
  }
  if (!path) {
    whisperModelPathMessage.textContent = "请填写完整模型目录。";
    return;
  }
  bindWhisperModelPathButton.disabled = true;
  whisperModelPathMessage.textContent = "正在写入 Whisper 模型路径配置";
  try {
    const response = await fetch("/api/model/path", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_id: modelId, path }),
    });
    const payload = await readJsonResponse(response);
    if (!response.ok) throw new Error(payload.detail || "绑定失败");
    renderModelStatus(payload);
    whisperModelPathMessage.textContent = "已绑定 Whisper 模型目录。";
  } catch (error) {
    whisperModelPathMessage.textContent = `绑定失败：${error.message}`;
  } finally {
    bindWhisperModelPathButton.disabled = false;
  }
}

async function unbindSelectedWhisperModelPath() {
  const modelId = modelSelect.value;
  if (!modelId) {
    whisperModelPathMessage.textContent = "请先选择 Whisper 模型。";
    return;
  }
  unbindWhisperModelPathButton.disabled = true;
  whisperModelPathMessage.textContent = "正在取消 Whisper 模型目录绑定";
  try {
    const response = await fetch(`/api/model/path/${encodeURIComponent(modelId)}`, { method: "DELETE" });
    const payload = await readJsonResponse(response);
    if (!response.ok) throw new Error(payload.detail || "取消绑定失败");
    renderModelStatus(payload);
    whisperModelPath.value = "";
    whisperModelPathMessage.textContent = "已取消绑定，继续优先检查项目 models 文件夹。";
  } catch (error) {
    whisperModelPathMessage.textContent = `取消绑定失败：${error.message}`;
  } finally {
    unbindWhisperModelPathButton.disabled = false;
  }
}

async function pickDirectoryPath() {
  const electronPath = await pickDirectoryWithDesktopApi();
  if (electronPath) return electronPath;

  try {
    const response = await fetch("/api/models/pick-directory", { method: "POST" });
    const payload = await readJsonResponse(response);
    if (response.ok && payload.path) return payload.path;
    throw new Error(payload.detail || "后端文件夹选择器不可用");
  } catch (backendError) {
    throw new Error(
      `${backendError.message}；浏览器文件夹上传无法提供可靠绝对路径，请手动粘贴模型目录。`,
    );
  }
}

async function pickDirectoryWithDesktopApi() {
  const apis = [
    window.electronAPI?.selectDirectory,
    window.electronAPI?.pickDirectory,
    window.electronAPI?.openDirectory,
    window.api?.selectDirectory,
    window.audioTranscribe?.selectDirectory,
  ].filter((item) => typeof item === "function");
  for (const api of apis) {
    try {
      const result = await api();
      const path = directoryPathFromPickerResult(result);
      if (path) return path;
    } catch {
      continue;
    }
  }
  return "";
}

function directoryPathFromPickerResult(result) {
  if (!result) return "";
  if (typeof result === "string") return result;
  if (Array.isArray(result)) return result[0] || "";
  if (typeof result.path === "string") return result.path;
  if (Array.isArray(result.filePaths)) return result.filePaths[0] || "";
  if (Array.isArray(result.paths)) return result.paths[0] || "";
  return "";
}

async function readJsonResponse(response) {
  const text = await response.text();
  if (!text) return {};
  try {
    return JSON.parse(text);
  } catch {
    return { detail: text };
  }
}

function providerLabel(provider) {
  return {
    ollama: "Ollama",
    mlx: "MLX",
    huggingface: "HuggingFace 本地",
    "llama.cpp": "llama.cpp",
    custom: "自定义目录",
  }[provider] || provider || "未知来源";
}

function capabilityLabel(capabilities) {
  const labels = [];
  if (capabilities?.audio) labels.push("音频");
  if (capabilities?.text) labels.push("文本");
  if (capabilities?.vision) labels.push("视觉");
  return labels.length ? labels.join(" / ") : "未标注能力";
}

function restoreJobsCollapsedState() {
  const collapsed = localStorage.getItem(JOBS_COLLAPSED_KEY) === "1";
  setJobsCollapsed(collapsed);
}

function toggleJobsCollapsed() {
  setJobsCollapsed(!jobsRegion.hidden);
}

function setJobsCollapsed(collapsed) {
  jobsRegion.hidden = collapsed;
  localStorage.setItem(JOBS_COLLAPSED_KEY, collapsed ? "1" : "0");
  jobsCollapseButton.title = collapsed ? "展开任务列表" : "收起任务列表";
  jobsCollapseButton.setAttribute("aria-label", jobsCollapseButton.title);
  jobsCollapseButton.classList.toggle("is-collapsed", collapsed);
}

function promptOverrides() {
  try {
    const parsed = JSON.parse(localStorage.getItem(PROMPT_OVERRIDES_KEY) || "{}");
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function currentProfilePrompt(profile) {
  const overrides = promptOverrides();
  return overrides[profile.id] || profile.default_prompt || profile.prompt_preview || profile.description || "";
}

function openPromptEditor() {
  const profile = primarySelectedPolishProfile();
  if (!profile) return;
  promptModalTitle.textContent = `${profile.label} · 当前 prompt`;
  promptEditor.value = currentProfilePrompt(profile);
  promptModal.showModal();
}

function savePromptOverride() {
  const profile = primarySelectedPolishProfile();
  if (!profile) return;
  const overrides = promptOverrides();
  overrides[profile.id] = promptEditor.value.trim() || profile.default_prompt || "";
  localStorage.setItem(PROMPT_OVERRIDES_KEY, JSON.stringify(overrides));
  promptModal.close();
  updatePromptPreview();
}

function restorePromptDefault() {
  const profile = primarySelectedPolishProfile();
  if (!profile) return;
  const overrides = promptOverrides();
  delete overrides[profile.id];
  localStorage.setItem(PROMPT_OVERRIDES_KEY, JSON.stringify(overrides));
  promptEditor.value = profile.default_prompt || profile.prompt_preview || "";
  updatePromptPreview();
}

function openFixModal() {
  renderFixPlan();
  fixModal.showModal();
}

function renderFixPlan() {
  const mirror = mirrorSourceToggle.checked;
  const items = [...healthList.querySelectorAll(".health-item")]
    .map((node) => node._item)
    .filter((item) => item && item.status !== "success");
  fixPlan.replaceChildren();
  if (!items.length) {
    const done = document.createElement("p");
    done.textContent = "当前没有需要修复的环境项。";
    fixPlan.append(done);
    return;
  }
  for (const item of items) {
    const row = document.createElement("div");
    row.className = "fix-row";
    const title = document.createElement("strong");
    title.textContent = item.label;
    const command = document.createElement("code");
    command.textContent = fixCommandForItem(item, mirror);
    const note = document.createElement("span");
    note.textContent = item.suggestion || item.message || "";
    row.append(title, note, command);
    fixPlan.append(row);
  }
}

function fixCommandForItem(item, mirror) {
  if (item.id === "ffmpeg") return "brew install ffmpeg";
  if (item.id === "faster_whisper") {
    return mirror
      ? "pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple"
      : "pip install -r requirements.txt";
  }
  if (item.id === "mlx_whisper") {
    return mirror ? "pip install mlx-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple" : "pip install mlx-whisper";
  }
  return "请按提示手动处理；本应用不会静默安装。";
}

function setClipRange(startValue, endValue) {
  startTimeInput.value = startValue;
  endTimeInput.value = endValue;
}

function loadMediaDuration(file) {
  const media = document.createElement(file.type.startsWith("video/") ? "video" : "audio");
  const objectUrl = URL.createObjectURL(file);
  media.preload = "metadata";
  media.addEventListener(
    "loadedmetadata",
    () => {
      URL.revokeObjectURL(objectUrl);
      if (!Number.isFinite(media.duration) || media.duration <= 0) return;
      const endValue = formatDurationForTimeInput(media.duration);
      setClipRange("00:00:00", endValue);
      clipDefaultsReady = true;
      clipRangeTouched = false;
    },
    { once: true },
  );
  media.addEventListener(
    "error",
    () => {
      URL.revokeObjectURL(objectUrl);
      clipDefaultsReady = false;
    },
    { once: true },
  );
  media.src = objectUrl;
}

function formatDurationForTimeInput(durationSeconds) {
  const totalSeconds = Math.min(Math.max(0, Math.floor(durationSeconds)), 86399);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return [hours, minutes, seconds].map((part) => String(part).padStart(2, "0")).join(":");
}

function startJobsPolling() {
  clearInterval(jobsPollTimer);
  jobsPollTimer = setInterval(refreshJobs, 1800);
}

async function refreshJobs() {
  const response = await fetch("/api/jobs");
  if (!response.ok) return;
  const jobs = await response.json();
  renderJobs(jobs);
  refreshCleanupStatus();
}

async function refreshCleanupStatus() {
  if (!jobsCleanupStatus || !jobsCleanupButton) return null;
  try {
    const response = await fetch("/api/jobs/cleanup/status");
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "工作文件检查失败");
    renderCleanupStatus(payload);
    return payload;
  } catch (error) {
    jobsCleanupStatus.textContent = `工作文件检查失败：${error.message}`;
    jobsCleanupButton.disabled = true;
    return null;
  }
}

function renderCleanupStatus(status) {
  const files = Number(status.files || 0);
  const bytes = Number(status.bytes || 0);
  const eligible = Number(status.eligible_jobs || 0);
  const active = Number(status.active_jobs || 0);
  jobsCleanupButton.disabled = files <= 0 || active > 0;
  if (active > 0) {
    jobsCleanupStatus.textContent = `有 ${active} 个任务正在处理，完成后可清理过往工作文件。`;
    return;
  }
  jobsCleanupStatus.textContent = files
    ? `可清理 ${eligible} 个过往任务的 ${files} 个工作文件，预计释放 ${formatBytes(bytes)}。`
    : "没有可清理的过往任务工作文件。";
}

async function cleanupJobWorkFiles() {
  const status = await refreshCleanupStatus();
  if (!status || !Number(status.files || 0)) return;
  const approved = window.confirm(
    `清理 ${status.eligible_jobs} 个过往任务的 ${status.files} 个工作文件，预计释放 ${formatBytes(status.bytes)}？\n\n这会删除 data/jobs 下已结束任务的 source、chunk、导出文件等工作文件；运行中的任务不会被删除。`,
  );
  if (!approved) return;

  jobsCleanupButton.disabled = true;
  jobsCleanupStatus.textContent = "正在清理过往任务工作文件。";
  try {
    const response = await fetch("/api/jobs/cleanup", { method: "POST" });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "工作文件清理失败");
    jobsCleanupStatus.textContent = `已清理 ${payload.cleaned_jobs} 个任务目录、${payload.cleaned_files} 个文件，释放 ${formatBytes(payload.cleaned_bytes)}。`;
    await refreshJobs();
  } catch (error) {
    jobsCleanupStatus.textContent = `工作文件清理失败：${error.message}`;
    showDiagnostic(diagnoseClientError(error.message));
  } finally {
    await refreshCleanupStatus();
  }
}

function renderJobs(jobs) {
  const transcriptScrollPositions = captureTranscriptScrollPositions();
  handleJobCompletionNotifications(jobs);
  lastJobs = jobs;
  storeCompletedJobs(jobs);
  const activeCount = jobs.filter((job) => isActiveState(job.state)).length;
  updateWorkbenchJobStats(jobs, activeCount);
  jobSummary.textContent = jobs.length ? `${jobs.length} 个任务，${activeCount} 个进行中或排队` : "等待创建任务";
  submitButton.disabled = submittingJob;
  const seen = new Set();
  const nodes = jobs.map((job) => {
    seen.add(job.id);
    const existing = jobElements.get(job.id);
    const next = renderJob(job);
    next.dataset.jobId = job.id;
    if (existing) {
      existing.replaceChildren(...next.childNodes);
      existing.className = next.className;
      existing.setAttribute("aria-label", next.getAttribute("aria-label") || "");
      return existing;
    }
    next.classList.add("is-new");
    next.addEventListener("animationend", () => next.classList.remove("is-new"), { once: true });
    jobElements.set(job.id, next);
    return next;
  });
  for (const [jobId, node] of jobElements.entries()) {
    if (!seen.has(jobId)) {
      jobElements.delete(jobId);
      node.remove();
    }
  }
  jobsList.replaceChildren(...nodes);
  restoreTranscriptScrollPositions(transcriptScrollPositions);
  if (!jobs.length) {
    jobElements.clear();
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "还没有任务。提交后会在这里显示队列、进度和文件。";
    jobsList.append(empty);
  }
}

function updateWorkbenchJobStats(jobs, activeCount = jobs.filter((job) => isActiveState(job.state)).length) {
  const completedCount = jobs.filter((job) => job.state === "completed").length;
  const failedCount = jobs.filter((job) => job.state === "failed").length;
  if (jobCountTotal) jobCountTotal.textContent = String(jobs.length);
  if (jobCountActive) jobCountActive.textContent = String(activeCount);
  if (jobCountCompleted) jobCountCompleted.textContent = String(completedCount);
  if (jobCountFailed) jobCountFailed.textContent = String(failedCount);
}

function initCompletionNotificationBadges() {
  for (const target of completionNotificationTargets()) {
    if (!target || target.querySelector(".completion-dot")) continue;
    const dot = document.createElement("span");
    dot.className = "completion-dot";
    dot.hidden = true;
    target.append(dot);
  }
  renderCompletionBadges();
}

function completionNotificationTargets() {
  return [jobsNavButton, headerOpenJobsButton].filter(Boolean);
}

function handleJobCompletionNotifications(jobs) {
  const nextSnapshot = new Map(jobs.map((job) => [job.id, job.state]));
  if (!jobCompletionTrackerReady) {
    for (const job of jobs) {
      if (isActiveState(job.state)) watchedCompletionJobIds.add(job.id);
    }
    jobStateSnapshot = nextSnapshot;
    jobCompletionTrackerReady = true;
    return;
  }

  const completedNow = jobs.filter((job) => {
    const previousState = jobStateSnapshot.get(job.id);
    if (isActiveState(job.state)) watchedCompletionJobIds.add(job.id);
    if (job.state !== "completed" || notifiedCompletionJobIds.has(job.id)) return false;
    return (
      watchedCompletionJobIds.has(job.id) ||
      (previousState && previousState !== "completed" && !terminalJobState(previousState))
    );
  });
  jobStateSnapshot = nextSnapshot;
  if (!completedNow.length) return;
  completedNow.forEach((job) => {
    notifiedCompletionJobIds.add(job.id);
    watchedCompletionJobIds.delete(job.id);
  });
  unreadCompletedJobs += completedNow.length;
  renderCompletionBadges();
  showCompletionToast(completedNow);
}

function renderCompletionBadges() {
  for (const target of completionNotificationTargets()) {
    const dot = target.querySelector(".completion-dot");
    if (!dot) continue;
    dot.hidden = unreadCompletedJobs <= 0;
    dot.textContent = unreadCompletedJobs > 9 ? "9+" : String(unreadCompletedJobs);
    const baseLabel = target.dataset.baseAriaLabel || target.getAttribute("aria-label") || target.textContent.trim() || "文件任务";
    target.dataset.baseAriaLabel = baseLabel;
    target.setAttribute(
      "aria-label",
      unreadCompletedJobs > 0 ? `${baseLabel}，${unreadCompletedJobs} 个任务已完成` : baseLabel,
    );
  }
}

function clearCompletionNotifications() {
  unreadCompletedJobs = 0;
  renderCompletionBadges();
}

function showCompletionToast(jobs) {
  if (!completionToast) return;
  const first = jobs[0];
  const suffix = jobs.length > 1 ? `等 ${jobs.length} 个任务` : first.source_label || `任务 ${shortId(first.id)}`;
  completionToast.textContent = `${suffix} 已完成，可在文件任务中查看结果。`;
  completionToast.hidden = false;
  window.clearTimeout(completionToastTimer);
  completionToastTimer = window.setTimeout(() => {
    completionToast.hidden = true;
  }, 5200);
}

function captureTranscriptScrollPositions() {
  const positions = new Map();
  jobsList.querySelectorAll(".transcript-block pre[data-scroll-key]").forEach((node) => {
    positions.set(node.dataset.scrollKey, {
      top: node.scrollTop,
      left: node.scrollLeft,
    });
  });
  return positions;
}

function restoreTranscriptScrollPositions(positions) {
  if (!positions.size) return;
  jobsList.querySelectorAll(".transcript-block pre[data-scroll-key]").forEach((node) => {
    const position = positions.get(node.dataset.scrollKey);
    if (!position) return;
    node.scrollTop = position.top;
    node.scrollLeft = position.left;
  });
}

function loadHistory() {
  try {
    const parsed = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    return Array.isArray(parsed) ? parsed.slice(0, HISTORY_LIMIT) : [];
  } catch {
    return [];
  }
}

function saveHistory(items) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, HISTORY_LIMIT)));
}

function storeCompletedJobs(jobs) {
  const completed = jobs.filter((job) => ["completed", "failed", "cancelled"].includes(job.state));
  if (!completed.length) return;
  const current = loadHistory();
  const byId = new Map(current.map((item) => [item.taskId, item]));
  for (const job of completed) {
    if (!job.raw_text && !job.polished_text && job.state !== "failed" && job.state !== "cancelled") continue;
    byId.set(job.id, historySnapshot(job));
  }
  const next = [...byId.values()]
    .sort((a, b) => Date.parse(b.createdAt || "") - Date.parse(a.createdAt || ""))
    .slice(0, HISTORY_LIMIT);
  saveHistory(next);
  renderHistory(next);
}

function historySnapshot(job) {
  return {
    taskId: job.id,
    fileName: job.source_label || `任务 ${shortId(job.id)}`,
    createdAt: job.created_at,
    language: job.language,
    whisperModel: job.whisper_model_id || job.transcription_model_id || job.model_label,
    polishProfile: job.polish_profile_label || "",
    polishModel: job.polish_model_id || "",
    status: job.state,
    elapsed: elapsedLabel(job),
    rawTranscript: limitHistoryText(job.raw_text || ""),
    polishedTranscript: limitHistoryText(job.polished_text || ""),
    segments: job.has_segments ? "available" : "none",
  };
}

function limitHistoryText(text) {
  const value = String(text || "");
  return value.length > HISTORY_TEXT_LIMIT ? value.slice(0, HISTORY_TEXT_LIMIT) : value;
}

function renderHistory(items) {
  historyMessage.textContent = items.length ? `${items.length} 条历史，最多保留 ${HISTORY_LIMIT} 条` : `最近 ${HISTORY_LIMIT} 条结果保存在当前浏览器。`;
  historyList.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "empty compact-empty";
    empty.textContent = "暂无历史记录。";
    historyList.append(empty);
    return;
  }
  for (const item of items) {
    const button = document.createElement("button");
    button.className = `history-item${selectedHistoryJobId === item.taskId ? " is-selected" : ""}`;
    button.type = "button";
    button.textContent = `${item.fileName} · ${stateLabel(item.status)} · ${item.elapsed}`;
    button.addEventListener("click", () => {
      selectedHistoryJobId = item.taskId;
      renderHistory(loadHistory());
      showHistorySnapshot(item);
    });
    historyList.append(button);
  }
}

function showHistorySnapshot(item) {
  const pseudoJob = {
    id: item.taskId,
    source_label: item.fileName,
    state: item.status,
    language: item.language,
    model_label: item.whisperModel,
    polish_profile_label: item.polishProfile,
    polish_model_id: item.polishModel,
    raw_text: item.rawTranscript,
    polished_text: item.polishedTranscript,
    events: [],
    outputs: [],
    warnings: [],
    formats: [],
    include_timestamps: false,
  };
  jobsList.prepend(renderJob(pseudoJob));
}

function isActiveState(state) {
  return ["queued", "validating", "preparing_model", "transcribing", "polishing"].includes(state);
}

function renderJob(job) {
  const item = document.createElement("article");
  item.className = `job-item state-${job.state}`;
  item.dataset.jobId = job.id;
  item.setAttribute("aria-label", `${stateLabel(job.state)}：${job.source_label || `任务 ${shortId(job.id)}`}`);

  const header = document.createElement("div");
  header.className = "job-head";

  const titleWrap = document.createElement("div");
  titleWrap.className = "job-title-wrap";
  const title = document.createElement("h3");
  const titleText = job.source_label || `任务 ${shortId(job.id)}`;
  if (job.source_url) {
    const titleLink = document.createElement("a");
    titleLink.className = "job-title-link";
    titleLink.href = job.source_url;
    titleLink.target = "_blank";
    titleLink.rel = "noreferrer";
    titleLink.textContent = titleText;
    title.append(titleLink);
  } else {
    title.textContent = titleText;
  }
  const meta = document.createElement("p");
  meta.className = "job-meta";
  meta.textContent = `任务 ${shortId(job.id)} · ${jobMeta(job)}`;
  titleWrap.append(title, meta);

  const pill = document.createElement("span");
  pill.className = `pill state-badge state-${job.state}`;
  pill.textContent = stateLabel(job.state);
  const isCollapsed = collapsedJobIds.has(job.id);
  const headerActions = document.createElement("div");
  headerActions.className = "job-head-actions";
  const toggleButton = document.createElement("button");
  toggleButton.className = `job-toggle${isCollapsed ? " is-collapsed" : ""}`;
  toggleButton.type = "button";
  toggleButton.setAttribute("aria-expanded", String(!isCollapsed));
  toggleButton.setAttribute("aria-label", isCollapsed ? "展开任务" : "收起任务");
  toggleButton.title = isCollapsed ? "展开任务" : "收起任务";
  toggleButton.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
  toggleButton.addEventListener("click", () => toggleJobCollapsed(job.id));
  headerActions.append(pill, toggleButton);
  header.append(titleWrap, headerActions);

  const bar = document.createElement("div");
  bar.className = "job-progress";
  const progress = Math.max(0, Math.min(100, Number(job.progress || 0)));
  bar.style.setProperty("--progress", progress);
  bar.setAttribute("role", "progressbar");
  bar.setAttribute("aria-label", "任务进度");
  bar.setAttribute("aria-valuemin", "0");
  bar.setAttribute("aria-valuemax", "100");
  bar.setAttribute("aria-valuenow", String(progress));
  const barFill = document.createElement("span");
  bar.append(barFill);

  const progressMeta = document.createElement("div");
  progressMeta.className = "job-progress-meta";
  const progressLabel = document.createElement("span");
  progressLabel.textContent = stateLabel(job.state);
  const progressValue = document.createElement("strong");
  progressValue.textContent = `${progress}%`;
  progressMeta.append(progressLabel, progressValue);

  const message = document.createElement("p");
  message.className = "job-message";
  message.textContent = job.error || job.message || "";

  const details = document.createElement("div");
  details.className = "job-details";
  for (const detail of jobDetails(job)) {
    const row = document.createElement("div");
    row.className = "job-detail";
    const label = document.createElement("span");
    label.textContent = detail.label;
    const value = document.createElement("strong");
    value.textContent = detail.value;
    row.append(label, value);
    details.append(row);
  }

  if (modelUsesCpu(job.model_label)) {
    const warning = document.createElement("div");
    warning.className = "job-warning";
    warning.textContent = "当前任务使用 CPU 转写，速度会明显慢于 CUDA。";
    details.append(warning);
  }

  const actions = document.createElement("div");
  actions.className = "job-actions";
  if (isActiveState(job.state)) {
    const stopButton = document.createElement("button");
    stopButton.className = "danger job-action-button";
    stopButton.type = "button";
    stopButton.textContent = "停止";
    stopButton.addEventListener("click", () => cancelJob(job.id, stopButton));
    actions.append(stopButton);
  }
  if (job.raw_text) {
    const copyRawButton = document.createElement("button");
    copyRawButton.className = "secondary job-action-button";
    copyRawButton.type = "button";
    copyRawButton.textContent = "复制原始文本";
    copyRawButton.addEventListener("click", () => copyText(job.raw_text, copyRawButton));
    actions.append(copyRawButton);
  }
  if (job.polished_text) {
    const copyPolishedButton = document.createElement("button");
    copyPolishedButton.className = "secondary job-action-button";
    copyPolishedButton.type = "button";
    copyPolishedButton.textContent = "复制整理后文本";
    copyPolishedButton.addEventListener("click", () => copyText(job.polished_text, copyPolishedButton));
    actions.append(copyPolishedButton);
  }
  if (job.raw_text && job.polished_text) {
    const compareButton = document.createElement("button");
    compareButton.className = "secondary job-action-button";
    compareButton.type = "button";
    compareButton.textContent = compareExpandedJobIds.has(job.id) ? "收起对比" : "对比";
    compareButton.setAttribute("aria-expanded", String(compareExpandedJobIds.has(job.id)));
    compareButton.addEventListener("click", () => toggleCompare(job.id));
    actions.append(compareButton);
  }
  if (job.raw_text && !isActiveState(job.state)) {
    const rerunButton = document.createElement("button");
    rerunButton.className = "secondary job-action-button";
    rerunButton.type = "button";
    rerunButton.textContent = "重新整理";
    rerunButton.addEventListener("click", () => rerunPolish(job.id, rerunButton));
    actions.append(rerunButton);
  }
  if (terminalJobState(job.state)) {
    const deleteRecordButton = document.createElement("button");
    deleteRecordButton.className = "danger ghost job-action-button";
    deleteRecordButton.type = "button";
    deleteRecordButton.textContent = "删除记录";
    deleteRecordButton.addEventListener("click", () => deleteJobRecord(job.id, job.source_label));
    actions.append(deleteRecordButton);
  }

  const outputs = document.createElement("div");
  outputs.className = "outputs";
  for (const file of job.outputs || []) {
    outputs.append(renderOutput(job.id, file));
  }

  const warnings = document.createElement("div");
  warnings.className = "job-warnings";
  for (const warningText of job.warnings || []) {
    const warning = document.createElement("div");
    warning.className = "job-warning";
    warning.textContent = warningText;
    warnings.append(warning);
  }

  const events = renderJobEvents(job.events || []);
  const stages = renderStageTimeline(job);
  const transcripts = renderTranscripts(job);
  const diagnostic = renderJobDiagnostic(job);

  const body = document.createElement("div");
  body.className = "job-body";
  body.hidden = isCollapsed;
  body.append(actions, outputs, details, diagnostic, warnings, stages, transcripts);
  if (job.raw_text && job.polished_text && compareExpandedJobIds.has(job.id)) {
    body.append(renderCompareView(job));
  }
  body.append(events);

  item.classList.toggle("is-collapsed", isCollapsed);
  item.append(header, progressMeta, bar, message, body);
  return item;
}

function renderStageTimeline(job) {
  const wrap = document.createElement("div");
  wrap.className = "stage-timeline";
  const stages = stageRows(job);
  if (!stages.length) return wrap;
  for (const stage of stages) {
    const row = document.createElement("div");
    row.className = `stage-row stage-${stage.status}`;
    const label = document.createElement("strong");
    label.textContent = stage.label;
    const value = document.createElement("span");
    value.textContent = stage.duration ? `${stage.statusLabel} · ${stage.duration}` : stage.statusLabel;
    row.append(label, value);
    if (stage.slowHint) {
      const hint = document.createElement("small");
      hint.textContent = stage.slowHint;
      row.append(hint);
    }
    wrap.append(row);
  }
  return wrap;
}

function stageRows(job) {
  const events = job.events || [];
  const createdAt = Date.parse(job.created_at || "");
  const finishedAt = Date.parse(job.processing_finished_at || "");
  const now = Date.now();
  const started = Date.parse(job.processing_started_at || job.created_at || "");
  const definitions = [
    { id: "validating", label: "文件校验", start: createdAt, end: eventTimeAny(events, ["Mock 模式：跳过音频标准化", "mock mode skipped audio normalization", "Whisper 转录开始", "whisper transcription started", "MLX Whisper 转录开始", "mlx whisper transcription started", "Qwen2-Audio 多模态音频理解开始"]) },
    { id: "preparing_model", label: "模型准备", start: eventTimeAny(events, ["Whisper 转录开始", "whisper transcription started", "MLX Whisper 转录开始", "mlx whisper transcription started", "Qwen2-Audio 多模态音频理解开始"]) || started, end: eventTimeAny(events, ["Whisper 转录完成", "whisper transcription completed", "MLX Whisper 转录完成", "mlx whisper transcription completed", "Qwen2-Audio 多模态音频理解完成"]) },
    { id: "transcribing", label: "转录", start: eventTimeAny(events, ["Whisper 转录开始", "whisper transcription started", "MLX Whisper 转录开始", "mlx whisper transcription started", "Qwen2-Audio 多模态音频理解开始", "本地大模型音频转录开始", "ollama direct audio started"]), end: eventTimeAny(events, ["Whisper 转录完成", "whisper transcription completed", "MLX Whisper 转录完成", "mlx whisper transcription completed", "Qwen2-Audio 多模态音频理解完成", "本地大模型音频转录完成", "ollama direct audio completed"]) },
    { id: "polishing", label: "文本整理", start: eventTimeAny(events, ["文本整理开始", "polish started", "重新执行文本整理", "polish rerun started"]), end: eventTimeAny(events, ["文本整理完成", "polish completed"]) },
    { id: "exporting", label: "导出准备", start: eventTimeAny(events, ["导出文件已生成", "export generated"]) ? null : eventTimeAny(events, ["文本整理完成", "polish completed"]), end: eventTimeAny(events, ["导出文件已生成", "export generated"]) },
  ];
  return definitions
    .filter((stage) => stage.start || stage.end || job.state === stage.id)
    .map((stage) => {
      const active = job.state === stage.id;
      const end = stage.end || (active ? now : Number.isFinite(finishedAt) ? finishedAt : null);
      const durationSeconds = stage.start && end ? Math.max(0, Math.floor((end - stage.start) / 1000)) : null;
      const status = active ? "active" : stage.end || terminalJobState(job.state) ? "done" : "pending";
      return {
        label: stage.label,
        status,
        statusLabel: status === "active" ? "进行中" : status === "done" ? "完成" : "等待",
        duration: durationSeconds === null ? "" : formatElapsed(durationSeconds),
        slowHint: active && durationSeconds !== null && durationSeconds > 180 ? "该阶段耗时较长，请检查模型、硬件或网络状态。" : "",
      };
    });
}

function eventTime(events, pattern) {
  const found = events.find((event) => String(event.message || "").includes(pattern));
  const value = Date.parse(found?.time || "");
  return Number.isFinite(value) ? value : null;
}

function eventTimeAny(events, patterns) {
  for (const pattern of patterns) {
    const value = eventTime(events, pattern);
    if (value) return value;
  }
  return null;
}

function terminalJobState(state) {
  return ["completed", "failed", "cancelled"].includes(state);
}

function renderJobDiagnostic(job) {
  const wrap = document.createElement("div");
  if (!job.error_diagnostic && !job.error) return wrap;
  const diagnostic = job.error_diagnostic || diagnoseClientError(job.error);
  wrap.className = "job-diagnostic";
  const title = document.createElement("strong");
  title.textContent = diagnostic.title || "任务失败";
  const message = document.createElement("p");
  message.textContent = diagnostic.message || job.error || "";
  const action = document.createElement("p");
  action.className = "diagnostic-action";
  action.textContent = diagnostic.action || "检查环境后重试。";
  wrap.append(title, message, action);
  if (diagnostic.technical_detail) {
    const detail = document.createElement("details");
    detail.open = openDiagnosticDetailJobIds.has(job.id);
    detail.addEventListener("toggle", () => {
      if (detail.open) {
        openDiagnosticDetailJobIds.add(job.id);
      } else {
        openDiagnosticDetailJobIds.delete(job.id);
      }
      storeIdSet(JOB_DIAGNOSTIC_DETAIL_OPEN_KEY, openDiagnosticDetailJobIds);
    });
    const summary = document.createElement("summary");
    summary.textContent = "技术细节";
    const pre = document.createElement("pre");
    pre.textContent = diagnostic.technical_detail;
    detail.append(summary, pre);
    wrap.append(detail);
  }
  return wrap;
}

function toggleJobCollapsed(jobId) {
  if (collapsedJobIds.has(jobId)) {
    collapsedJobIds.delete(jobId);
  } else {
    collapsedJobIds.add(jobId);
  }
  storeIdSet(JOB_DETAIL_COLLAPSED_KEY, collapsedJobIds);
  rerenderKnownJobs();
}

function toggleCompare(jobId) {
  if (compareExpandedJobIds.has(jobId)) {
    compareExpandedJobIds.delete(jobId);
  } else {
    compareExpandedJobIds.add(jobId);
    collapsedJobIds.delete(jobId);
    storeIdSet(JOB_DETAIL_COLLAPSED_KEY, collapsedJobIds);
  }
  storeIdSet(JOB_COMPARE_EXPANDED_KEY, compareExpandedJobIds);
  rerenderKnownJobs();
}

function rerenderKnownJobs() {
  if (lastJobs.length) {
    renderJobs(lastJobs);
    return;
  }
  refreshJobs();
}

function loadStoredIdSet(key) {
  try {
    const parsed = JSON.parse(localStorage.getItem(key) || "[]");
    return new Set(Array.isArray(parsed) ? parsed.filter(Boolean) : []);
  } catch {
    return new Set();
  }
}

function storeIdSet(key, values) {
  localStorage.setItem(key, JSON.stringify([...values].slice(0, 80)));
}

function renderCompareView(job) {
  const wrap = document.createElement("section");
  wrap.className = "compare-view";
  const heading = document.createElement("h4");
  heading.textContent = `文本整理对比 · ${job.polish_profile_label || "未记录配置"} · ${job.polish_model_id || "未记录模型"}`;
  wrap.append(heading);
  const rows = compareParagraphs(job.raw_text || "", job.polished_text || "");
  if (differenceRatio(job.raw_text || "", job.polished_text || "") > 0.55) {
    const warning = document.createElement("div");
    warning.className = "job-warning";
    warning.textContent = "原始文本和整理后文本差异较大，建议使用“保守清理”重新整理。";
    wrap.append(warning);
  }
  const grid = document.createElement("div");
  grid.className = "compare-grid";
  const rawLabel = document.createElement("strong");
  rawLabel.className = "compare-column-label";
  rawLabel.textContent = "原始文本";
  const polishedLabel = document.createElement("strong");
  polishedLabel.className = "compare-column-label";
  polishedLabel.textContent = "整理后文本";
  grid.append(rawLabel, polishedLabel);
  for (const row of rows) {
    const raw = document.createElement("pre");
    raw.textContent = row.raw;
    raw.dataset.changed = row.changed ? "true" : "false";
    const polished = document.createElement("pre");
    polished.textContent = row.polished;
    polished.dataset.changed = row.changed ? "true" : "false";
    grid.append(raw, polished);
  }
  wrap.append(grid);
  return wrap;
}

function compareParagraphs(rawText, polishedText) {
  const rawParts = splitParagraphs(rawText);
  const polishedParts = splitParagraphs(polishedText);
  const length = Math.max(rawParts.length, polishedParts.length);
  return Array.from({ length }, (_, index) => {
    const raw = rawParts[index] || "";
    const polished = polishedParts[index] || "";
    return { raw, polished, changed: raw.trim() !== polished.trim() };
  });
}

function splitParagraphs(text) {
  return String(text || "")
    .split(/\n{2,}/)
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 30);
}

function differenceRatio(rawText, polishedText) {
  const raw = String(rawText || "");
  const polished = String(polishedText || "");
  const maxLength = Math.max(raw.length, polished.length, 1);
  return Math.abs(raw.length - polished.length) / maxLength;
}

function renderTranscripts(job) {
  const wrap = document.createElement("div");
  wrap.className = "transcripts";
  if (!job.raw_text && !job.polished_text) return wrap;

  if (job.raw_text) {
    wrap.append(renderTranscriptBlock("原始转录文本", job.raw_text, job.id, "raw"));
  }
  if (job.polished_text) {
    wrap.append(renderTranscriptBlock("整理后转录文本", job.polished_text, job.id, "polished"));
  }
  return wrap;
}

function renderTranscriptBlock(title, text, jobId, kind) {
  const block = document.createElement("section");
  block.className = "transcript-block";
  const heading = document.createElement("h4");
  heading.textContent = title;
  const body = document.createElement("pre");
  body.dataset.scrollKey = `${jobId}:${kind}`;
  body.textContent = truncateText(text, 1800);
  block.append(heading, body);
  return block;
}

function renderJobEvents(events) {
  const wrap = document.createElement("div");
  wrap.className = "job-events";
  if (!events.length) return wrap;

  const title = document.createElement("h4");
  title.textContent = "事件";
  wrap.append(title);

  for (const event of events) {
    const row = document.createElement("div");
    row.className = "job-event";
    row.dataset.level = event.level || "info";
    const time = document.createElement("time");
    time.dateTime = event.time || "";
    time.textContent = eventTimeLabel(event.time);
    const level = document.createElement("span");
    level.textContent = event.level || "info";
    const message = document.createElement("strong");
    message.textContent = event.message || "";
    row.append(time, level, message);
    wrap.append(row);
  }
  return wrap;
}

function renderOutput(jobId, file) {
  const row = document.createElement("div");
  row.className = "output-row";

  const link = document.createElement("a");
  link.className = "download";
  link.href = file.download_url;
  link.download = file.name;
  link.textContent = file.name;

  const size = document.createElement("small");
  size.textContent = file.saved_path ? `${formatBytes(file.bytes)} · 已存储到 ${file.saved_path}` : formatBytes(file.bytes);

  const deleteButton = document.createElement("button");
  deleteButton.className = "danger ghost";
  deleteButton.type = "button";
  deleteButton.textContent = "删除";
  deleteButton.addEventListener("click", () => deleteOutput(jobId, file.name));

  row.append(link, size, deleteButton);
  return row;
}

async function cancelJob(jobId, button) {
  if (button) {
    button.disabled = true;
    button.textContent = "正在停止";
  }
  const response = await fetch(`/api/jobs/${jobId}/cancel`, { method: "POST" });
  if (!response.ok) {
    if (button) {
      button.disabled = false;
      button.textContent = "停止";
    }
    const payload = await response.json().catch(() => ({}));
    showDiagnostic(diagnoseClientError(payload.detail || "停止任务失败", "TASK_CANCELLED"));
    return;
  }
  await refreshJobs();
}

async function rerunPolish(jobId, button) {
  if (!enablePolishInput.checked) {
    enablePolishInput.checked = true;
    updatePolishControls();
  }
  button.disabled = true;
  button.textContent = "整理中";
  try {
    const response = await fetch(`/api/jobs/${jobId}/polish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model_id: polishModelSelect.value || "",
        profile_id: selectedPolishProfileIds().join(",") || "repair",
        custom_instruction: effectivePolishInstructionValue(),
        export_scope: form.querySelector('input[name="export_scope"]:checked')?.value || "raw",
        formats: [...form.querySelectorAll('input[name="formats"]:checked')].map((input) => input.value),
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "重新整理失败");
    }
    await refreshJobs();
  } catch (error) {
    showDiagnostic(diagnoseClientError(error.message));
  } finally {
    button.disabled = false;
    button.textContent = "重新整理";
  }
}

async function copyText(text, button) {
  try {
    await navigator.clipboard.writeText(text || "");
    const previous = button.textContent;
    button.textContent = "已复制";
    setTimeout(() => {
      button.textContent = previous;
    }, 1200);
  } catch (error) {
    showDiagnostic(diagnoseClientError(`复制失败：${error.message}`));
  }
}

async function deleteOutput(jobId, fileName) {
  const approved = window.confirm(`删除转录文件 ${fileName}？`);
  if (!approved) return;
  const response = await fetch(`/api/jobs/${jobId}/outputs/${encodeURIComponent(fileName)}`, { method: "DELETE" });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    showDiagnostic(diagnoseClientError(payload.detail || "删除导出文件失败"));
    return;
  }
  await refreshJobs();
}

async function deleteJobRecord(jobId, sourceLabel = "") {
  const name = sourceLabel || `任务 ${shortId(jobId)}`;
  const approved = window.confirm(`删除转录记录 ${name}？已自动存储或已下载的文件不会被删除。`);
  if (!approved) return;
  const response = await fetch(`/api/jobs/${jobId}`, { method: "DELETE" });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    showDiagnostic(diagnoseClientError(payload.detail || "删除任务记录失败"));
    return;
  }
  removeHistoryItem(jobId);
  selectedHistoryJobId = selectedHistoryJobId === jobId ? null : selectedHistoryJobId;
  renderJobs(Array.isArray(payload) ? payload : []);
}

function removeHistoryItem(jobId) {
  const next = loadHistory().filter((item) => item.taskId !== jobId);
  saveHistory(next);
  renderHistory(next);
}

function showDiagnostic(diagnostic) {
  diagnosticCard.hidden = false;
  diagnosticCard.replaceChildren();
  const title = document.createElement("strong");
  title.textContent = diagnostic.title || "需要处理";
  const message = document.createElement("p");
  message.textContent = diagnostic.message || "";
  const action = document.createElement("p");
  action.className = "diagnostic-action";
  action.textContent = diagnostic.action || "";
  const close = document.createElement("button");
  close.className = "secondary";
  close.type = "button";
  close.textContent = "关闭";
  close.addEventListener("click", () => {
    diagnosticCard.hidden = true;
  });
  diagnosticCard.append(title, message, action, close);
  if (diagnostic.technical_detail) {
    const detail = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "技术细节";
    const pre = document.createElement("pre");
    pre.textContent = diagnostic.technical_detail;
    detail.append(summary, pre);
    diagnosticCard.append(detail);
  }
}

function diagnoseClientError(message, codeHint) {
  const text = String(message || "");
  const lower = text.toLowerCase();
  if (codeHint === "EXPORT_FORMAT_MISSING") {
    return {
      code: "EXPORT_FORMAT_MISSING",
      title: "未选择导出格式",
      message: text,
      action: "至少选择 TXT、Markdown、JSON、SRT 或 Word 中的一种。",
      technical_detail: text,
    };
  }
  if (text.includes("Ollama 服务不可用") || lower.includes("failed to fetch")) {
    return {
      code: "OLLAMA_NOT_RUNNING",
      title: "Ollama 未运行",
      message: "本地 Ollama 服务不可用。",
      action: "启动 Ollama 桌面应用，或执行 ollama serve 后重试。",
      technical_detail: text,
    };
  }
  if (text.includes("未检测到") && (lower.includes("gemma") || lower.includes("ollama"))) {
    return {
      code: "OLLAMA_MODEL_MISSING",
      title: "Ollama 模型缺失",
      message: "所选 Ollama 模型不在本地模型列表中。",
      action: "切换到已安装模型；如需新增模型，请在应用外手动安装。",
      technical_detail: text,
    };
  }
  if (lower.includes("ffmpeg")) {
    return {
      code: "FFMPEG_MISSING",
      title: "FFmpeg 不可用",
      message: "音频预处理无法继续。",
      action: "安装 FFmpeg，或设置 AUDIO_TRANSCRIBE_FFMPEG。",
      technical_detail: text,
    };
  }
  if (lower.includes("mlx whisper") || lower.includes("mlx-whisper") || lower.includes("mlx_whisper")) {
    return {
      code: "MLX_WHISPER_UNAVAILABLE",
      title: "MLX Whisper 不可用",
      message: text,
      action: "确认当前是 Apple Silicon Mac、已自行安装 mlx-whisper，并填写本地 MLX 模型目录或已缓存 repo id。",
      technical_detail: text,
    };
  }
  if (lower.includes("mlx vlm") || lower.includes("mlx-vlm") || lower.includes("gemma4 mlx vlm audio")) {
    return {
      code: "MLX_VLM_AUDIO_UNAVAILABLE",
      title: "Gemma4 MLX Audio 不可用",
      message: "Gemma4 MLX 多模态音频转录前置条件未满足。",
      action: "确认项目 .venv 已安装 mlx-vlm，并选择本地 Gemma4 MLX Audio/Text 模型目录。",
      technical_detail: text,
    };
  }
  if (text.includes("STT 后端不支持") || lower.includes("not supported for stt")) {
    return {
      code: "AUDIO_MODEL_UNSUPPORTED",
      title: "音频模型暂未接入",
      message: "所选模型不能被当前 MLX Audio STT 转录管线调用。",
      action: "切换到 Qwen2-Audio MLX 模型，或使用 Whisper / MLX Whisper。Gemma 音频模型需要新的本地多模态适配器后才能用于转录。",
      technical_detail: text,
    };
  }
  if (lower.includes("qwen2-audio") || lower.includes("qwen-audio") || lower.includes("mlx-audio") || lower.includes("mlx audio")) {
    return {
      code: "QWEN_AUDIO_UNAVAILABLE",
      title: "MLX Audio 不可用",
      message: text,
      action: "确认当前是 Apple Silicon Mac、已自行安装 mlx-audio，并填写本地 MLX Audio 模型目录或已缓存 repo id。",
      technical_detail: text,
    };
  }
  if (text.includes("任务已停止")) {
    return {
      code: "TASK_CANCELLED",
      title: "任务已取消",
      message: "当前任务已停止。",
      action: "需要时重新提交任务。",
      technical_detail: text,
    };
  }
  return {
    code: "UNKNOWN_ERROR",
    title: "操作失败",
    message: text || "请求未完成。",
    action: "查看技术细节，确认环境检查通过后重试。",
    technical_detail: text,
  };
}

function stateLabel(state) {
  return {
    queued: "排队中",
    validating: "校验中",
    preparing_model: "准备模型",
    transcribing: "转录中",
    polishing: "文本整理中",
    completed: "已完成",
    failed: "失败",
    cancelled: "已取消",
  }[state] || state;
}

function shortId(id) {
  return String(id || "").slice(0, 10);
}

function jobDetails(job) {
  const details = [
    { label: "引擎", value: transcriptionEngineLabel(job.transcription_engine) },
    { label: "语言", value: languageLabel(job.language) },
    { label: "截取", value: timeRangeLabel(job.start_time, job.end_time) },
    { label: "模型", value: job.model_label || "未记录" },
    { label: "文本整理", value: job.enable_polish ? job.polish_model_id || "已启用" : "未启用" },
    { label: "格式", value: job.formats?.length ? job.formats.map(formatLabel).join(" / ") : "未选择" },
    { label: "时间轴", value: job.include_timestamps ? "带时间轴" : "纯文本" },
    { label: "耗时", value: elapsedLabel(job) },
  ];
  if (job.auto_save_outputs) {
    details.push({ label: "自动存储", value: job.auto_save_dir || "等待保存到音频目录" });
  }
  return details;
}

function elapsedLabel(job) {
  const start = Date.parse(job.processing_started_at || job.created_at || "");
  if (!Number.isFinite(start)) return "等待开始";
  const finished = Date.parse(job.processing_finished_at || "");
  const end = Number.isFinite(finished) ? finished : Date.now();
  return formatElapsed(Math.max(0, Math.floor((end - start) / 1000)));
}

function formatElapsed(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return [hours, minutes, seconds].map((part) => String(part).padStart(2, "0")).join(":");
}

function modelUsesCpu(modelLabel) {
  return /\(cpu\//i.test(modelLabel || "");
}

function jobMeta(job) {
  const details = [
    `语言：${languageLabel(job.language)}`,
    `截取：${timeRangeLabel(job.start_time, job.end_time)}`,
    `模型：${job.model_label || "未记录"}`,
  ];
  if (job.formats?.length) {
    details.push(`格式：${job.formats.map(formatLabel).join("、")}`);
  }
  details.push(job.include_timestamps ? "带时间轴" : "纯文本");
  return details.join(" · ");
}

function languageLabel(language) {
  return {
    auto: "自动识别",
    zh: "中文",
    ja: "日语",
    en: "英语",
    ko: "韩语",
  }[language] || language || "自动识别";
}

function transcriptionEngineLabel(engine) {
  return {
    whisper: "Whisper",
    "mlx-whisper": "MLX Whisper",
    ollama_audio: "本地大模型音频转录",
    "qwen-audio": "MLX Audio",
    "mlx-vlm-audio": "MLX VLM Audio",
  }[engine] || engine || "Whisper";
}

function timeRangeLabel(startTime, endTime) {
  if (startTime && endTime) return `${startTime} - ${endTime}`;
  if (startTime) return `${startTime} 起`;
  if (endTime) return `截至 ${endTime}`;
  return "完整音频";
}

function formatLabel(format) {
  return {
    docx: "Word",
    txt: "TXT",
    md: "Markdown",
    json: "JSON",
    srt: "SRT",
  }[format] || format;
}

function truncateText(text, limit) {
  const value = String(text || "");
  return value.length > limit ? `${value.slice(0, limit)}\n...` : value;
}

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`;
}

function selectedTranscriptionEngine() {
  const mode = selectedAudioMode();
  if (mode === "whisper" || mode === "mlx-whisper") return mode;
  if (mode !== "local_audio_llm") return "";
  const selected = selectedAudioModel();
  return audioPipelineForModel(selected);
}

function updateEngineControls() {
  const engine = selectedTranscriptionEngine();
  const mode = selectedAudioMode();
  const usingOllamaAudio = engine === "ollama_audio";
  const usingMlxWhisper = engine === "mlx-whisper";
  const usingQwenAudio = engine === "qwen-audio";
  const usingMlxVlmAudio = engine === "mlx-vlm-audio";
  const whisperDownloading = lastModelStatus?.download_state === "downloading";
  whisperModelField.hidden = mode !== "whisper";
  localAudioLlmField.hidden = mode !== "local_audio_llm";
  mlxModelField.hidden = !usingMlxWhisper;
  qwenModelField.hidden = !(usingQwenAudio || usingMlxVlmAudio);
  modelSelect.disabled = usingOllamaAudio || usingMlxWhisper || usingQwenAudio || usingMlxVlmAudio || whisperDownloading;
  if (engine === "whisper") {
    refreshModelStatus();
  }
  if (usingMlxWhisper) {
    refreshMlxStatus();
  }
  if (usingQwenAudio) {
    refreshQwenStatus();
  }
  if (usingMlxVlmAudio) {
    refreshMlxVlmStatus();
  }
  ollamaTranscriptionModelSelect.disabled = !availableAudioRegistryModels().length;
  renderModeStatus();
  renderEnvironmentStatus();
  updateWorkbenchSummaries();
}

function renderModeStatus() {
  const whisperExists = Boolean(lastModelStatus?.available || (lastModelStatus?.models || []).some((model) => model.available));
  whisperModeStatus.textContent = whisperExists ? "已找到本地 Whisper 模型。" : "未找到本地 Whisper 模型，可先检测或下载。";
  mlxModeStatus.textContent = lastMlxStatus?.available
    ? `MLX 模型已配置：${lastMlxStatus.model_path_or_repo || "可用"}`
    : lastMlxStatus?.reason || "未检测到可用的 MLX Whisper。";
  const localCount = (lastModelRegistry?.models || []).filter(isLocalAudioLlmModel).length;
  localAudioModeStatus.textContent = localCount
    ? `已检测到 ${localCount} 个音频大模型。`
    : "未检测到音频大模型，可在“模型检测”中绑定。";
}

function updatePolishControls() {
  polishField.hidden = !enablePolishInput.checked;
  localModelTools.hidden = true;
  polishProfileField.hidden = !enablePolishInput.checked;
  document.querySelector("#polish-custom-field").hidden = !enablePolishInput.checked;
  document.querySelector("#prompt-preview").hidden = !enablePolishInput.checked;
  polishModelSelect.disabled = !enablePolishInput.checked;
  localProviderSelect.disabled = true;
  localModelSelect.disabled = true;
  localModelDetectButton.disabled = true;
  polishProfileList.querySelectorAll("input").forEach((input) => {
    input.disabled = !enablePolishInput.checked;
  });
  polishCustomInstruction.disabled = !enablePolishInput.checked;
  updatePromptPreview();
  updateExportScopeControls();
  updateWorkbenchSummaries();
}

function updateExportScopeControls() {
  const allowPolished = enablePolishInput.checked;
  const selected = form.querySelector('input[name="export_scope"]:checked');
  for (const input of form.querySelectorAll('input[name="export_scope"]')) {
    const requiresPolish = ["both", "polished"].includes(input.value);
    input.disabled = requiresPolish && !allowPolished;
    input.closest("label")?.classList.toggle("is-disabled", input.disabled);
  }
  if (!allowPolished && selected && selected.value !== "raw") {
    form.querySelector('input[name="export_scope"][value="raw"]').checked = true;
  }
}

function updateFormatControls() {
  if (!srtFormatInput) return;
  const enabled = includeTimestampsInput.checked;
  srtFormatInput.disabled = !enabled;
  if (!enabled) {
    srtFormatInput.checked = false;
  }
  const label = srtFormatInput.closest("label");
  if (label) {
    label.title = enabled ? "包含时间戳 segments 时可导出字幕" : "SRT 需要开启时间轴";
    label.classList.toggle("is-disabled", !enabled);
  }
  updateWorkbenchSummaries();
}

async function refreshPolishProfiles() {
  try {
    const response = await fetch("/api/polish/profiles");
    polishProfiles = await response.json();
    if (!response.ok) throw new Error("文本整理配置读取失败");
    renderPolishProfileOptions();
    updatePolishProfileDescription();
    updatePromptPreview();
  } catch {
    polishProfiles = [];
  }
}

function updatePolishProfileDescription() {
  const selected = selectedPolishProfiles();
  if (!selected.length) {
    polishProfileDescription.textContent = "至少选择一个文本整理配置。";
    updateWorkbenchSummaries();
    return;
  }
  const names = selected.map((profile) => profile.label).join(" + ");
  polishProfileDescription.textContent =
    selected.length === 1 ? selected[0].description : `已选择 ${selected.length} 个配置：${names}。系统会按顺序合并指令。`;
  updateWorkbenchSummaries();
}

function updatePromptPreview() {
  const selected = selectedPolishProfiles();
  const base = selected.length
    ? selected.map((profile, index) => `${index + 1}. ${profile.label}\n${currentProfilePrompt(profile)}`).join("\n\n")
    : "读取 profile 后显示基础指令。";
  const custom = polishCustomInstruction.value.trim();
  promptPreviewText.textContent = custom ? `${base}\n追加用户指令：${custom}` : base;
}

function effectivePolishInstructionValue() {
  const selected = selectedPolishProfiles();
  const custom = polishCustomInstruction.value.trim();
  if (!selected.length) return custom;
  const hasOverride = selected.some((profile) => {
    const base = currentProfilePrompt(profile);
    const defaultPrompt = profile.default_prompt || profile.prompt_preview || "";
    return base && base !== defaultPrompt;
  });
  if (hasOverride) {
    const base = selected.map((profile) => currentProfilePrompt(profile)).filter(Boolean).join("\n\n");
    return `__OVERRIDE_PROMPT__${custom ? `${base}\n追加用户指令：${custom}` : base}`;
  }
  return custom;
}

function renderPolishProfileOptions() {
  const previousIds = selectedPolishProfileIds();
  polishProfileList.replaceChildren(
    ...polishProfiles.map((profile, index) => {
      const label = document.createElement("label");
      label.className = "polish-profile-option";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = profile.id;
      input.checked = previousIds.includes(profile.id) || (!previousIds.length && index === 0);
      input.addEventListener("change", () => {
        if (!selectedPolishProfileIds().length) input.checked = true;
        syncPolishProfileValue();
        updatePolishProfileDescription();
        updatePromptPreview();
      });
      const content = document.createElement("span");
      const title = document.createElement("strong");
      title.textContent = profile.label;
      const description = document.createElement("small");
      description.textContent = profile.description;
      content.append(title, description);
      label.append(input, content);
      return label;
    }),
  );
  syncPolishProfileValue();
}

function selectedPolishProfileIds() {
  const checked = [...polishProfileList.querySelectorAll('input[type="checkbox"]:checked')].map((input) => input.value);
  if (checked.length) return checked;
  return (polishProfileSelect.value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function selectedPolishProfiles() {
  const ids = selectedPolishProfileIds();
  return ids.map((id) => polishProfiles.find((profile) => profile.id === id)).filter(Boolean);
}

function primarySelectedPolishProfile() {
  return selectedPolishProfiles()[0] || polishProfiles[0] || null;
}

function syncPolishProfileValue() {
  polishProfileSelect.value = selectedPolishProfileIds().join(",") || "repair";
}

function loadSavedCustomInstruction() {
  polishCustomInstruction.value = localStorage.getItem(CUSTOM_INSTRUCTION_KEY) || "";
}

async function refreshHealth() {
  try {
    const response = await fetch("/api/health");
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "环境检查失败");
    renderHealth(payload);
    return payload;
  } catch (error) {
    healthMessage.textContent = `环境检查失败：${error.message}`;
    return null;
  }
}

function renderHealth(payload) {
  const items = payload.items || [];
  const errorCount = items.filter((item) => item.status === "error").length;
  const warningCount = items.filter((item) => item.status === "warning").length;
  healthMessage.textContent = errorCount
    ? `${errorCount} 项错误，${warningCount} 项警告`
    : warningCount
      ? `${warningCount} 项需要确认`
      : "环境检查通过";
  healthList.replaceChildren(...items.map(renderHealthItem));
  renderEnvironmentStatus();
}

function renderHealthItem(item) {
  const row = document.createElement("div");
  row.className = `health-item health-${item.status}`;
  row.dataset.id = item.id;
  row._item = item;
  const title = document.createElement("strong");
  title.textContent = item.label;
  const message = document.createElement("span");
  message.textContent = item.status === "success" ? "已就绪" : item.message || item.suggestion || "需要确认";
  row.append(title, message);
  if (item.suggestion && item.status !== "success") {
    const suggestion = document.createElement("small");
    suggestion.textContent = item.suggestion;
    row.append(suggestion);
  }
  return row;
}

function renderEnvironmentStatus() {
  if (!environmentStatusGrid) return;
  const engine = selectedTranscriptionEngine();
  const platform = platformSummary();
  const selected = selectedAudioModel();
  const registryModels = lastModelRegistry?.models || [];
  const audioCount = registryModels.filter((model) => model.capabilities?.audio && model.metadata?.status === "available").length;
  const textCount = registryModels.filter((model) => model.capabilities?.text && model.metadata?.status === "available").length;
  const whisperReady = Boolean(lastModelStatus?.available || registryModels.some((model) => model.capabilities?.audio && /whisper/i.test(`${model.name} ${model.path_or_id}`)));
  const mlxReady = Boolean(lastMlxStatus?.available);
  const mlxVlmReady = Boolean(lastMlxVlmStatus?.available);
  const ollamaReady = Boolean(lastOllamaStatus?.available);
  const selectedModel = selected ? `${selected.name} · ${providerLabel(selected.provider)}` : "未选择模型";

  environmentSummary.textContent = `${engine ? transcriptionEngineLabel(engine) : "未选择引擎"} · ${selectedModel}`;
  environmentStatusGrid.replaceChildren(
    statusRow("后端服务", "可响应", "success", "API 服务已连接"),
    statusRow("Python 环境", dependencyLabel("python"), dependencyKind("python"), dependencyMessage("python")),
    statusRow("FFmpeg", dependencyLabel("ffmpeg"), dependencyKind("ffmpeg"), dependencyMessage("ffmpeg")),
    statusRow("MLX 运行库", dependencyLabel("mlx_whisper"), dependencyKind("mlx_whisper"), dependencyMessage("mlx_whisper")),
    statusRow("Whisper 后端", dependencyLabel("faster_whisper"), dependencyKind("faster_whisper"), dependencyMessage("faster_whisper")),
    statusRow("统一模型池", `${audioCount} 个音频 / ${textCount} 个文本`, audioCount || textCount ? "success" : "warning", lastModelRegistry?.checked_at || "等待检测"),
    statusRow("当前引擎", engine ? transcriptionEngineLabel(engine) : "未选择", currentEngineStatus(engine), selectedModel),
    statusRow("平台适配", platform.label, platform.status, platform.detail),
    statusRow("Whisper / faster-whisper", whisperReady ? "已检测" : "未配置", whisperReady ? "success" : "warning", lastModelStatus?.message || "等待检测"),
    statusRow("MLX Whisper", mlxReady ? "可用" : mlxStatusLabel(lastMlxStatus), mlxReady ? "success" : mlxStatusKind(lastMlxStatus), mlxStatusDetail(lastMlxStatus)),
    statusRow("MLX VLM Audio", mlxVlmReady ? "可用" : mlxVlmStatusLabel(lastMlxVlmStatus), mlxVlmReady ? "success" : mlxVlmStatusKind(lastMlxVlmStatus), mlxVlmStatusDetail(lastMlxVlmStatus)),
    statusRow("本地大模型", ollamaReady ? "服务可用" : "未检测到服务", ollamaReady ? "success" : "warning", lastOllamaStatus?.message || "支持 Ollama、MLX、本地目录和 llama.cpp"),
  );
  environmentAdvice?.replaceChildren(...environmentAdviceItems(platform, engine));
}

function statusRow(label, value, kind, detail) {
  const row = document.createElement("div");
  row.className = "status-row";
  const title = document.createElement("span");
  title.textContent = label;
  const badge = document.createElement("strong");
  badge.className = `status-badge status-${kind || "neutral"}`;
  badge.textContent = value || "未知";
  const note = document.createElement("small");
  note.textContent = compactStatusDetail(label, detail);
  note.title = detail || "";
  row.append(title, badge, note);
  return row;
}

function compactStatusDetail(label, detail) {
  const text = String(detail || "").trim();
  if (!text) return "";
  if (label === "后端服务") return "API 服务已连接";
  if (label === "Python 环境") return text.match(/Python\s*[\d.]+/)?.[0] || "Python 可用";
  if (label === "FFmpeg") return text.includes("/") ? `路径：${text.split("/").pop()}` : text;
  if (label === "MLX 运行库" && text.includes("未检测到")) return "未检测到 mlx-whisper";
  if (label === "Whisper 后端") return text.includes("导入") ? "faster-whisper 可导入" : text;
  if (label === "统一模型池") return text.includes("T") ? text.replace(/\.\d+/, "") : text;
  if (label === "当前引擎") return text.replace(/\s+·\s+/g, " · ");
  if (label === "MLX Whisper" && text.includes("未检测到")) return "未检测到 mlx-whisper";
  if (label === "MLX VLM Audio" && text.includes("未配置")) return "未配置模型路径";
  if (label === "本地大模型" && text.length > 36) return "支持 Ollama、MLX 和本地目录";
  return text.length > 48 ? `${text.slice(0, 45)}...` : text;
}

function platformSummary() {
  const os = lastMlxStatus?.os || navigator.platform || "unknown";
  const arch = lastMlxStatus?.arch || "";
  if (lastMlxStatus?.is_apple_silicon) {
    return { label: `${os} / Apple Silicon`, status: "success", detail: "可使用 MLX Whisper 或 faster-whisper" };
  }
  if (/win/i.test(os) || /win/i.test(navigator.platform || "")) {
    return { label: "Windows", status: "success", detail: "可使用 faster-whisper / Whisper；CUDA 可用时优先 CUDA" };
  }
  return { label: [os, arch].filter(Boolean).join(" / "), status: "warning", detail: "优先使用 faster-whisper；MLX 可能不适配" };
}

function currentEngineStatus(engine) {
  if (!engine) return "neutral";
  if (engine === "mlx-whisper") return lastMlxStatus?.available ? "success" : "warning";
  if (engine === "qwen-audio") return lastQwenStatus?.available ? "success" : "warning";
  if (engine === "mlx-vlm-audio") return lastMlxVlmStatus?.available ? "success" : "warning";
  if (engine === "ollama_audio") return lastOllamaStatus?.available ? "success" : "warning";
  return lastModelStatus?.available ? "success" : "warning";
}

function mlxStatusLabel(status) {
  if (!status) return "等待检测";
  if (!status.platform_supported) return "平台不适配";
  if (!status.dependency_installed) return "依赖缺失";
  if (!status.model_configured) return "未配置";
  if (!status.ffmpeg_available) return "FFmpeg 缺失";
  return "模型未找到";
}

function mlxStatusKind(status) {
  if (!status) return "neutral";
  return status.platform_supported ? "warning" : "muted";
}

function mlxStatusDetail(status) {
  if (!status) return "等待检测 mlx-whisper";
  return status.reason || status.hint || "MLX Whisper 可用";
}

function qwenStatusLabel(status) {
  if (!status) return "等待检测";
  if (!status.platform_supported) return "平台不适配";
  if (!status.dependency_installed) return "依赖缺失";
  if (!status.model_configured) return "未配置";
  if (!status.ffmpeg_available) return "FFmpeg 缺失";
  return "模型未找到";
}

function qwenStatusKind(status) {
  if (!status) return "neutral";
  return status.platform_supported ? "warning" : "muted";
}

function qwenStatusDetail(status) {
  if (!status) return "等待检测 MLX Audio";
  return status.reason || status.hint || "MLX Audio 可用";
}

function mlxVlmStatusLabel(status) {
  if (!status) return "等待检测";
  if (!status.platform_supported) return "平台不适配";
  if (!status.python_available) return "Python 缺失";
  if (!status.dependency_installed) return "依赖缺失";
  if (!status.model_configured) return "未配置";
  if (!status.ffmpeg_available) return "FFmpeg 缺失";
  return "模型未找到";
}

function mlxVlmStatusKind(status) {
  if (!status) return "neutral";
  return status.platform_supported ? "warning" : "muted";
}

function mlxVlmStatusDetail(status) {
  if (!status) return "等待检测 MLX VLM Audio";
  return status.reason || status.hint || "MLX VLM Audio 可用";
}

function dependencyLabel(id) {
  const item = healthItem(id);
  return item?.status === "success" ? "可用" : item?.status === "error" ? "缺失" : "需确认";
}

function dependencyKind(id) {
  const item = healthItem(id);
  return item?.status === "success" ? "success" : item?.status === "error" ? "danger" : "warning";
}

function dependencyDetail(extra) {
  const ffmpeg = healthItem("ffmpeg");
  const python = healthItem(extra);
  return [ffmpeg?.message, python?.message].filter(Boolean).join(" · ");
}

function dependencyMessage(id) {
  return healthItem(id)?.message || "等待检测";
}

function healthItem(id) {
  return [...healthList.querySelectorAll(".health-item")].find((node) => node.dataset.id === id)?._item || null;
}

function environmentAdviceItems(platform, engine) {
  const items = [];
  const add = (text) => {
    const item = document.createElement("p");
    item.textContent = text;
    items.push(item);
  };
  if (lastMlxStatus?.is_apple_silicon) {
    add("Mac 用户可优先配置 MLX Whisper。");
  } else {
    add(platform.detail || "当前平台建议优先使用 faster-whisper。");
  }
  if (engine === "mlx-whisper" && !lastMlxStatus?.available) {
    add(lastMlxStatus?.hint || "请先安装 mlx-whisper 并配置模型。");
  }
  if (engine === "qwen-audio" && !lastQwenStatus?.available) {
    add(lastQwenStatus?.hint || "请先安装 mlx-audio 并配置 MLX Audio 模型。");
  }
  if (engine === "mlx-vlm-audio" && !lastMlxVlmStatus?.available) {
    add(lastMlxVlmStatus?.hint || "请先配置安装了 mlx-vlm 的 Python 环境和 Gemma4 MLX 模型。");
  }
  add("本项目不会自动下载 MLX Whisper、MLX Audio 或 MLX VLM Audio 模型。");
  return items.slice(0, 3);
}

async function ensureSelectedOllamaModelsReady() {
  const required = [];
  if (selectedTranscriptionEngine() === "ollama_audio") {
    if (!ollamaTranscriptionModelSelect.value) {
      showDiagnostic(diagnoseClientError("请选择支持音频输入的 Ollama 模型。"));
      return false;
    }
    required.push({ modelId: ollamaTranscriptionModelSelect.value, task: "direct_audio" });
  }
  if (enablePolishInput.checked) {
    if (!polishModelSelect.value) {
      showDiagnostic(diagnoseClientError("请选择检测到的 Text 模型后再启用文本整理。"));
      return false;
    }
    const polishModel = selectedPolishModel();
    if (polishModel?.provider === "ollama") {
      required.push({ modelId: polishModel.path_or_id, task: "polish" });
    }
  }
  const uniqueChecks = [];
  const seen = new Set();
  for (const item of required) {
    const key = `${item.modelId}:${item.task}`;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueChecks.push(item);
    }
  }
  if (!uniqueChecks.length) return true;

  const status = await refreshOllamaStatus();
  if (!status?.available) {
    showDiagnostic(diagnoseClientError("Ollama 服务不可用，请先启动 Ollama。"));
    return false;
  }

  for (const item of uniqueChecks) {
    const check = await preflightOllamaModel(item.modelId, item.task);
    if (!check.service_available) {
      showDiagnostic(diagnoseClientError("Ollama 服务不可用，请先启动 Ollama。"));
      return false;
    }
    if (!check.model_exists) {
      showDiagnostic({
        code: "OLLAMA_MODEL_MISSING",
        title: "Ollama 模型缺失",
        message: `${item.modelId} 不在本地模型列表中。`,
        action: "点击“检测本地模型”查看已存在模型，或在应用外手动安装模型。本流程不会自动下载。",
        technical_detail: check.message || item.modelId,
      });
      return false;
    }
    if (!check.can_generate) {
      showDiagnostic(diagnoseClientError(check.error || check.message || `${item.modelId} preflight 未通过`));
      return false;
    }
    if (check.warnings?.length) {
      ollamaMessage.textContent = check.warnings.join(" ");
    }
  }
  return true;
}

async function ensureSelectedMlxReady() {
  if (selectedTranscriptionEngine() !== "mlx-whisper") return true;
  const status = await refreshMlxStatus();
  if (status?.available) return true;
  showDiagnostic({
    code: "MLX_WHISPER_UNAVAILABLE",
    title: "MLX Whisper 不可用",
    message: status?.reason || "MLX Whisper 前置条件未满足。",
    action: status?.hint || "请自行安装 mlx-whisper，并准备本地 MLX 格式 Whisper 模型。本项目不会自动下载模型。",
    technical_detail: JSON.stringify(status || {}, null, 2),
  });
  return false;
}

async function ensureSelectedQwenReady() {
  if (selectedTranscriptionEngine() !== "qwen-audio") return true;
  if (!mockBanner.hidden) return true;
  const status = await refreshQwenStatus();
  if (status?.model_supported === false && isMlxVlmAudioModel({ path_or_id: status.model_path_or_repo || qwenModelPathOrRepo.value })) {
    return ensureSelectedMlxVlmReady(true);
  }
  if (status?.available) return true;
  showDiagnostic({
    code: "QWEN_AUDIO_UNAVAILABLE",
    title: "MLX Audio 不可用",
    message: status?.reason || "MLX Audio 前置条件未满足。",
    action: status?.hint || "请自行安装 mlx-audio，并准备本地 MLX Audio 模型。本项目不会自动调用云服务。",
    technical_detail: JSON.stringify(status || {}, null, 2),
  });
  return false;
}

async function ensureSelectedMlxVlmReady(force = false) {
  if (!force && selectedTranscriptionEngine() !== "mlx-vlm-audio") return true;
  if (!mockBanner.hidden) return true;
  const status = await refreshMlxVlmStatus();
  if (status?.available) return true;
  showDiagnostic({
    code: "MLX_VLM_AUDIO_UNAVAILABLE",
    title: "MLX VLM Audio 不可用",
    message: status?.reason || "MLX VLM Audio 前置条件未满足。",
    action: status?.hint || "请确认项目 .venv 已安装 mlx-vlm，并选择本地 Gemma4 MLX Audio/Text 模型。",
    technical_detail: JSON.stringify(status || {}, null, 2),
  });
  return false;
}

async function refreshMlxStatus() {
  try {
    const params = new URLSearchParams();
    const configured = mlxModelPathOrRepo.value.trim();
    if (configured) params.set("model_path_or_repo", configured);
    const response = await fetch(`/api/mlx-whisper/status${params.toString() ? `?${params.toString()}` : ""}`);
    const status = await response.json();
    if (!response.ok) throw new Error(status.detail || "MLX Whisper 状态检测失败");
    renderMlxStatus(status);
    return status;
  } catch (error) {
    mlxModelHelp.textContent = `MLX Whisper 状态检测失败：${error.message}`;
    lastMlxStatus = null;
    renderEnvironmentStatus();
    return null;
  }
}

function renderMlxStatus(status) {
  lastMlxStatus = status;
  if (!mlxModelPathOrRepo.value && status.model_path_or_repo) {
    mlxModelPathOrRepo.value = status.model_path_or_repo;
  }
  mlxModelHelp.textContent = status.reason
    ? `${status.reason} ${status.hint || ""}`
    : status.hint || "MLX Whisper 可用。转录时不会自动下载模型。";
  mlxModelHelp.classList.toggle("warning-text", !status.available);
  renderModeStatus();
  renderModelDetection(lastModelRegistry?.errors || []);
  renderEnvironmentStatus();
  updateWorkbenchSummaries();
}

async function refreshQwenStatus() {
  try {
    const params = new URLSearchParams();
    const configured = qwenModelPathOrRepo.value.trim();
    if (configured) params.set("model_path_or_repo", configured);
    const response = await fetch(`/api/qwen-audio/status${params.toString() ? `?${params.toString()}` : ""}`);
    const status = await response.json();
    if (!response.ok) throw new Error(status.detail || "MLX Audio 状态检测失败");
    renderQwenStatus(status);
    return status;
  } catch (error) {
    qwenModelHelp.textContent = `MLX Audio 状态检测失败：${error.message}`;
    lastQwenStatus = null;
    renderEnvironmentStatus();
    return null;
  }
}

function renderQwenStatus(status) {
  lastQwenStatus = status;
  if (!qwenModelPathOrRepo.value && status.model_path_or_repo) {
    qwenModelPathOrRepo.value = status.model_path_or_repo;
  }
  qwenModelHelp.textContent = status.reason
    ? `${status.reason} ${status.hint || ""}`
    : status.hint || "MLX Audio 可用。chunk 级结果会随任务状态逐步更新。";
  qwenModelHelp.classList.toggle("warning-text", !status.available);
  renderEnvironmentStatus();
  updateWorkbenchSummaries();
}

async function refreshMlxVlmStatus() {
  try {
    const params = new URLSearchParams();
    const configured = qwenModelPathOrRepo.value.trim();
    if (configured) params.set("model_path_or_repo", configured);
    const response = await fetch(`/api/mlx-vlm-audio/status${params.toString() ? `?${params.toString()}` : ""}`);
    const status = await response.json();
    if (!response.ok) throw new Error(status.detail || "MLX VLM Audio 状态检测失败");
    renderMlxVlmStatus(status);
    return status;
  } catch (error) {
    qwenModelHelp.textContent = `MLX VLM Audio 状态检测失败：${error.message}`;
    lastMlxVlmStatus = null;
    renderEnvironmentStatus();
    return null;
  }
}

function renderMlxVlmStatus(status) {
  lastMlxVlmStatus = status;
  if (!qwenModelPathOrRepo.value && status.model_path_or_repo) {
    qwenModelPathOrRepo.value = status.model_path_or_repo;
  }
  qwenModelHelp.textContent = status.reason
    ? `${status.reason} ${status.hint || ""}`
    : status.hint || `MLX VLM Audio 可用。Python：${status.python_executable || "未记录"}`;
  qwenModelHelp.classList.toggle("warning-text", !status.available);
  renderEnvironmentStatus();
  updateWorkbenchSummaries();
}

async function preflightOllamaModel(modelId, task) {
  const params = new URLSearchParams({ model_id: modelId, task });
  const response = await fetch(`/api/ollama/preflight?${params.toString()}`);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Ollama preflight 失败");
  }
  return payload;
}

async function confirmAndStartOllamaDownload(modelId) {
  const approved = window.confirm(
    `${modelId} 不在本地 Ollama 模型列表中。确认调用 Ollama 下载该模型吗？模型文件由 Ollama 管理，不会下载到项目目录。`,
  );
  if (!approved) return false;

  ollamaManagedModelSelect.value = modelId;
  ollamaDownloadButton.disabled = true;
  ollamaMessage.textContent = `正在提交 ${modelId} 下载任务`;
  const response = await fetch("/api/ollama/models/pull", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model_id: modelId }),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    ollamaMessage.textContent = payload.detail || "Ollama 模型下载任务启动失败";
    ollamaDownloadButton.disabled = false;
    return false;
  }
  renderOllamaPullStatus(payload);
  startOllamaPolling(modelId);
  return true;
}

async function refreshOllamaStatus() {
  try {
    const response = await fetch("/api/ollama/status");
    const status = await response.json();
    renderOllamaStatus(status);
    return status;
  } catch (error) {
    ollamaMessage.textContent = `Ollama 状态检测失败：${error.message}`;
    ollamaServicePill.textContent = "服务：不可用";
    ollamaServicePill.dataset.device = "unknown";
    mockBanner.hidden = true;
    return null;
  }
}

function renderOllamaStatus(status) {
  lastOllamaStatus = status;
  ollamaMessage.textContent = status.error || status.message;
  mockBanner.hidden = !status.mock_mode;
  ollamaServicePill.textContent = status.available
    ? `服务：可用${status.version ? `（${status.version}）` : ""}`
    : "服务：不可用";
  ollamaServicePill.dataset.device = status.available ? "cpu" : "unknown";
  renderOllamaOptions(status);
  refreshSelectedOllamaModel();
  renderEnvironmentStatus();
}

function eventTimeLabel(value) {
  const time = Date.parse(value || "");
  if (!Number.isFinite(time)) return "--:--:--";
  return new Date(time).toLocaleTimeString([], {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatOllamaModelOption(model, details = []) {
  const suffix = details.filter(Boolean).join("，");
  return `${model.label} — ${model.id}${suffix ? `（${suffix}）` : ""}`;
}

function availableRegistryModels() {
  return (lastModelRegistry?.models || []).filter(
    (model) => model.metadata?.status === "available" && !isWhisperLikeModel(model) && (model.capabilities?.audio || model.capabilities?.text),
  );
}

function availableAudioRegistryModels() {
  return availableRegistryModels().filter((model) => isLocalAudioLlmModel(model) && audioPipelineForModel(model));
}

function availableTextRegistryModels() {
  return availableRegistryModels().filter((model) => model.capabilities?.text);
}

function modelCapabilityTags(model) {
  const tags = [];
  if (model.capabilities?.audio) tags.push("音频");
  if (model.capabilities?.text) tags.push("文本");
  if (model.capabilities?.vision) tags.push("视觉");
  return tags.join(" / ") || "未知能力";
}

function modelDetailOptionLabel(model) {
  return `${model.name} — ${providerLabel(model.provider)} · ${modelCapabilityTags(model)}`;
}

function modelSourceLabel(model) {
  return model.metadata?.source === "user_added" ? "已导入" : "已检测";
}

function registryModelOption(model) {
  const option = document.createElement("option");
  option.value = model.path_or_id;
  option.textContent = modelDetailOptionLabel(model);
  option.dataset.provider = model.provider;
  option.dataset.modelId = model.id;
  option.dataset.status = model.metadata?.status || "";
  return option;
}

function ollamaStatusModelOption(modelId) {
  const option = document.createElement("option");
  option.value = modelId;
  option.textContent = `${modelId} — Ollama · 本机已有模型`;
  option.dataset.provider = "ollama";
  option.dataset.status = "available";
  return option;
}

function selectedManagedModelMeta() {
  const option = ollamaManagedModelSelect.selectedOptions[0];
  const value = ollamaManagedModelSelect.value;
  const registryModel = availableRegistryModels().find((model) => model.path_or_id === value || model.id === option?.dataset.modelId);
  return {
    option,
    model: registryModel || null,
    provider: registryModel?.provider || option?.dataset.provider || "",
    available: option?.dataset.status === "available" || Boolean(registryModel),
  };
}

function renderLoadedModelMetrics(status = {}) {
  const audioModels = availableAudioRegistryModels();
  const textModels = availableTextRegistryModels();
  const ollamaModels = status.local_models || [];
  if (loadedAudioCount) loadedAudioCount.textContent = String(audioModels.length);
  if (loadedTextCount) loadedTextCount.textContent = String(textModels.length);
  if (ollamaLocalCount) ollamaLocalCount.textContent = String(ollamaModels.length);
  if (loadedModelSummary) {
    loadedModelSummary.textContent = audioModels.length
      ? `${audioModels.length} 个模型可直转，${textModels.length} 个模型可整理`
      : "未检测到可直转模型";
  }
  renderLocalModelInventory();
}

function renderLocalModelInventory() {
  if (!localModelInventory) return;
  const models = availableRegistryModels();
  if (!models.length) {
    const empty = document.createElement("small");
    empty.className = "inventory-empty";
    empty.textContent = "未检测到已加载模型；请在“模型检测”中绑定目录或启动本地模型服务。";
    localModelInventory.replaceChildren(empty);
    return;
  }
  localModelInventory.replaceChildren(
    ...models.slice(0, 6).map((model) => {
      const item = document.createElement("div");
      item.className = "inventory-model";
      item.title = model.path_or_id;
      const state = document.createElement("span");
      state.className = "inventory-state";
      state.textContent = modelSourceLabel(model);
      const name = document.createElement("strong");
      name.textContent = model.name;
      const meta = document.createElement("span");
      meta.className = "inventory-capability";
      meta.textContent = `${providerLabel(model.provider)} · ${modelCapabilityTags(model)}`;
      const path = document.createElement("small");
      path.textContent = displayModelPath(model.path_or_id);
      item.append(state, name, meta, path);
      return item;
    }),
  );
}

function renderOllamaOptions(status) {
  const audioModels = availableAudioRegistryModels();
  const registryModels = availableRegistryModels();
  const currentTranscription = ollamaTranscriptionModelSelect.value;
  const currentManaged = ollamaManagedModelSelect.value;

  const transcriptionOptions = audioModels.map(registryModelOption);
  if (!transcriptionOptions.length) {
    transcriptionOptions.push(new Option("未检测到可直转模型", ""));
  }
  ollamaTranscriptionModelSelect.replaceChildren(...transcriptionOptions);
  const selectedAudio = selectedAudioModel();
  const preferredTranscription = selectedAudio?.path_or_id || currentTranscription || audioModels[0]?.path_or_id || "";
  ollamaTranscriptionModelSelect.value = transcriptionOptions.some((option) => option.value === preferredTranscription)
    ? preferredTranscription
    : "";

  const localOllamaIds = new Set(status.local_models || []);
  const registryOllamaIds = new Set(
    registryModels.filter((model) => model.provider === "ollama").map((model) => normalizeOllamaId(model.path_or_id)),
  );
  const ollamaOnlyOptions = [...localOllamaIds]
    .filter((modelId) => !registryOllamaIds.has(normalizeOllamaId(modelId)))
    .map(ollamaStatusModelOption);
  const configuredMissingOptions = [...(status.transcription_models || []), ...(status.polish_models || [])]
    .filter((model) => model.available && !localOllamaIds.has(model.id))
    .map((model) => {
      const option = document.createElement("option");
      option.value = model.id;
      option.textContent = formatOllamaModelOption(model, [model.role, "已存在"]);
      option.dataset.provider = "ollama";
      option.dataset.status = "available";
      return option;
    });
  const combined = [...registryModels.map(registryModelOption), ...ollamaOnlyOptions, ...configuredMissingOptions];
  const seen = new Set();
  const options = [];
  for (const option of combined) {
    if (seen.has(option.value)) continue;
    seen.add(option.value);
    options.push(option);
  }
  if (!options.length) {
    options.push(new Option("未检测到模型库记录", ""));
  }
  ollamaManagedModelSelect.replaceChildren(...options);
  ollamaManagedModelSelect.value = options.some((option) => option.value === currentManaged) ? currentManaged : options[0]?.value || "";
  renderLoadedModelMetrics(status);
}

function normalizeOllamaId(modelId) {
  const value = String(modelId || "");
  return value.includes(":") ? value : `${value}:latest`;
}

function applyDetailAudioModelSelection() {
  const value = ollamaTranscriptionModelSelect.value;
  const model = availableAudioRegistryModels().find((item) => item.path_or_id === value || item.id === value);
  if (!model) {
    updateWorkbenchSummaries();
    return;
  }
  audioModelSelect.value = model.id;
  selectAudioMode("local_audio_llm");
  applySelectedAudioModelToForm();
  renderSelectedAudioModel();
  updateEngineControls();
  updateWorkbenchSummaries();
}

async function refreshLocalModelDetection() {
  localModelDetectButton.disabled = true;
  localModelDetectLabel.textContent = "检测中";
  localModelMessage.textContent = "正在检测 Ollama、LM Studio、llama.cpp 和本地兼容服务";
  try {
    const response = await fetch("/api/local-models/detect");
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "本地模型检测失败");
    renderLocalModelDetection(payload);
    return payload;
  } catch (error) {
    localModelMessage.textContent = `本地模型检测失败：${error.message}`;
    localModelResults.replaceChildren();
    return null;
  } finally {
    localModelDetectButton.disabled = !enablePolishInput.checked;
    localModelDetectLabel.textContent = "检测本地模型";
  }
}

function renderLocalModelDetection(payload) {
  lastLocalModelDetection = payload;
  localModelMessage.textContent = payload.message || "检测完成。本功能不会自动下载模型。";
  renderLocalProviderChoices();
  renderLocalModelChoices();
  const providers = payload.providers || [];
  localModelResults.replaceChildren(...providers.map(renderLocalProviderResult));
  if (!providers.length) {
    const empty = document.createElement("p");
    empty.className = "empty compact-empty";
    empty.textContent = "未检测到本地模型服务。请确认 Ollama / LM Studio / llama.cpp server 是否已启动。本功能不会自动下载模型。";
    localModelResults.append(empty);
  }
}

function renderLocalProviderChoices() {
  const providers = lastLocalModelDetection?.providers || [];
  const onlineProviders = providers.filter((provider) => provider.online);
  const selectable = onlineProviders.length ? onlineProviders : providers;
  if (!selectable.length) {
    localProviderSelect.replaceChildren(new Option("未检测到提供方", ""));
    localProviderSelect.disabled = true;
    localModelSelect.replaceChildren(new Option("未检测到模型", ""));
    localModelSelect.disabled = true;
    return;
  }
  const current = localProviderSelect.value;
  localProviderSelect.replaceChildren(
    ...selectable.map((provider) => {
      const label = `${provider.name} · ${provider.online ? "在线" : "离线"} · ${provider.models?.length || 0} 个模型`;
      return new Option(label, provider.id);
    }),
  );
  localProviderSelect.value = selectable.some((provider) => provider.id === current) ? current : selectable[0].id;
  localProviderSelect.disabled = !enablePolishInput.checked;
}

function renderLocalModelChoices() {
  const provider = selectedLocalProvider();
  const models = provider?.models || [];
  if (!provider || !models.length) {
    localModelSelect.replaceChildren(new Option("未检测到模型", ""));
    localModelSelect.disabled = true;
    return;
  }
  const current = localModelSelect.value;
  localModelSelect.replaceChildren(
    ...models.map((model) => {
      const state = model.can_polish ? "可用于文本整理" : "仅检测展示";
      const option = new Option(`${model.name} · ${state}`, model.id);
      option.dataset.providerId = model.provider_id;
      option.title = model.recommendation || "";
      return option;
    }),
  );
  localModelSelect.value = models.some((model) => model.id === current) ? current : models[0].id;
  localModelSelect.disabled = !enablePolishInput.checked;
  applyDetectedLocalModelSelection();
}

function selectedLocalProvider() {
  const providers = lastLocalModelDetection?.providers || [];
  return providers.find((provider) => provider.id === localProviderSelect.value);
}

function selectedLocalModel() {
  const provider = selectedLocalProvider();
  return (provider?.models || []).find((model) => model.id === localModelSelect.value);
}

function applyDetectedLocalModelSelection() {
  const model = selectedLocalModel();
  if (!model) return;
  if (model.provider_type === "ollama" && model.can_polish) {
    ensurePolishOption(model.id, `${model.name} — ${model.id}（Ollama 本地检测，可用于文本整理）`);
    polishModelSelect.value = model.id;
    localModelMessage.textContent = `当前文本整理使用 Ollama / ${model.id}。检测不会下载模型。`;
    return;
  }
  localModelMessage.textContent = `${model.provider} / ${model.name} 已检测到；当前版本暂未接入该提供方的文本整理调用。`;
}

function ensurePolishOption(modelId, label) {
  if ([...polishModelSelect.options].some((option) => option.value === modelId)) return;
  const option = document.createElement("option");
  option.value = modelId;
  option.textContent = label;
  option.dataset.provider = "ollama";
  option.dataset.modelId = modelId;
  polishModelSelect.append(option);
}

function renderLocalProviderResult(provider) {
  const card = document.createElement("section");
  card.className = `local-provider-result ${provider.online ? "is-online" : "is-offline"}`;
  const heading = document.createElement("div");
  heading.className = "local-provider-head";
  const title = document.createElement("strong");
  title.textContent = provider.name;
  const pill = document.createElement("span");
  pill.className = "pill";
  pill.textContent = provider.online ? "在线" : "离线";
  heading.append(title, pill);
  const message = document.createElement("p");
  message.textContent = `${provider.message} ${provider.can_polish ? "可用于当前文本整理。" : "当前仅检测展示。"}`;
  const url = document.createElement("small");
  url.textContent = provider.url;
  card.append(heading, message, url);
  if (provider.error) {
    const error = document.createElement("small");
    error.className = "provider-error";
    error.textContent = provider.error;
    card.append(error);
  }
  const models = provider.models || [];
  if (models.length) {
    const list = document.createElement("div");
    list.className = "local-model-list";
    for (const model of models) {
      const row = document.createElement("div");
      row.className = "local-model-row";
      const name = document.createElement("strong");
      name.textContent = model.name;
      const meta = document.createElement("span");
      const details = [model.size_label, model.modified_at, model.can_polish ? "可用于文本整理" : "仅检测展示"].filter(Boolean);
      meta.textContent = details.join(" · ");
      const note = document.createElement("small");
      note.textContent = model.recommendation || "";
      row.append(name, meta, note);
      list.append(row);
    }
    card.append(list);
  }
  return card;
}

async function refreshSelectedOllamaModel() {
  const modelId = ollamaManagedModelSelect.value;
  if (!modelId || !lastOllamaStatus) return;
  const selectedMeta = selectedManagedModelMeta();
  const isOllamaModel = selectedMeta.provider === "ollama";
  const available = Boolean(
    selectedMeta.available
      || (lastOllamaStatus.local_models || []).some((name) => normalizeOllamaId(name) === normalizeOllamaId(modelId)),
  );
  const selectedLabel = selectedMeta.model?.name || modelId;
  ollamaModelPath.textContent = selectedMeta.model
    ? `${modelSourceLabel(selectedMeta.model)}：${providerLabel(selectedMeta.model.provider)} · ${displayModelPath(selectedMeta.model.path_or_id)}`
    : isOllamaModel
      ? "Ollama 模型由 Ollama 管理，不下载到项目目录。"
      : "本地模型已绑定，不由 Ollama 下载。";
  if (!isOllamaModel) {
    ollamaProgress.hidden = true;
    ollamaProgress.setAttribute("aria-hidden", "true");
    ollamaDownloadButton.disabled = true;
    ollamaCancelButton.disabled = true;
    ollamaDownloadLabel.textContent = available ? "本地已就绪" : "无需下载";
    ollamaMessage.textContent = available ? `已导入并可用：${selectedLabel}` : `未检测到：${selectedLabel}`;
    return;
  }
  const downloading = await refreshOllamaPullStatus(modelId);
  if (downloading) return;
  ollamaDownloadButton.disabled = !lastOllamaStatus.available || available;
  ollamaCancelButton.disabled = true;
  ollamaDownloadLabel.textContent = available ? "模型已就绪" : "下载模型";
}

async function refreshOllamaPullStatus(modelId) {
  try {
    const response = await fetch(`/api/ollama/models/${encodeURIComponent(modelId)}/pull`);
    const status = await response.json();
    renderOllamaPullStatus(status);
    return status.state === "downloading";
  } catch {
    return false;
  }
}

function startOllamaPolling(modelId) {
  clearInterval(ollamaPollTimer);
  ollamaPollTimer = setInterval(async () => {
    const downloading = await refreshOllamaPullStatus(modelId);
    if (!downloading) {
      clearInterval(ollamaPollTimer);
      await refreshOllamaStatus();
    }
  }, 1800);
}

function renderOllamaPullStatus(status) {
  const downloading = status.state === "downloading";
  const progress = Math.max(0, Math.min(100, Number(status.progress || 0)));
  ollamaProgress.hidden = !(downloading || progress > 0);
  ollamaProgress.setAttribute("aria-hidden", ollamaProgress.hidden ? "true" : "false");
  ollamaProgressFill.style.width = `${progress}%`;
  const byteLabel =
    status.completed_bytes && status.total_bytes
      ? ` · ${formatBytes(status.completed_bytes)} / ${formatBytes(status.total_bytes)}`
      : "";
  ollamaProgressLabel.textContent = `${status.progress_label || "下载进度"} · ${progress}%${byteLabel}`;
  ollamaDownloadButton.disabled = downloading || status.state === "completed";
  ollamaCancelButton.disabled = !downloading;
  ollamaDownloadLabel.textContent = downloading ? "下载中" : status.state === "completed" ? "模型已就绪" : "下载模型";
  ollamaCancelLabel.textContent = downloading ? "取消下载" : "取消下载";
  if (status.error) {
    ollamaMessage.textContent = status.error;
  } else if (status.message && status.state !== "idle") {
    ollamaMessage.textContent = status.message;
  }
}

async function refreshModelStatus() {
  try {
    const response = await fetch("/api/model");
    const status = await response.json();
    renderModelStatus(status);
    return status;
  } catch (error) {
    modelMessage.textContent = `模型状态检测失败：${error.message}`;
    modelDownloadButton.disabled = false;
    return null;
  }
}

function startModelPolling() {
  clearInterval(modelPollTimer);
  modelPollTimer = setInterval(async () => {
    const status = await refreshModelStatus();
    if (!status || ["completed", "failed", "canceled"].includes(status.download_state)) {
      clearInterval(modelPollTimer);
    }
  }, 2500);
}

function renderModelStatus(status) {
  lastModelStatus = status;
  renderModelOptions(status);
  renderSelectedWhisperModelMeta();
  modelMessage.textContent = status.error || status.message;
  const plannedDevice = (status.configured_device || "unknown").toUpperCase();
  const activeDevice = status.active_device ? status.active_device.toUpperCase() : null;
  const computeType = status.active_compute_type ? ` / ${status.active_compute_type}` : "";
  modelDevice.textContent = activeDevice
    ? `运行设备：${activeDevice}${computeType}`
    : `计划设备：${plannedDevice}（模型加载后确认）`;
  modelDevice.dataset.device = (status.active_device || status.configured_device || "unknown").toLowerCase();
  modelPath.textContent = status.available
    ? `当前模型：${status.active_path}`
    : `默认检查：${status.managed_path}`;
  const selectedWhisper = (status.models || []).find((model) => model.id === status.selected_model);
  const configuredPath = selectedWhisper?.configured_path || status.configured_path || "";
  if (document.activeElement !== whisperModelPath) {
    whisperModelPath.value = configuredPath;
  }
  whisperModelPathMessage.textContent = configuredPath
    ? `已绑定：${configuredPath}`
    : "默认先检查项目 models 文件夹；此处填写完整目录后会写入配置。";

  const downloading = status.download_state === "downloading";
  const engine = selectedTranscriptionEngine();
  modelSelect.disabled = downloading || engine === "ollama_audio" || engine === "mlx-whisper" || engine === "qwen-audio" || engine === "mlx-vlm-audio";
  modelDownloadButton.disabled = !modelSelect.value || status.available || downloading;
  modelCancelButton.disabled = !downloading;
  modelRefreshButton.disabled = downloading;
  bindWhisperModelPathButton.disabled = downloading || !modelSelect.value;
  unbindWhisperModelPathButton.disabled = downloading || !modelSelect.value || !configuredPath;
  modelDownloadLabel.textContent = downloading ? "下载中" : status.available ? "模型已就绪" : "下载模型";
  modelCancelLabel.textContent = downloading ? "取消下载" : "取消下载";
  renderModelDownloadProgress(status, downloading);
  if (!modelRefreshButton.disabled) {
    modelRefreshLabel.textContent = "重新检测";
  }
  renderModeStatus();
  renderModelDetection(lastModelRegistry?.errors || []);
  renderEnvironmentStatus();
  updateWorkbenchSummaries();
}

function renderModelDownloadProgress(status, downloading) {
  const progress = Math.max(0, Math.min(100, Number(status.download_progress || 0)));
  const shouldShow = downloading || progress > 0;
  modelProgress.hidden = !shouldShow;
  modelProgress.setAttribute("aria-hidden", shouldShow ? "false" : "true");
  modelProgressFill.style.width = `${progress}%`;

  const byteLabel =
    status.downloaded_bytes && status.total_bytes
      ? ` · ${formatBytes(status.downloaded_bytes)} / ${formatBytes(status.total_bytes)}`
      : "";
  const label = status.download_progress_label || (downloading ? "下载中" : "下载进度");
  modelProgressLabel.textContent = `${label} · ${progress}%${byteLabel}`;
}

function renderModelOptions(status) {
  const models = status.models || [];
  if (!models.length) return;

  const existingValues = [...modelSelect.options].map((option) => option.value).join("|");
  const nextValues = ["", ...models.map((model) => model.id)].join("|");
  if (existingValues !== nextValues) {
    modelSelect.replaceChildren(
      new Option("请选择 Whisper 模型", ""),
      ...models.map((model) => {
        const option = document.createElement("option");
        option.value = model.id;
        option.textContent = model.available ? `${model.label}（已存在）` : model.label;
        option.title = model.meta ? `${model.meta.positioning}；${model.meta.description}` : model.label;
        return option;
      }),
    );
  } else {
    for (const option of modelSelect.options) {
      const model = models.find((item) => item.id === option.value);
      if (model) {
        option.textContent = model.available ? `${model.label}（已存在）` : model.label;
        option.title = model.meta ? `${model.meta.positioning}；${model.meta.description}` : model.label;
      }
    }
  }

  if (modelSelect.value && models.some((model) => model.id === modelSelect.value)) {
    modelSelect.value = modelSelect.value;
  } else if (status.selected_model && models.some((model) => model.id === status.selected_model)) {
    modelSelect.value = status.selected_model;
  } else {
    modelSelect.value = "";
  }
}

function selectedWhisperModel() {
  const models = lastModelStatus?.models || [];
  return models.find((model) => model.id === modelSelect.value) || models.find((model) => model.id === lastModelStatus?.selected_model);
}

function renderSelectedWhisperModelMeta() {
  const model = selectedWhisperModel();
  const meta = model?.meta;
  if (!model || !meta) {
    modelDescription.textContent = "";
    modelInfoPopover.replaceChildren();
    return;
  }
  modelDescription.replaceChildren(renderWhisperSummary(model, meta));
  modelInfoPopover.replaceChildren(renderWhisperDetail(model, meta));
}

function renderWhisperSummary(model, meta) {
  const wrap = document.createElement("div");
  wrap.className = "model-summary";
  const title = document.createElement("strong");
  title.textContent = `${model.label} · ${meta.positioning}`;
  const text = document.createElement("span");
  text.textContent = `速度：${meta.speed}；准确率：${meta.accuracy}；资源：${meta.resource}。${meta.mac_m4_air_advice}`;
  wrap.append(title, text);
  return wrap;
}

function renderWhisperDetail(model, meta) {
  const wrap = document.createElement("div");
  wrap.className = "model-info-card";
  const title = document.createElement("strong");
  title.textContent = `${model.label} 说明`;
  const description = document.createElement("p");
  description.textContent = meta.description;
  const rows = [
    ["模型定位", meta.positioning],
    ["速度", meta.speed],
    ["准确率", meta.accuracy],
    ["资源占用", meta.resource],
    ["适用场景", (meta.recommended_for || []).join(" / ")],
    ["M 系列 MacBook Air 16GB", meta.mac_m4_air_advice],
  ];
  const grid = document.createElement("dl");
  for (const [label, value] of rows) {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value || "-";
    grid.append(dt, dd);
  }
  wrap.append(title, description, grid);
  return wrap;
}
