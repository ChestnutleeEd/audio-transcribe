import re

with open("static/index.html", "r") as f:
    html = f.read()

# Extract head and scripts/dialogs
head_match = re.search(r"<head>.*?</head>", html, re.DOTALL)
head_content = head_match.group(0)

# Extract scripts and dialogs at the bottom
dialogs_scripts = re.search(r"(<dialog id=\"prompt-modal\".*?</html>)", html, re.DOTALL).group(0)

# Extract job-form
form_match = re.search(r"(<form id=\"job-form\".*?</form>)", html, re.DOTALL)
form_content = form_match.group(1)

# Inside the monitor, there's diagnostic-card, jobs header, jobs-region (which has jobs-list and history-card), environment-panel, legacy-status, model-details
# I will extract each piece carefully.

# jobs-head (contains h2 "任务列表" and #job-summary)
jobs_head_match = re.search(r"(<div class=\"panel-head\">\s*<div>\s*<h2>任务列表</h2>.*?(?=<div id=\"jobs-region\">))", html, re.DOTALL)
jobs_head = jobs_head_match.group(1) if jobs_head_match else ""

# jobs-list (and cleanup status)
jobs_list_match = re.search(r"(<p class=\"cleanup-status\".*?<div id=\"jobs-list\" class=\"jobs-list\"></div>)", html, re.DOTALL)
jobs_list = jobs_list_match.group(1) if jobs_list_match else ""

# history-card
history_match = re.search(r"(<div class=\"model-card history-card\">.*?</div>\s*</div>)", html, re.DOTALL)
history_card = history_match.group(1) if history_match else ""
if history_card.endswith("</div>\s*</div>"):
    # strip trailing
    history_card = history_card.rsplit("</div>", 1)[0].strip()

# environment-panel
env_match = re.search(r"(<details class=\"model-card environment-card\" id=\"environment-panel\".*?</details>)", html, re.DOTALL)
env_panel = env_match.group(1) if env_match else ""

# legacy status & model-details (Ollama)
legacy_match = re.search(r"(<div class=\"legacy-status-panels\".*?<details class=\"model-details\".*?</details>)", html, re.DOTALL)
legacy_panels = legacy_match.group(1) if legacy_match else ""

# Assemble new HTML
new_html = f"""<!doctype html>
<html lang="zh-CN">
  {head_content}
  <body>
    <!-- Welcome Page -->
    <div id="welcome-page" class="welcome-container">
      <nav class="welcome-nav">
        <div class="logo">
          <svg viewBox="0 0 64 64" width="24" height="24" class="logo-icon"><rect width="64" height="64" rx="14" fill="#070707"/><path d="M18 40V24M28 48V16M38 42V22M48 36V28" stroke="#d8b15e" stroke-width="5" stroke-linecap="round"/></svg>
          Audio Transcribe
        </div>
        <div class="nav-links">
          <span>Features</span>
          <span>Workflow</span>
          <span>Models</span>
        </div>
        <div class="nav-actions">
          <button class="primary small-button" id="nav-start-button">Start Dashboard</button>
        </div>
      </nav>
      <div class="hero-section" aria-labelledby="page-title">
        <div class="hero-content">
          <p class="eyebrow">Local Model Workstation</p>
          <h1 id="page-title">本地 AI 音频与视频转录工作台</h1>
          <p class="lede">基于本地模型池的高性能转写台。支持长音频智能切片、视频转音频、Whisper/MLX 原生加速，以及 LLM 智能文本整理。全程本地运行，保护隐私数据。</p>
          <div class="hero-actions">
            <button class="primary glow-button" id="start-app-button">开始转录</button>
            <button class="secondary glass-button" id="hero-tutorial-button">了解工作流</button>
          </div>
          <p class="mock-banner" id="mock-banner" hidden>Mock 模式：不会调用真实模型</p>
        </div>
        <div class="hero-visual">
          <img src="/assets/images/hero-product-mockup.webp" alt="Dashboard Mockup" class="floating-mockup" />
        </div>
      </div>
      <div class="feature-cards">
        <div class="glass-card stagger-1">
          <h3>Local Models</h3>
          <p>Seamlessly integrate with Whisper and MLX native models for maximum speed.</p>
        </div>
        <div class="glass-card stagger-2">
          <h3>Long Audio Chunking</h3>
          <p>Smart VAD-based slicing ensures even hours of audio are transcribed flawlessly.</p>
        </div>
        <div class="glass-card stagger-3">
          <h3>Transcript Polish</h3>
          <p>Use local LLMs to automatically format, punctuate, and correct transcripts.</p>
        </div>
      </div>
    </div>

    <!-- App Dashboard (Hidden initially) -->
    <div id="app-dashboard" class="dashboard-container" hidden>
      <!-- Left Sidebar (approx 280px) -->
      <aside class="dashboard-sidebar">
        <div class="sidebar-logo">
          <svg viewBox="0 0 64 64" width="32" height="32" class="logo-icon"><rect width="64" height="64" rx="14" fill="#070707"/><path d="M18 40V24M28 48V16M38 42V22M48 36V28" stroke="#d8b15e" stroke-width="5" stroke-linecap="round"/></svg>
          Audio Transcribe
        </div>
        <nav class="sidebar-nav">
          <a href="#" class="active" title="转录工作台">
            <svg viewBox="0 0 24 24" aria-hidden="true" width="20" height="20" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round"><path d="M12 20V10M18 20V4M6 20v-4"/></svg>
            转录工作台
          </a>
          <a href="#" title="文件任务">
            <svg viewBox="0 0 24 24" aria-hidden="true" width="20" height="20" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            文件任务
          </a>
        </nav>
        
        <div class="sidebar-modules">
          {history_card}
          {env_panel}
          {legacy_panels}
        </div>

        <div class="sidebar-spacer"></div>
        <div class="sidebar-status">
          <span class="status-dot"></span> Local Mode / Ready
        </div>
      </aside>

      <!-- Main Content Area -->
      <main class="dashboard-main">
        <!-- Top Header -->
        <header class="dashboard-header">
          <div class="header-title">
            <span class="breadcrumb">Workspace /</span> 新建任务
          </div>
          <div class="header-actions">
            <button class="icon-button" type="button" id="tutorial-button-dash" aria-label="使用教程" title="使用教程">
              <svg viewBox="0 0 24 24" aria-hidden="true" width="20" height="20" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round"><path d="M4 19.5V5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1 0-4h12"/><path d="M8 7h6"/></svg>
            </button>
            <button class="icon-button" id="return-home-button" title="返回欢迎页">
              <svg viewBox="0 0 24 24" aria-hidden="true" width="20" height="20" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
            </button>
          </div>
        </header>

        <!-- Main Form Area -->
        <div class="dashboard-center">
           {form_content}
        </div>
      </main>
      
      <!-- Right Panel (approx 360px) -->
      <aside class="dashboard-right-panel" aria-live="polite">
         <div class="diagnostic-card" id="diagnostic-card" hidden></div>
         {jobs_head}
         <div id="jobs-region" class="jobs-region-flex">
           {jobs_list}
         </div>
      </aside>
    </div>

    {dialogs_scripts}
"""

with open("static/index.html", "w") as f:
    f.write(new_html)

print("HTML restructured!")
