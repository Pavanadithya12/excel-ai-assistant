// ==========================================================================
// AI EXCEL ASSISTANT - DYNAMIC APPLICATION CONTROLLER
// 100% Database-Driven • Direct Auth • Dynamic Document Type Detection
// ==========================================================================

// Global Application State
let token = localStorage.getItem("token") || null;
let currentUser = null;
let activeFile = null;
let activeSessionId = null;
let currentPendingEmail = null;

// DOM Elements Cache
const authScreen = document.getElementById("auth-screen");
const appContainer = document.getElementById("app-container");
const schemaModal = document.getElementById("schema-modal");
const historyModal = document.getElementById("history-modal");

// Sidebar & Workspace Elements
const fileInput = document.getElementById("file-input");
const btnUpload = document.getElementById("btn-upload-file");
const activeFileCard = document.getElementById("active-file-card");
const fileTypePill = document.getElementById("file-type-pill");
const fileNameDisplay = document.getElementById("file-name-display");
const fileSizeDisplay = document.getElementById("file-size-display");
const fileStatRows = document.getElementById("file-stat-rows");
const fileStatCols = document.getElementById("file-stat-cols");
const sheetDropdown = document.getElementById("sheet-dropdown");
const btnInspectSchema = document.getElementById("btn-inspect-schema");
const btnDownloadOriginal = document.getElementById("btn-download-original");
const btnDownloadModified = document.getElementById("btn-download-modified");
const recentFilesList = document.getElementById("recent-files-list");

// Chat & Suggestion Elements
const chatStream = document.getElementById("chat-stream");
const welcomeHero = document.getElementById("welcome-hero");
const dynamicHeroChips = document.getElementById("dynamic-hero-chips");
const dynamicSuggestionsContainer = document.getElementById("dynamic-suggestions-container");
const bottomSuggestionsBar = document.getElementById("bottom-suggestions-bar");
const questionInput = document.getElementById("question-input");
const btnSubmitQuestion = document.getElementById("btn-submit-question");
const btnNewChat = document.getElementById("btn-new-chat");
const chatHistoryList = document.getElementById("chat-history-list");
const chatTitleHeader = document.getElementById("chat-title-header");
const activeSheetPill = document.getElementById("active-sheet-pill");

// User Profile Elements
const userName = document.getElementById("user-name");
const userAvatar = document.getElementById("user-avatar");
const btnLogout = document.getElementById("btn-logout");
const btnHistoryView = document.getElementById("btn-history-view");

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  checkAuthenticationState();
});

function setupEventListeners() {
  btnUpload.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", handleFileUpload);
  btnSubmitQuestion.addEventListener("click", sendQuestion);
  btnNewChat.addEventListener("click", startNewChat);
  btnInspectSchema.addEventListener("click", openSchemaModal);
  btnHistoryView.addEventListener("click", openHistoryModal);
  btnLogout.addEventListener("click", logout);

  // Enter sends question (Shift+Enter inserts newline)
  questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  });

  // Drag and drop for upload
  const dropzone = document.getElementById("upload-dropzone");
  if (dropzone) {
    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "var(--color-primary)";
    });
    dropzone.addEventListener("dragleave", () => {
      dropzone.style.borderColor = "#475569";
    });
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "#475569";
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileDirect(e.dataTransfer.files[0]);
      }
    });
  }
}

// Request Headers Helper
function getAuthHeaders(isFormData = false) {
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }
  return headers;
}

// ==========================================================================
// 1. AUTHENTICATION CONTROLLER (Direct Login & Sign Up Screen)
// ==========================================================================

async function checkAuthenticationState() {
  if (!token) {
    showDirectAuthScreen();
    return;
  }

  try {
    const res = await fetch("/api/auth/me", { headers: getAuthHeaders() });
    if (!res.ok) {
      logout();
      return;
    }
    currentUser = await res.json();
    showWorkspace();
    updateUserUI();
    loadRecentFiles();
    loadChatSessions();
  } catch (err) {
    console.error("Auth check failed:", err);
    logout();
  }
}

function showDirectAuthScreen() {
  authScreen.style.display = "flex";
  appContainer.style.display = "none";
  switchAuthTab("signin");
}

function showWorkspace() {
  authScreen.style.display = "none";
  appContainer.style.display = "flex";
}

function switchAuthTab(tab) {
  const tabSignin = document.getElementById("tab-signin");
  const tabSignup = document.getElementById("tab-signup");
  const viewSignin = document.getElementById("view-signin");
  const viewSignup = document.getElementById("view-signup");
  const viewOtp = document.getElementById("view-otp");

  viewOtp.style.display = "none";

  if (tab === "signin") {
    tabSignin.classList.add("active");
    tabSignup.classList.remove("active");
    viewSignin.style.display = "block";
    viewSignup.style.display = "none";
  } else if (tab === "signup") {
    tabSignup.classList.add("active");
    tabSignin.classList.remove("active");
    viewSignin.style.display = "none";
    viewSignup.style.display = "block";
  }
}

function showOTPView(email, devOtp) {
  currentPendingEmail = email;
  document.getElementById("view-signin").style.display = "none";
  document.getElementById("view-signup").style.display = "none";
  document.getElementById("view-otp").style.display = "block";
  document.getElementById("otp-target-email").innerText = email;

  if (devOtp) {
    document.getElementById("otp-dev-hint").style.display = "flex";
    document.getElementById("dev-otp-value").innerText = devOtp;
    document.getElementById("input-otp").value = devOtp;
  } else {
    document.getElementById("otp-dev-hint").style.display = "none";
  }
}

async function handleSignIn() {
  const email = document.getElementById("signin-email").value.trim();
  const password = document.getElementById("signin-password").value;

  if (!email || !password) {
    showNotification("Please enter both email and password.", "error");
    return;
  }

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (!res.ok) {
      if (res.status === 403) {
        showNotification("Email unverified. Enter the code sent to your email.", "info");
        showOTPView(email, res.headers.get("X-Dev-OTP"));
        return;
      }
      throw new Error(data.detail || "Sign in failed.");
    }

    token = data.access_token;
    localStorage.setItem("token", token);
    currentUser = data.user;

    showWorkspace();
    updateUserUI();
    loadRecentFiles();
    loadChatSessions();
    showNotification(`Welcome back, ${currentUser.full_name || currentUser.email}!`, "success");
  } catch (err) {
    showNotification(err.message, "error");
  }
}

async function handleSignUp() {
  const name = document.getElementById("signup-name").value.trim();
  const email = document.getElementById("signup-email").value.trim();
  const password = document.getElementById("signup-password").value;

  if (!name || !email || !password) {
    showNotification("Please fill in all registration fields.", "error");
    return;
  }

  try {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name: name, email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Registration failed.");

    showNotification(data.message, "success");
    showOTPView(email, data.dev_otp);
  } catch (err) {
    showNotification(err.message, "error");
  }
}

async function handleVerifyOTP() {
  const otp = document.getElementById("input-otp").value.trim();
  if (!otp || !currentPendingEmail) {
    showNotification("Please enter your 6-digit OTP code.", "error");
    return;
  }

  try {
    const res = await fetch("/api/auth/verify-otp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: currentPendingEmail, otp })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Verification failed.");

    token = data.access_token;
    localStorage.setItem("token", token);
    currentUser = data.user;

    showWorkspace();
    updateUserUI();
    loadRecentFiles();
    loadChatSessions();
    showNotification("Account successfully activated! Welcome to Excel AI Assistant.", "success");
  } catch (err) {
    showNotification(err.message, "error");
  }
}

async function handleResendOTP() {
  if (!currentPendingEmail) return;
  try {
    const res = await fetch("/api/auth/resend-otp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: currentPendingEmail })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to resend code.");
    showNotification("A new verification code was sent to your email.", "success");
  } catch (err) {
    showNotification(err.message, "error");
  }
}

function updateUserUI() {
  if (currentUser) {
    const displayName = currentUser.full_name || currentUser.email.split("@")[0];
    userName.innerText = displayName;
    userAvatar.innerText = displayName[0].toUpperCase();
  }
}

function logout() {
  token = null;
  currentUser = null;
  activeFile = null;
  activeSessionId = null;
  localStorage.removeItem("token");
  showDirectAuthScreen();
  showNotification("Signed out successfully.", "info");
}

// ==========================================================================
// 2. DOCUMENT UPLOAD & DYNAMIC TYPE DETECTION
// ==========================================================================

async function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  await handleFileDirect(file);
  fileInput.value = "";
}

async function handleFileDirect(file) {
  const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
  if (![".xlsx", ".xls", ".csv"].includes(ext)) {
    showNotification("Unsupported file format. Please upload .xlsx, .xls, or .csv", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    showNotification(`Uploading and analyzing ${file.name}...`, "info");
    const res = await fetch("/api/excel/upload", {
      method: "POST",
      headers: getAuthHeaders(true),
      body: formData
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Spreadsheet upload failed.");

    // Update state & UI
    setActiveFile(data.metadata || data);
    renderUploadConfirmation(data.metadata || data);
    showNotification(data.message || `Uploaded ${data.filename}`, "success");
  } catch (err) {
    showNotification("Upload failed: " + err.message, "error");
  }
}

function setActiveFile(fileMeta) {
  activeFile = fileMeta;
  activeFileCard.style.display = "flex";

  const fileTypeLabel = fileMeta.file_type || "Spreadsheet Document";
  fileTypePill.innerHTML = `<iconify-icon icon="lucide:file-spreadsheet"></iconify-icon> ${escapeHtml(fileTypeLabel)}`;
  fileNameDisplay.innerText = fileMeta.filename;
  fileSizeDisplay.innerText = formatBytes(fileMeta.file_size || 0);

  // Stats
  const rows = fileMeta.total_rows || 0;
  const cols = fileMeta.total_columns || 0;
  fileStatRows.innerHTML = `<iconify-icon icon="lucide:rows-3"></iconify-icon> ${rows.toLocaleString()} rows`;
  fileStatCols.innerHTML = `<iconify-icon icon="lucide:columns-3"></iconify-icon> ${cols.toLocaleString()} cols`;

  // Sheet Selector
  sheetDropdown.innerHTML = "";
  const sheets = fileMeta.sheet_names || [];
  sheets.forEach((sheet) => {
    const opt = document.createElement("option");
    opt.value = sheet;
    opt.innerText = `Worksheet: ${sheet}`;
    sheetDropdown.appendChild(opt);
  });

  btnDownloadOriginal.href = `/api/excel/${fileMeta.file_id || fileMeta.id}/download`;
  activeSheetPill.innerHTML = `<iconify-icon icon="lucide:check-circle-2" style="color: var(--color-success);"></iconify-icon> ${escapeHtml(fileMeta.filename)}`;

  // Update Dynamic Suggestions
  updateDynamicSuggestions(fileMeta.dynamic_suggestions || []);

  // Refresh database files list
  loadRecentFiles();
}

function renderUploadConfirmation(meta) {
  // Hide welcome dropzone and show chat confirmation card
  welcomeHero.style.display = "none";

  const row = document.createElement("div");
  row.className = "message-row assistant";

  const suggestions = meta.dynamic_suggestions || [];
  const chipsHtml = suggestions.map(q => `
    <button class="suggestion-chip" onclick="askDynamicQuestion('${escapeHtml(q)}')">
      <iconify-icon icon="lucide:sparkles" style="color: var(--color-primary);"></iconify-icon>
      ${escapeHtml(q)}
    </button>
  `).join("");

  row.innerHTML = `
    <div class="message-avatar"><iconify-icon icon="lucide:bot" width="20" height="20"></iconify-icon></div>
    <div class="message-bubble">
      <div style="font-weight: 700; color: #ffffff; margin-bottom: 4px;">
        <iconify-icon icon="lucide:file-check" style="color: var(--color-success);"></iconify-icon> Document Uploaded & Analyzed
      </div>
      <p style="color: var(--color-text-muted); font-size: 13px; margin-bottom: 12px;">
        Successfully parsed into your secured database. What would you like to calculate or visualize?
      </p>

      <div class="upload-confirm-card">
        <div class="confirm-header">
          <div class="confirm-title">
            <iconify-icon icon="lucide:table" style="color: var(--color-primary);"></iconify-icon>
            <span>${escapeHtml(meta.filename)}</span>
          </div>
          <span class="file-type-pill">${escapeHtml(meta.file_type || "Excel / CSV")}</span>
        </div>

        <div class="confirm-details-grid">
          <div class="confirm-detail-item">
            <span class="label">Document Size</span>
            <span class="value">${formatBytes(meta.file_size || 0)}</span>
          </div>
          <div class="confirm-detail-item">
            <span class="label">Detected Domain</span>
            <span class="value">${escapeHtml(meta.inferred_domain || "Tabular Data")}</span>
          </div>
          <div class="confirm-detail-item">
            <span class="label">Total Worksheets</span>
            <span class="value">${(meta.sheet_names || []).length} sheet(s) (${(meta.sheet_names || []).join(", ")})</span>
          </div>
          <div class="confirm-detail-item">
            <span class="label">Total Dimension</span>
            <span class="value">${(meta.total_rows || 0).toLocaleString()} rows × ${(meta.total_columns || 0).toLocaleString()} columns</span>
          </div>
        </div>

        ${suggestions.length > 0 ? `
          <div style="margin-top: 6px;">
            <div style="font-size: 11px; font-weight: 700; color: var(--color-text-dim); text-transform: uppercase; margin-bottom: 8px;">
              Dynamic Column-Based Suggestions:
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
              ${chipsHtml}
            </div>
          </div>
        ` : ''}
      </div>
    </div>
  `;

  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
}

function updateDynamicSuggestions(suggestions) {
  if (!suggestions || suggestions.length === 0) {
    bottomSuggestionsBar.style.display = "none";
    dynamicSuggestionsContainer.style.display = "none";
    return;
  }

  // Update Bottom Bar
  bottomSuggestionsBar.innerHTML = "";
  bottomSuggestionsBar.style.display = "flex";

  suggestions.forEach(q => {
    const chip = document.createElement("span");
    chip.className = "suggestion-chip";
    chip.innerHTML = `<iconify-icon icon="lucide:arrow-right" width="14" height="14"></iconify-icon> ${escapeHtml(q)}`;
    chip.onclick = () => askDynamicQuestion(q);
    bottomSuggestionsBar.appendChild(chip);
  });

  // Update Hero Chips
  dynamicHeroChips.innerHTML = "";
  dynamicSuggestionsContainer.style.display = "block";
  suggestions.forEach(q => {
    const chip = document.createElement("button");
    chip.className = "suggestion-chip";
    chip.innerHTML = `<iconify-icon icon="lucide:sparkles" style="color: var(--color-primary);"></iconify-icon> ${escapeHtml(q)}`;
    chip.onclick = () => askDynamicQuestion(q);
    dynamicHeroChips.appendChild(chip);
  });
}

function askDynamicQuestion(q) {
  questionInput.value = q;
  sendQuestion();
}

// ==========================================================================
// 3. DATABASE PERSISTED FILES & CHATS
// ==========================================================================

async function loadRecentFiles() {
  if (!token) return;
  try {
    const res = await fetch("/api/excel/files", { headers: getAuthHeaders() });
    if (!res.ok) return;
    const files = await res.json();

    recentFilesList.innerHTML = "";
    if (files.length === 0) {
      recentFilesList.innerHTML = `
        <div style="font-size: 12px; color: var(--color-text-dim); padding: 8px; text-align: center;">
          No documents uploaded yet
        </div>
      `;
      return;
    }

    files.forEach(f => {
      const item = document.createElement("div");
      item.className = `recent-file-item ${activeFile && (activeFile.file_id === f.id || activeFile.id === f.id) ? 'active' : ''}`;
      item.onclick = () => selectFileFromDatabase(f.id);
      item.innerHTML = `
        <div class="item-title">
          <iconify-icon icon="lucide:file-spreadsheet" style="color: var(--color-primary);"></iconify-icon>
          ${escapeHtml(f.filename)}
        </div>
        <div class="item-meta">
          <span>${formatBytes(f.file_size || 0)}</span>
          <span>•</span>
          <span>${escapeHtml(f.file_type || "Excel")}</span>
        </div>
      `;
      recentFilesList.appendChild(item);
    });

    // Auto-select newest if none active
    if (!activeFile && files.length > 0) {
      selectFileFromDatabase(files[0].id);
    }
  } catch (err) {
    console.warn("Could not load recent files from database:", err);
  }
}

async function selectFileFromDatabase(fileId) {
  try {
    const res = await fetch(`/api/excel/${fileId}/metadata`, { headers: getAuthHeaders() });
    if (!res.ok) throw new Error("Could not load metadata from database.");
    const meta = await res.json();
    setActiveFile(meta);
  } catch (err) {
    showNotification("Error loading file: " + err.message, "error");
  }
}

// ==========================================================================
// 4. CHAT & SPREADSHEET QUERY EXECUTION
// ==========================================================================

function startNewChat() {
  activeSessionId = null;
  chatStream.innerHTML = "";
  chatStream.appendChild(welcomeHero);
  welcomeHero.style.display = "block";
  chatTitleHeader.innerText = "Spreadsheet Intelligence";
  btnDownloadModified.style.display = "none";
}

async function sendQuestion() {
  const question = questionInput.value.trim();
  if (!question) return;

  questionInput.value = "";
  welcomeHero.style.display = "none";

  appendUserMessage(question);

  const fileId = activeFile ? (activeFile.file_id || activeFile.id) : null;
  const sheetName = sheetDropdown ? sheetDropdown.value : null;
  const enableWeb = document.getElementById("check-web-research").checked;
  const modifyExcel = document.getElementById("check-modify-excel").checked;

  const loadingBubble = appendLoadingBubble();

  try {
    const res = await fetch("/api/chat/ask", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        file_id: fileId,
        session_id: activeSessionId,
        sheet_name: sheetName,
        question: question,
        enable_web_research: enableWeb,
        modify_excel: modifyExcel
      })
    });
    const data = await res.json();
    loadingBubble.remove();

    if (!res.ok) throw new Error(data.detail || "Error analyzing query.");

    activeSessionId = data.session_id;
    appendAssistantMessage(data);
    loadChatSessions();

    if (data.modified_file_url) {
      btnDownloadModified.href = data.modified_file_url;
      btnDownloadModified.style.display = "inline-flex";
    }
  } catch (err) {
    loadingBubble.remove();
    appendAssistantMessage({
      role: "assistant",
      content: `⚠️ ${err.message}`
    });
  }
}

function appendUserMessage(text) {
  const row = document.createElement("div");
  row.className = "message-row user";
  row.innerHTML = `
    <div class="message-avatar">You</div>
    <div class="message-bubble">${escapeHtml(text)}</div>
  `;
  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
}

function appendLoadingBubble() {
  const row = document.createElement("div");
  row.className = "message-row assistant";
  row.innerHTML = `
    <div class="message-avatar"><iconify-icon icon="lucide:bot" width="20" height="20"></iconify-icon></div>
    <div class="message-bubble" style="color: var(--color-text-muted);">
      <iconify-icon icon="lucide:loader-2" class="spin" style="margin-right: 6px;"></iconify-icon>
      Analyzing spreadsheet in database & calculating response...
    </div>
  `;
  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
  return row;
}

function appendAssistantMessage(data) {
  const row = document.createElement("div");
  row.className = "message-row assistant";

  let innerContent = `<div>${escapeHtml(data.content)}</div>`;

  // Formula Card
  if (data.formula) {
    innerContent += `
      <div class="formula-card">
        <div class="formula-header">
          <span><iconify-icon icon="lucide:function-square"></iconify-icon> EXCEL FORMULA</span>
          <button class="copy-btn" onclick="copyToClipboard('${escapeHtml(data.formula)}')">
            <iconify-icon icon="lucide:copy"></iconify-icon> Copy
          </button>
        </div>
        <div class="formula-code">${escapeHtml(data.formula)}</div>
        ${data.formula_explanation ? `<div class="formula-explanation">${escapeHtml(data.formula_explanation)}</div>` : ''}
      </div>
    `;
  }

  // Analysis Result (Table or Metrics)
  if (data.analysis_result) {
    const res = data.analysis_result;
    if (res.summary && res.rows) {
      let tableRows = res.rows.map(r => {
        const keys = Object.keys(r).filter(k => k !== "formatted_value");
        return `<tr><td>${escapeHtml(r[keys[0]])}</td><td style="font-weight: 700; text-align: right;">${escapeHtml(r.formatted_value || r[keys[1]])}</td></tr>`;
      }).join("");

      innerContent += `
        <div class="analysis-table-wrapper">
          <table class="analysis-table">
            <thead>
              <tr><th>${escapeHtml(res.group_column || "Category")}</th><th style="text-align: right;">${escapeHtml(res.value_column || "Total")}</th></tr>
            </thead>
            <tbody>${tableRows}</tbody>
          </table>
        </div>
      `;
    } else if (res.total !== undefined || res.average !== undefined || res.value !== undefined) {
      innerContent += `
        <div class="analysis-metrics-grid">
          ${res.total !== undefined ? `<div class="metric-card"><div class="metric-label">Total Sum</div><div class="metric-value">$${formatNumber(res.total)}</div></div>` : ''}
          ${res.average !== undefined ? `<div class="metric-card"><div class="metric-label">Average</div><div class="metric-value">$${formatNumber(res.average)}</div></div>` : ''}
          ${res.min !== undefined ? `<div class="metric-card"><div class="metric-label">Minimum</div><div class="metric-value">$${formatNumber(res.min)}</div></div>` : ''}
          ${res.max !== undefined ? `<div class="metric-card"><div class="metric-label">Maximum</div><div class="metric-value">$${formatNumber(res.max)}</div></div>` : ''}
          ${res.entity !== undefined ? `<div class="metric-card"><div class="metric-label">Top Item</div><div class="metric-value">${escapeHtml(res.entity)} ($${formatNumber(res.value)})</div></div>` : ''}
        </div>
      `;
    }
  }

  // Chart Visualization Card
  if (data.chart_url) {
    innerContent += `
      <div class="chart-display-card">
        <img src="${data.chart_url}" alt="Generated Visualization">
        <div class="chart-card-footer">
          <span><iconify-icon icon="lucide:bar-chart-2"></iconify-icon> ${escapeHtml(data.chart_type || "Visualization")}</span>
          <a href="${data.chart_url}" target="_blank" class="btn-secondary" style="font-size: 11px; padding: 4px 10px; text-decoration: none;">
            <iconify-icon icon="lucide:maximize-2"></iconify-icon> View Full Resolution
          </a>
        </div>
      </div>
    `;
  }

  // Modified Excel Download Button
  if (data.modified_file_url) {
    innerContent += `
      <div style="margin-top: 10px;">
        <a href="${data.modified_file_url}" class="btn-primary" style="background: var(--color-success); text-decoration: none; display: inline-flex; font-size: 12px;">
          <iconify-icon icon="lucide:file-down"></iconify-icon> Download Enhanced Excel (.xlsx)
        </a>
      </div>
    `;
  }

  row.innerHTML = `
    <div class="message-avatar"><iconify-icon icon="lucide:bot" width="20" height="20"></iconify-icon></div>
    <div class="message-bubble">${innerContent}</div>
  `;
  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
}

// ==========================================================================
// 5. CHAT SESSIONS & PERSISTENCE
// ==========================================================================

async function loadChatSessions() {
  if (!token) return;
  try {
    const res = await fetch("/api/chat/sessions", { headers: getAuthHeaders() });
    if (!res.ok) return;
    const sessions = await res.json();
    chatHistoryList.innerHTML = "";

    if (sessions.length === 0) {
      chatHistoryList.innerHTML = `
        <div style="font-size: 12px; color: var(--color-text-dim); padding: 8px; text-align: center;">
          No conversations yet
        </div>
      `;
      return;
    }

    sessions.forEach(s => {
      const item = document.createElement("div");
      item.className = `history-item ${s.id === activeSessionId ? 'active' : ''}`;
      item.onclick = () => loadSession(s.id);
      item.innerHTML = `
        <div class="item-title">${escapeHtml(s.title)}</div>
        <div class="item-meta">
          <span><iconify-icon icon="lucide:message-circle"></iconify-icon> ${s.message_count} msgs</span>
          ${s.filename ? `<span>•</span><span>${escapeHtml(s.filename)}</span>` : ''}
        </div>
      `;
      chatHistoryList.appendChild(item);
    });
  } catch (err) {
    console.warn("Could not load sessions from database:", err);
  }
}

async function loadSession(sessionId) {
  try {
    const res = await fetch(`/api/chat/sessions/${sessionId}`, { headers: getAuthHeaders() });
    if (!res.ok) return;
    const session = await res.json();

    activeSessionId = session.id;
    welcomeHero.style.display = "none";
    chatStream.innerHTML = "";
    chatTitleHeader.innerText = session.title;

    session.messages.forEach(m => {
      if (m.role === "user") {
        appendUserMessage(m.content);
      } else {
        appendAssistantMessage(m);
      }
    });

    loadChatSessions();
  } catch (err) {
    showNotification("Could not load session: " + err.message, "error");
  }
}

// ==========================================================================
// 6. MODALS (SCHEMA INSPECTOR & SQL HISTORY)
// ==========================================================================

function openSchemaModal() {
  if (!activeFile) {
    showNotification("Please upload or select an Excel/CSV document first.", "info");
    return;
  }

  const currentSheet = sheetDropdown.value;
  const sheets = activeFile.sheets || {};
  const sheetMeta = sheets[currentSheet] || Object.values(sheets)[0];

  if (!sheetMeta) {
    showNotification("No column metadata available for this sheet.", "info");
    return;
  }

  const container = document.getElementById("schema-content-area");
  container.innerHTML = `
    <div style="margin-bottom: 16px; font-size: 13px; color: var(--color-text-muted); display: flex; gap: 16px; flex-wrap: wrap;">
      <div>Worksheet: <b style="color: #ffffff;">${escapeHtml(sheetMeta.sheet_name || currentSheet)}</b></div>
      <div>Total Rows: <b style="color: #ffffff;">${sheetMeta.row_count.toLocaleString()}</b></div>
      <div>Total Columns: <b style="color: #ffffff;">${sheetMeta.column_count}</b></div>
    </div>
    <div class="analysis-table-wrapper">
      <table class="analysis-table">
        <thead>
          <tr>
            <th>Col</th>
            <th>Header Name</th>
            <th>Data Type</th>
            <th>Non-Null</th>
            <th>Summary / Range</th>
            <th>Sample Values</th>
          </tr>
        </thead>
        <tbody>
          ${sheetMeta.columns.map(c => `
            <tr>
              <td><b style="color: var(--color-primary-hover);">${c.column_letter}</b></td>
              <td><b>${escapeHtml(c.name)}</b></td>
              <td><span class="file-type-pill" style="font-size: 10px;">${c.data_type}</span></td>
              <td>${c.non_null_count}</td>
              <td>${c.mean_val ? `Mean: ${c.mean_val}` : (c.min_val !== null ? `${c.min_val} ~ ${c.max_val}` : '-')}</td>
              <td style="color: var(--color-text-muted); font-size: 11px;">${escapeHtml(c.sample_values.slice(0, 3).join(", "))}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
  schemaModal.style.display = "flex";
}

function closeSchemaModal() {
  schemaModal.style.display = "none";
}

async function openHistoryModal() {
  historyModal.style.display = "flex";
  const container = document.getElementById("history-content-area");
  container.innerHTML = `<p style="color: var(--color-text-muted);">Loading SQL analysis records from database...</p>`;

  try {
    const res = await fetch("/api/history", { headers: getAuthHeaders() });
    const records = await res.json();

    if (!records || records.length === 0) {
      container.innerHTML = `<p style="color: var(--color-text-muted); text-align: center; padding: 20px;">No analysis history recorded in database yet.</p>`;
      return;
    }

    container.innerHTML = `
      <div class="analysis-table-wrapper">
        <table class="analysis-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Question Asked</th>
              <th>Operation</th>
              <th>Excel Formula</th>
              <th>Chart Image</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            ${records.map(r => `
              <tr>
                <td>#${r.id}</td>
                <td style="font-weight: 600;">${escapeHtml(r.question)}</td>
                <td><span class="file-type-pill" style="font-size: 10px;">${r.operation_type}</span></td>
                <td><code>${r.formula_generated ? escapeHtml(r.formula_generated) : '-'}</code></td>
                <td>${r.chart_path ? `<a href="${r.chart_path}" target="_blank" style="color: var(--color-primary-hover);">View Chart</a>` : '-'}</td>
                <td style="font-size: 11px; color: var(--color-text-dim);">${new Date(r.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<p style="color: var(--color-danger);">Error fetching database history: ${err.message}</p>`;
  }
}

function closeHistoryModal() {
  historyModal.style.display = "none";
}

// ==========================================================================
// 7. UTILITIES
// ==========================================================================

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showNotification("Excel formula copied to clipboard!", "success");
  });
}

function showNotification(msg, type = "info") {
  const notif = document.createElement("div");
  notif.style.position = "fixed";
  notif.style.bottom = "24px";
  notif.style.right = "24px";
  notif.style.padding = "10px 18px";
  notif.style.background = type === "success" ? "var(--color-success)" : (type === "error" ? "var(--color-danger)" : "var(--color-primary)");
  notif.style.color = "#ffffff";
  notif.style.borderRadius = "var(--radius-sm)";
  notif.style.fontSize = "13px";
  notif.style.fontWeight = "600";
  notif.style.boxShadow = "var(--shadow-lg)";
  notif.style.zIndex = "99999";
  notif.style.display = "flex";
  notif.style.alignItems = "center";
  notif.style.gap = "8px";
  
  const icon = type === "success" ? "lucide:check-circle" : (type === "error" ? "lucide:alert-circle" : "lucide:info");
  notif.innerHTML = `<iconify-icon icon="${icon}"></iconify-icon> <span>${escapeHtml(msg)}</span>`;
  
  document.body.appendChild(notif);
  setTimeout(() => notif.remove(), 3200);
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

function formatNumber(num) {
  if (num === null || num === undefined) return "0.00";
  return Number(num).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
