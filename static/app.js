const form = document.querySelector("#job-form");
const resetButton = document.querySelector("#reset-button");
const fileInput = document.querySelector("#file-input");
const fileLabel = document.querySelector("#file-label");
const statePill = document.querySelector("#state-pill");
const jobId = document.querySelector("#job-id");
const progressRing = document.querySelector(".progress-ring");
const progressText = document.querySelector("#progress-text");
const message = document.querySelector("#message");
const outputs = document.querySelector("#outputs");
const submitButton = form.querySelector(".primary");
const modelMessage = document.querySelector("#model-message");
const modelPath = document.querySelector("#model-path");
const modelDownloadButton = document.querySelector("#model-download-button");
const modelDownloadLabel = document.querySelector("#model-download-label");

let pollTimer = null;
let modelPollTimer = null;

refreshModelStatus();

modelDownloadButton.addEventListener("click", async () => {
  const approved = window.confirm(
    "large-v3 模型文件很大，会下载到项目的 models/large-v3-local 目录。确认开始下载吗？",
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

fileInput.addEventListener("change", () => {
  fileLabel.textContent = fileInput.files[0]?.name || "选择本地音频或视频";
});

resetButton.addEventListener("click", () => {
  form.reset();
  fileLabel.textContent = "选择本地音频或视频";
  setStatus({ id: "", state: "idle", progress: 0, message: "选择文件或粘贴链接后开始。", outputs: [] });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form);
  const selectedFormats = [...form.querySelectorAll('input[name="formats"]:checked')].map((input) => input.value);
  data.set("formats", selectedFormats.join(","));
  data.set("include_timestamps", form.querySelector('input[name="include_timestamps"]').checked ? "true" : "false");

  if (!fileInput.files.length) {
    data.delete("file");
  }

  submitButton.disabled = true;
  setStatus({ id: "", state: "queued", progress: 1, message: "正在提交任务", outputs: [] });

  try {
    const response = await fetch("/api/jobs", { method: "POST", body: data });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "任务创建失败");
    }
    setStatus(payload);
    startPolling(payload.id);
  } catch (error) {
    setStatus({ id: "", state: "failed", progress: 100, message: "任务创建失败", error: error.message, outputs: [] });
    submitButton.disabled = false;
  }
});

function startPolling(id) {
  clearInterval(pollTimer);
  pollTimer = setInterval(async () => {
    const response = await fetch(`/api/jobs/${id}`);
    const payload = await response.json();
    setStatus(payload);
    if (["completed", "failed"].includes(payload.state)) {
      clearInterval(pollTimer);
      submitButton.disabled = false;
    }
  }, 1600);
}

function setStatus(status) {
  const progress = Number(status.progress || 0);
  statePill.textContent = status.state;
  jobId.textContent = status.id ? `任务 ${status.id.slice(0, 10)}` : "等待创建任务";
  progressRing.style.setProperty("--progress", progress);
  progressText.textContent = `${progress}%`;
  message.textContent = status.error || status.message || "";
  outputs.replaceChildren(...(status.outputs || []).map(renderDownload));
}

function renderDownload(file) {
  const link = document.createElement("a");
  link.className = "download";
  link.href = file.download_url;
  link.download = file.name;
  link.innerHTML = `<span>${file.name}</span><small>${formatBytes(file.bytes)}</small>`;
  link.addEventListener("click", () => {
    setTimeout(() => {
      link.style.opacity = "0.48";
      link.querySelector("small").textContent = "已请求删除";
    }, 500);
  });
  return link;
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
    if (!status || ["completed", "failed"].includes(status.download_state)) {
      clearInterval(modelPollTimer);
    }
  }, 2500);
}

function renderModelStatus(status) {
  modelMessage.textContent = status.error || status.message;
  modelPath.textContent = status.available
    ? `当前模型：${status.active_path}`
    : `将下载到：${status.managed_path}`;

  const downloading = status.download_state === "downloading";
  modelDownloadButton.disabled = status.available || downloading;
  modelDownloadLabel.textContent = downloading ? "下载中" : status.available ? "模型已就绪" : "下载模型";
}
