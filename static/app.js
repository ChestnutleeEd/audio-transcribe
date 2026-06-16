const form = document.querySelector("#job-form");
const resetButton = document.querySelector("#reset-button");
const fileInput = document.querySelector("#file-input");
const fileLabel = document.querySelector("#file-label");
const submitButton = form.querySelector(".primary");
const startTimeInput = form.querySelector('input[name="start_time"]');
const endTimeInput = form.querySelector('input[name="end_time"]');
const jobsList = document.querySelector("#jobs-list");
const jobSummary = document.querySelector("#job-summary");
const jobsRefreshButton = document.querySelector("#jobs-refresh-button");
const modelSelect = document.querySelector("#model-select");
const modelMessage = document.querySelector("#model-message");
const modelDevice = document.querySelector("#model-device");
const modelPath = document.querySelector("#model-path");
const modelDownloadButton = document.querySelector("#model-download-button");
const modelDownloadLabel = document.querySelector("#model-download-label");
const modelCancelButton = document.querySelector("#model-cancel-button");
const modelCancelLabel = document.querySelector("#model-cancel-label");
const modelProgress = document.querySelector("#model-progress");
const modelProgressFill = document.querySelector("#model-progress-fill");
const modelProgressLabel = document.querySelector("#model-progress-label");
const modelRefreshButton = document.querySelector("#model-refresh-button");
const modelRefreshLabel = document.querySelector("#model-refresh-label");
const mockBanner = document.querySelector("#mock-banner");
const enablePolishInput = document.querySelector("#enable-polish");
const polishModelSelect = document.querySelector("#polish-model-select");
const polishField = document.querySelector("#polish-field");
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
const ollamaProgress = document.querySelector("#ollama-progress");
const ollamaProgressFill = document.querySelector("#ollama-progress-fill");
const ollamaProgressLabel = document.querySelector("#ollama-progress-label");

let jobsPollTimer = null;
let modelPollTimer = null;
let ollamaPollTimer = null;
let lastOllamaStatus = null;
let clipDefaultsReady = false;
let clipRangeTouched = false;

refreshModelStatus();
refreshOllamaStatus();
refreshJobs();
startJobsPolling();
updateEngineControls();
updatePolishControls();

jobsRefreshButton.addEventListener("click", refreshJobs);
enablePolishInput.addEventListener("change", updatePolishControls);
form.querySelectorAll('input[name="transcription_engine"]').forEach((input) => {
  input.addEventListener("change", updateEngineControls);
});
ollamaManagedModelSelect.addEventListener("change", refreshSelectedOllamaModel);

modelSelect.addEventListener("change", async () => {
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
  clipDefaultsReady = false;
  clipRangeTouched = false;
  setClipRange("00:00:00", "00:00:00");
  if (file) {
    loadMediaDuration(file);
  }
});

resetButton.addEventListener("click", () => {
  form.reset();
  fileLabel.textContent = "选择本地音频或视频";
  clipDefaultsReady = false;
  clipRangeTouched = false;
  setClipRange("00:00:00", "00:00:00");
});

startTimeInput.addEventListener("change", () => {
  clipRangeTouched = true;
});

endTimeInput.addEventListener("change", () => {
  clipRangeTouched = true;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const ready = await ensureSelectedOllamaModelsReady();
  if (!ready) return;

  const data = new FormData(form);
  const selectedFormats = [...form.querySelectorAll('input[name="formats"]:checked')].map((input) => input.value);
  data.set("formats", selectedFormats.join(","));
  data.set("include_timestamps", form.querySelector('input[name="include_timestamps"]').checked ? "true" : "false");
  data.set("transcription_engine", selectedTranscriptionEngine());
  data.set("whisper_model_id", modelSelect.value || "");
  data.set("transcription_model_id", ollamaTranscriptionModelSelect.value || "gemma4:12b");
  data.set("enable_polish", enablePolishInput.checked ? "true" : "false");
  if (!enablePolishInput.checked) {
    data.delete("polish_model_id");
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

  submitButton.disabled = true;
  try {
    const response = await fetch("/api/jobs", { method: "POST", body: data });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "任务创建失败");
    }
    form.reset();
    fileLabel.textContent = "选择本地音频或视频";
    clipDefaultsReady = false;
    clipRangeTouched = false;
    setClipRange("00:00:00", "00:00:00");
    await refreshJobs();
  } catch (error) {
    window.alert(error.message);
  } finally {
    submitButton.disabled = false;
  }
});

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
}

function renderJobs(jobs) {
  const activeCount = jobs.filter((job) => ["queued", "running"].includes(job.state)).length;
  jobSummary.textContent = jobs.length ? `${jobs.length} 个任务，${activeCount} 个进行中或排队` : "等待创建任务";
  jobsList.replaceChildren(...jobs.map(renderJob));
  if (!jobs.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "还没有任务。提交后会在这里显示队列、进度和文件。";
    jobsList.append(empty);
  }
}

function renderJob(job) {
  const item = document.createElement("article");
  item.className = `job-item state-${job.state}`;

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
  meta.textContent = `任务 ${shortId(job.id)}`;
  titleWrap.append(title, meta);

  const pill = document.createElement("span");
  pill.className = "pill";
  pill.textContent = stateLabel(job.state);
  header.append(titleWrap, pill);

  const bar = document.createElement("div");
  bar.className = "job-progress";
  bar.style.setProperty("--progress", Number(job.progress || 0));
  const barFill = document.createElement("span");
  bar.append(barFill);

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
  if (["queued", "running"].includes(job.state)) {
    const stopButton = document.createElement("button");
    stopButton.className = "danger";
    stopButton.type = "button";
    stopButton.textContent = "停止";
    stopButton.addEventListener("click", () => cancelJob(job.id, stopButton));
    actions.append(stopButton);
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

  item.append(header, details, bar, message, warnings, events, actions, outputs);
  return item;
}

function renderJobEvents(events) {
  const wrap = document.createElement("div");
  wrap.className = "job-events";
  if (!events.length) return wrap;

  const title = document.createElement("h4");
  title.textContent = "Events";
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
  size.textContent = formatBytes(file.bytes);

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
    window.alert(payload.detail || "停止任务失败");
    return;
  }
  await refreshJobs();
}

async function deleteOutput(jobId, fileName) {
  const approved = window.confirm(`删除转录文件 ${fileName}？`);
  if (!approved) return;
  await fetch(`/api/jobs/${jobId}/outputs/${encodeURIComponent(fileName)}`, { method: "DELETE" });
  await refreshJobs();
}

function stateLabel(state) {
  return {
    queued: "排队中",
    running: "处理中",
    completed: "已完成",
    failed: "失败",
    canceled: "已停止",
  }[state] || state;
}

function shortId(id) {
  return String(id || "").slice(0, 10);
}

function jobDetails(job) {
  return [
    { label: "引擎", value: transcriptionEngineLabel(job.transcription_engine) },
    { label: "语言", value: languageLabel(job.language) },
    { label: "截取", value: timeRangeLabel(job.start_time, job.end_time) },
    { label: "模型", value: job.model_label || "large-v3" },
    { label: "Polish", value: job.enable_polish ? job.polish_model_id || "已启用" : "未启用" },
    { label: "格式", value: job.formats?.length ? job.formats.map(formatLabel).join(" / ") : "未选择" },
    { label: "时间轴", value: job.include_timestamps ? "带时间轴" : "纯文本" },
    { label: "耗时", value: elapsedLabel(job) },
  ];
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
    `模型：${job.model_label || "large-v3"}`,
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
    ollama_audio: "Gemma 4 12B direct audio",
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
  }[format] || format;
}

function formatBytes(bytes) {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`;
}

function selectedTranscriptionEngine() {
  return form.querySelector('input[name="transcription_engine"]:checked')?.value || "whisper";
}

function updateEngineControls() {
  const usingOllamaAudio = selectedTranscriptionEngine() === "ollama_audio";
  modelSelect.disabled = usingOllamaAudio || modelSelect.disabled;
  if (!usingOllamaAudio) {
    refreshModelStatus();
  }
  ollamaTranscriptionModelSelect.disabled = !usingOllamaAudio;
}

function updatePolishControls() {
  polishField.hidden = !enablePolishInput.checked;
  polishModelSelect.disabled = !enablePolishInput.checked;
}

async function ensureSelectedOllamaModelsReady() {
  const required = [];
  if (selectedTranscriptionEngine() === "ollama_audio") {
    required.push({ modelId: ollamaTranscriptionModelSelect.value || "gemma4:12b", task: "direct_audio" });
  }
  if (enablePolishInput.checked) {
    required.push({ modelId: polishModelSelect.value || "gemma4:12b", task: "polish" });
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
    window.alert("Ollama 服务不可用，请先启动 Ollama。");
    return false;
  }

  for (const item of uniqueChecks) {
    const check = await preflightOllamaModel(item.modelId, item.task);
    if (!check.service_available) {
      window.alert("Ollama 服务不可用，请先启动 Ollama。");
      return false;
    }
    if (!check.model_exists) {
      const started = await confirmAndStartOllamaDownload(item.modelId);
      if (started) {
        window.alert(`${item.modelId} 下载已开始。请等待下载完成后再提交任务。`);
      }
      return false;
    }
    if (!check.can_generate) {
      window.alert(check.error || check.message || `${item.modelId} preflight 未通过`);
      return false;
    }
    if (check.warnings?.length) {
      ollamaMessage.textContent = check.warnings.join(" ");
    }
  }
  return true;
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

function renderOllamaOptions(status) {
  const transcriptionModels = status.transcription_models || [];
  const polishModels = status.polish_models || [];
  if (transcriptionModels.length) {
    ollamaTranscriptionModelSelect.replaceChildren(
      ...transcriptionModels.map((model) => {
        const option = document.createElement("option");
        option.value = model.id;
        option.textContent = `${model.label}（实验性 direct audio${model.available ? "，已存在" : ""}）`;
        return option;
      }),
    );
  }

  if (polishModels.length) {
    const currentPolishModel = polishModelSelect.value || "gemma4:12b";
    polishModelSelect.replaceChildren(
      ...polishModels.map((model) => {
        const option = document.createElement("option");
        option.value = model.id;
        option.textContent = `${model.label}（${model.role}${model.default ? "，默认" : ""}${model.available ? "，已存在" : ""}）`;
        return option;
      }),
    );
    polishModelSelect.value = [...polishModelSelect.options].some((option) => option.value === currentPolishModel)
      ? currentPolishModel
      : polishModels[0]?.id || "gemma4:12b";
  }

  const combined = [...transcriptionModels, ...polishModels];
  const seen = new Set();
  const options = [];
  for (const model of combined) {
    if (seen.has(model.id)) continue;
    seen.add(model.id);
    const option = document.createElement("option");
    option.value = model.id;
    option.textContent = `${model.label}${model.experimental ? "（实验性）" : ""}${model.available ? "（已存在）" : ""}`;
    options.push(option);
  }
  if (options.length) {
    const current = ollamaManagedModelSelect.value;
    ollamaManagedModelSelect.replaceChildren(...options);
    if ([...ollamaManagedModelSelect.options].some((option) => option.value === current)) {
      ollamaManagedModelSelect.value = current;
    }
  }
}

async function refreshSelectedOllamaModel() {
  const modelId = ollamaManagedModelSelect.value;
  if (!modelId || !lastOllamaStatus) return;
  const option = [...(lastOllamaStatus.transcription_models || []), ...(lastOllamaStatus.polish_models || [])].find(
    (model) => model.id === modelId,
  );
  const available = Boolean(option?.available);
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
  renderModelOptions(status);
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
    : `将下载到：${status.managed_path}`;

  const downloading = status.download_state === "downloading";
  modelSelect.disabled = downloading;
  modelDownloadButton.disabled = status.available || downloading;
  modelCancelButton.disabled = !downloading;
  modelRefreshButton.disabled = downloading;
  modelDownloadLabel.textContent = downloading ? "下载中" : status.available ? "模型已就绪" : "下载模型";
  modelCancelLabel.textContent = downloading ? "取消下载" : "取消下载";
  renderModelDownloadProgress(status, downloading);
  if (!modelRefreshButton.disabled) {
    modelRefreshLabel.textContent = "重新检测";
  }
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
  const nextValues = models.map((model) => model.id).join("|");
  if (existingValues !== nextValues) {
    modelSelect.replaceChildren(
      ...models.map((model) => {
        const option = document.createElement("option");
        option.value = model.id;
        option.textContent = model.available ? `${model.label}（已存在）` : model.label;
        return option;
      }),
    );
  } else {
    for (const option of modelSelect.options) {
      const model = models.find((item) => item.id === option.value);
      if (model) {
        option.textContent = model.available ? `${model.label}（已存在）` : model.label;
      }
    }
  }

  modelSelect.value = status.selected_model;
}
