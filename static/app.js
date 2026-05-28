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
const modelRefreshButton = document.querySelector("#model-refresh-button");
const modelRefreshLabel = document.querySelector("#model-refresh-label");

let jobsPollTimer = null;
let modelPollTimer = null;
let clipDefaultsReady = false;
let clipRangeTouched = false;

refreshModelStatus();
refreshJobs();
startJobsPolling();

jobsRefreshButton.addEventListener("click", refreshJobs);

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
  const data = new FormData(form);
  const selectedFormats = [...form.querySelectorAll('input[name="formats"]:checked')].map((input) => input.value);
  data.set("formats", selectedFormats.join(","));
  data.set("include_timestamps", form.querySelector('input[name="include_timestamps"]').checked ? "true" : "false");
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

  item.append(header, details, bar, message, actions, outputs);
  return item;
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
    { label: "语言", value: languageLabel(job.language) },
    { label: "截取", value: timeRangeLabel(job.start_time, job.end_time) },
    { label: "模型", value: job.model_label || "large-v3" },
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
  if (!modelRefreshButton.disabled) {
    modelRefreshLabel.textContent = "重新检测";
  }
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
