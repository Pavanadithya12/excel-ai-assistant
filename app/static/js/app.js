// ==========================================================================
// AI EXCEL ASSISTANT - DYNAMIC APPLICATION CONTROLLER (V4.0)
// 100% Database-Driven • Direct Auth • Right-Side Rail • Document Deletion
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
const fileTypeDisplay = document.getElementById("file-type-display");
const fileNameDisplay = document.getElementById("file-name-display");
const fileSizeDisplay = document.getElementById("file-size-display");
const fileStatRows = document.getElementById("file-stat-rows");
const fileStatCols = document.getElementById("file-stat-cols");
const sheetDropdown = document.getElementById("sheet-dropdown");
const btnInspectSchema = document.getElementById("btn-inspect-schema");
const btnDownloadOriginal = document.getElementById("btn-download-original");
const btnDownloadModified = document.getElementById("btn-download-modified");
const btnDeleteActiveFile = document.getElementById("btn-delete-active-file");
const recentFilesList = document.getElementById("recent-files-list");
const docCountBadge = document.getElementById("doc-count-badge");

// Right Panel (Suggestions & Insights Rail)
const rightPanel = document.getElementById("right-panel");
const btnToggleSuggestions = document.getElementById("btn-toggle-suggestions");
const rightPanelSuggestions = document.getElementById("right-panel-suggestions");
const rightPanelDocMeta = document.getElementById("right-panel-doc-meta");
const rightPanelColumns = document.getElementById("right-panel-columns");
const rpActiveDocTag = document.getElementById("rp-active-doc-tag");
const rpDocType = document.getElementById("rp-doc-type");
const rpDocDomain = document.getElementById("rp-doc-domain");
const rpDocDims = document.getElementById("rp-doc-dims");
const rpDocSize = document.getElementById("rp-doc-size");
const rpColumnsList = document.getElementById("rp-columns-list");

// Chat Elements
const chatStream = document.getElementById("chat-stream");
const welcomeHero = document.getElementById("welcome-hero");
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

  if (btnDeleteActiveFile) {
    btnDeleteActiveFile.addEventListener("click", () => {
      if (activeFile) {
        deleteDocumentById(activeFile.file_id || activeFile.id, activeFile.filename);
      }
    });
  }

  if (btnToggleSuggestions) {
    btnToggleSuggestions.addEventListener("click", () => {
      rightPanel.classList.toggle("collapsed");
    });
  }

  // Enter sends question (Shift+Enter inserts newline)
  questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  });

  // Drag and drop upload zone
  const dropzone = document.getElementById("upload-dropzone");
  if (dropzone) {
    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "var(--color-cyan)";
    });
    dropzone.addEventListener("dragleave", () => {
      dropzone.style.borderColor = "#2d426b";
    });
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "#2d426b";
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

function autoFillOTP() {
  const devEl = document.getElementById("dev-otp-value");
  if (devEl && devEl.innerText) {
    const input = document.getElementById("input-otp");
    if (input) {
      input.value = devEl.innerText.trim();
      input.focus();
      showNotification("OTP code auto-filled! Click 'Verify & Sign In'.", "success");
    }
  }
}

function showOTPView(email, devOtp = null, deliveredToInbox = false) {
  currentPendingEmail = email;
  document.getElementById("view-signin").style.display = "none";
  document.getElementById("view-signup").style.display = "none";
  document.getElementById("view-otp").style.display = "block";
  document.getElementById("otp-target-email").innerText = email;

  const descEl = document.getElementById("otp-view-desc");
  if (descEl) {
    if (deliveredToInbox) {
      descEl.innerHTML = `We've sent a real verification code to <b style="color: var(--color-primary);">${email}</b>.<br>Please check your inbox (and Spam folder), copy the 6-digit code, and enter it below:`;
    } else {
      descEl.innerHTML = `Verification code generated for <b style="color: var(--color-primary);">${email}</b>.<br>Enter the 6-digit code below to authenticate:`;
    }
  }

  // Clear input so user types/pastes the real OTP
  const inputOtp = document.getElementById("input-otp");
  if (inputOtp) {
    inputOtp.value = "";
    inputOtp.focus();
  }
  const devHint = document.getElementById("otp-dev-hint");
  const devVal = document.getElementById("dev-otp-value");
  if (devHint && devVal) {
    if (devOtp) {
      devVal.innerText = devOtp;
      devHint.style.display = "flex";
    } else {
      devHint.style.display = "none";
    }
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
    showNotification("Verifying credentials & sending OTP code...", "info");
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (!res.ok) {
      if (res.status === 403) {
        showNotification("Account requires verification. Check your email.", "info");
        showOTPView(email, data.dev_otp, data.delivered_to_inbox);
        return;
      }
      throw new Error(data.detail || "Sign in failed.");
    }

    if (data.requires_otp) {
      showNotification(data.message || `OTP sent to ${email}.`, "success");
      showOTPView(email, data.dev_otp, data.delivered_to_inbox);
      return;
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
    showNotification("Creating account & generating verification OTP...", "info");
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name: name, email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Registration failed.");

    showNotification(data.message || "OTP code ready!", "success");
    showOTPView(email, data.dev_otp, data.delivered_to_inbox);
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
    showNotification("Account successfully activated! Welcome to Excel AI Studio.", "success");
  } catch (err) {
    showNotification(err.message, "error");
  }
}

async function handleResendOTP() {
  if (!currentPendingEmail) return;
  try {
    showNotification("Generating fresh verification code...", "info");
    const res = await fetch("/api/auth/resend-otp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: currentPendingEmail })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to resend code.");
    showNotification(data.message || "A fresh verification code was generated.", "success");
    showOTPView(currentPendingEmail, data.dev_otp, data.delivered_to_inbox);
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

    const meta = data.metadata || data;
    setActiveFile(meta);
    renderUploadConfirmation(meta);
    showNotification(data.message || `Uploaded ${data.filename}`, "success");
  } catch (err) {
    showNotification("Upload failed: " + err.message, "error");
  }
}

function setActiveFile(fileMeta) {
  activeFile = fileMeta;
  activeFileCard.style.display = "flex";

  // Hide the big welcome dropzone so no unwanted clutter is in chat
  welcomeHero.style.display = "none";

  const fileTypeLabel = fileMeta.file_type || "Microsoft Excel (.xlsx)";
  
  // Document Name
  fileNameDisplay.innerText = fileMeta.filename;
  fileSizeDisplay.innerText = formatBytes(fileMeta.file_size || 0);

  // Document Type Shown DIRECTLY Below Document Name
  fileTypeDisplay.innerHTML = `<iconify-icon icon="material-symbols-light:badge-outline" width="14" height="14"></iconify-icon> ${escapeHtml(fileTypeLabel)}`;

  // Stats
  const rows = fileMeta.total_rows || 0;
  const cols = fileMeta.total_columns || 0;
  fileStatRows.innerHTML = `<iconify-icon icon="material-symbols-light:table-rows-outline" width="14" height="14"></iconify-icon> ${rows.toLocaleString()} rows`;
  fileStatCols.innerHTML = `<iconify-icon icon="material-symbols-light:view-column-outline" width="14" height="14"></iconify-icon> ${cols.toLocaleString()} cols`;

  // Worksheets Selector
  sheetDropdown.innerHTML = "";
  const sheets = fileMeta.sheet_names || [];
  sheets.forEach((sheet) => {
    const opt = document.createElement("option");
    opt.value = sheet;
    opt.innerText = `Sheet: ${sheet}`;
    sheetDropdown.appendChild(opt);
  });

  const fileId = fileMeta.file_id || fileMeta.id;
  btnDownloadOriginal.href = `/api/excel/${fileId}/download`;
  activeSheetPill.innerHTML = `<iconify-icon icon="material-symbols-light:check-circle-outline" style="color: var(--color-success);"></iconify-icon> ${escapeHtml(fileMeta.filename)}`;

  // Populate Right-Side Rail (Suggestions & Document Overview)
  updateRightPanel(fileMeta);

  // Refresh recent documents from database
  loadRecentFiles();
}

// Update the Right-Side Rail with Dynamic Questions and Metadata
function updateRightPanel(meta) {
  rpActiveDocTag.innerText = meta.filename ? (meta.filename.length > 16 ? meta.filename.substring(0, 14) + '...' : meta.filename) : 'Active';

  // 1. Dynamic Questions on Right Side (Filter out duplicates from pinned section)
  let rawSuggestions = meta.dynamic_suggestions || [];
  let suggestions = rawSuggestions.filter(q => {
    const l = q.toLowerCase();
    return !l.includes("preview of the first") &&
           !l.includes("how many rows and columns") &&
           !l.includes("what data types are in each column") &&
           !l.includes("summarize key column distributions");
  });
  
  // Robust fallback if suggestions list is empty
  if (suggestions.length === 0) {
    const sheets = meta.sheets || {};
    const currentSheet = sheetDropdown?.value;
    const sheetMeta = sheets[currentSheet] || Object.values(sheets)[0];
    const cols = sheetMeta?.columns?.filter(c => !strStartsWith(c.name, "Unnamed:") && !strStartsWith(c.name, "Col_")) || [];
    const numCols = cols.filter(c => c.data_type === "numeric");
    const textCols = cols.filter(c => c.data_type === "text");

    if (numCols.length > 0) {
      suggestions.push(`What is the average ${numCols[0].name}?`);
      suggestions.push(`What is the total ${numCols[0].name}?`);
    }
    if (numCols.length > 0 && textCols.length > 0) {
      suggestions.push(`Create a bar chart comparing ${numCols[0].name} by ${textCols[0].name}.`);
      suggestions.push(`Which ${textCols[0].name} has the highest ${numCols[0].name}?`);
    } else if (textCols.length > 0) {
      suggestions.push(`Show unique values in the ${textCols[0].name} column.`);
      if (textCols.length > 1) {
        suggestions.push(`How many unique ${textCols[1].name} entries are there?`);
      }
    }
    if (cols.length >= 2) {
      suggestions.push(`List top entries sorted by ${cols[0].name}.`);
    }
  }

  rightPanelSuggestions.innerHTML = "";

  if (suggestions.length === 0) {
    rightPanelSuggestions.innerHTML = `
      <div class="empty-suggestions-hint">
        <iconify-icon icon="material-symbols-light:auto-awesome-outline" width="28" height="28" style="color: var(--color-primary);"></iconify-icon>
        <p>No suggestions available for this document.</p>
      </div>
    `;
  } else {
    suggestions.forEach(q => {
      const card = document.createElement("div");
      card.className = "suggested-question-card";
      card.innerHTML = `
        <iconify-icon icon="material-symbols-light:auto-awesome-outline" width="16" height="16" style="color: var(--color-primary);"></iconify-icon>
        <span>${escapeHtml(q)}</span>
      `;
      card.onclick = () => askDynamicQuestion(q);
      rightPanelSuggestions.appendChild(card);
    });
  }

  // 2. Document Overview Metadata
  rightPanelDocMeta.style.display = "block";
  rpDocType.innerText = meta.file_type || "Excel / CSV";
  rpDocDomain.innerText = meta.inferred_domain || "Tabular Dataset";
  rpDocDims.innerText = `${(meta.total_rows || 0).toLocaleString()} rows × ${(meta.total_columns || 0)} cols`;
  rpDocSize.innerText = formatBytes(meta.file_size || 0);

  // 3. Columns Explorer
  const sheets = meta.sheets || {};
  const currentSheet = sheetDropdown.value;
  const sheetMeta = sheets[currentSheet] || Object.values(sheets)[0];

  if (sheetMeta && sheetMeta.columns) {
    rightPanelColumns.style.display = "block";
    rpColumnsList.innerHTML = "";
    sheetMeta.columns.forEach(col => {
      if (strStartsWith(col.name, "Unnamed:") || strStartsWith(col.name, "Col_")) return;
      const pill = document.createElement("span");
      const typeClass = col.data_type === "numeric" ? "type-numeric" : (col.data_type === "datetime" ? "type-datetime" : "type-text");
      pill.className = `col-pill-badge ${typeClass}`;
      pill.innerHTML = `<iconify-icon icon="material-symbols-light:label-outline" width="12" height="12"></iconify-icon> ${escapeHtml(col.name)} <small style="opacity: 0.7;">(${col.data_type})</small>`;
      rpColumnsList.appendChild(pill);
    });
  } else {
    rightPanelColumns.style.display = "none";
  }

  // Ensure right panel is visible
  rightPanel.classList.remove("collapsed");
}

function strStartsWith(str, prefix) {
  return str && String(str).startsWith(prefix);
}

function renderUploadConfirmation(meta) {
  welcomeHero.style.display = "none";

  const row = document.createElement("div");
  row.className = "message-row assistant";

  row.innerHTML = `
    <div class="message-avatar"><iconify-icon icon="material-symbols-light:smart-toy-outline" width="20" height="20"></iconify-icon></div>
    <div class="message-bubble">
      <div style="font-weight: 700; color: #ffffff; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
        <iconify-icon icon="material-symbols-light:check-circle-outline" style="color: var(--color-success);"></iconify-icon>
        <span>Spreadsheet Connected to Database</span>
      </div>
      <p style="color: var(--color-text-muted); font-size: 13px; margin-bottom: 10px;">
        Uploaded <b>${escapeHtml(meta.filename)}</b>. AI suggested analysis prompts are ready in the right-side rail.
      </p>

      <div class="upload-confirm-card">
        <div class="confirm-header">
          <div class="confirm-title">
            <iconify-icon icon="material-symbols-light:table-view-outline" style="color: var(--color-primary);"></iconify-icon>
            <span>${escapeHtml(meta.filename)}</span>
          </div>
          <span class="doc-type-badge-below">${escapeHtml(meta.file_type || "Excel / CSV")}</span>
        </div>

        <div class="confirm-details-grid">
          <div class="confirm-detail-item">
            <span class="label">Document Type</span>
            <span class="value">${escapeHtml(meta.file_type || "Excel / CSV")}</span>
          </div>
          <div class="confirm-detail-item">
            <span class="label">Domain Category</span>
            <span class="value">${escapeHtml(meta.inferred_domain || "Tabular Dataset")}</span>
          </div>
          <div class="confirm-detail-item">
            <span class="label">Worksheets</span>
            <span class="value">${(meta.sheet_names || []).length} sheet(s)</span>
          </div>
          <div class="confirm-detail-item">
            <span class="label">Dimension</span>
            <span class="value">${(meta.total_rows || 0).toLocaleString()} rows × ${(meta.total_columns || 0)} cols</span>
          </div>
        </div>
      </div>
    </div>
  `;

  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
}

function askDynamicQuestion(q) {
  questionInput.value = q;
  sendQuestion();
}

// ==========================================================================
// 3. DATABASE PERSISTED FILES & DELETION CONTROLLER
// ==========================================================================

async function loadRecentFiles() {
  if (!token) return;
  try {
    const res = await fetch("/api/excel/files", { headers: getAuthHeaders() });
    if (!res.ok) return;
    const files = await res.json();

    recentFilesList.innerHTML = "";
    if (docCountBadge) docCountBadge.innerText = files.length;

    if (files.length === 0) {
      recentFilesList.innerHTML = `
        <div style="font-size: 12px; color: var(--color-text-dim); padding: 12px; text-align: center;">
          No stored documents yet
        </div>
      `;
      return;
    }

    files.forEach(f => {
      const item = document.createElement("div");
      const isActive = activeFile && (activeFile.file_id === f.id || activeFile.id === f.id);
      item.className = `recent-file-item ${isActive ? 'active' : ''}`;
      item.onclick = () => selectFileFromDatabase(f.id);

      item.innerHTML = `
        <div class="item-info-col">
          <div class="item-title" title="${escapeHtml(f.filename)}">
            <iconify-icon icon="material-symbols-light:table-view-outline" style="color: var(--color-primary); margin-right: 4px;"></iconify-icon>
            ${escapeHtml(f.filename)}
          </div>
          <div class="item-meta">
            <span>${formatBytes(f.file_size || 0)}</span>
            <span>•</span>
            <span>${escapeHtml(f.file_type ? f.file_type.split(" ")[0] : "Excel")}</span>
          </div>
        </div>
        <button class="btn-item-delete" onclick="event.stopPropagation(); deleteDocumentById(${f.id}, '${escapeHtml(f.filename)}')" title="Delete Document">
          <iconify-icon icon="material-symbols-light:delete-outline" width="14" height="14"></iconify-icon>
        </button>
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

// Delete Document from Database & Disk Anytime
async function deleteDocumentById(fileId, filename) {
  if (!confirm(`Are you sure you want to delete "${filename}" from the database?`)) {
    return;
  }

  try {
    const res = await fetch(`/api/excel/${fileId}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to delete document.");

    showNotification(`Deleted "${filename}" successfully.`, "success");

    // If currently active file was deleted, reset state
    if (activeFile && (activeFile.file_id === fileId || activeFile.id === fileId)) {
      activeFile = null;
      activeFileCard.style.display = "none";
      activeSheetPill.innerHTML = `<iconify-icon icon="material-symbols-light:info-outline"></iconify-icon> Ready for upload`;
      welcomeHero.style.display = "block";
      rightPanelDocMeta.style.display = "none";
      rightPanelColumns.style.display = "none";
      rpActiveDocTag.innerText = "No Doc";
      rightPanelSuggestions.innerHTML = `
        <div class="empty-suggestions-hint">
          <iconify-icon icon="material-symbols-light:help-outline" width="28" height="28"></iconify-icon>
          <p>Upload a spreadsheet to automatically generate AI analysis prompts.</p>
        </div>
      `;
    }

    loadRecentFiles();
  } catch (err) {
    showNotification("Error deleting document: " + err.message, "error");
  }
}

// ==========================================================================
// 4. CHAT SESSIONS & DELETION CONTROLLER
// ==========================================================================

function startNewChat() {
  activeSessionId = null;
  chatStream.innerHTML = "";
  chatTitleHeader.innerText = "Spreadsheet Intelligence";
  btnDownloadModified.style.display = "none";

  if (!activeFile) {
    chatStream.appendChild(welcomeHero);
    welcomeHero.style.display = "block";
  } else {
    welcomeHero.style.display = "none";
  }
}

async function sendQuestion() {
  const question = questionInput.value.trim();
  if (!question) return;

  questionInput.value = "";
  welcomeHero.style.display = "none";

  appendUserMessage(question);

  const fileId = activeFile ? (activeFile.file_id || activeFile.id) : null;
  const sheetName = sheetDropdown ? sheetDropdown.value : null;
  const enableWeb = document.getElementById("check-web-research")?.checked || false;
  const modifyExcel = document.getElementById("check-modify-excel")?.checked || false;

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
    <div class="message-avatar"><iconify-icon icon="material-symbols-light:smart-toy-outline" width="20" height="20"></iconify-icon></div>
    <div class="message-bubble" style="color: var(--color-text-muted);">
      <iconify-icon icon="material-symbols-light:progress-activity" class="spin" style="margin-right: 6px;"></iconify-icon>
      Executing spreadsheet query & generating visualization...
    </div>
  `;
  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
  return row;
}

function appendAssistantMessage(data) {
  const row = document.createElement("div");
  row.className = "message-row assistant";

  // Render markdown-like formatting: **bold**, newlines → <br>
  function renderText(text) {
    if (!text) return "";
    return escapeHtml(text)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  }

  let innerContent = `<div class="message-text">${renderText(data.content)}</div>`;

  // Formula Card
  if (data.formula) {
    innerContent += `
      <div class="formula-card">
        <div class="formula-header">
          <span><iconify-icon icon="material-symbols-light:functions"></iconify-icon> EXCEL FORMULA</span>
          <button class="copy-btn" onclick="copyToClipboard('${escapeHtml(data.formula)}')">
            <iconify-icon icon="material-symbols-light:content-copy-outline"></iconify-icon> Copy
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
    
    // Direct Data Table (Preview, Unique Values, Schema Types, etc.)
    if (res.is_table && res.rows && res.rows.length > 0) {
      const cols = res.columns || Object.keys(res.rows[0]);
      let headerHtml = cols.map(c => `<th>${escapeHtml(c)}</th>`).join("");
      let tableRows = res.rows.map(r => {
        let cells = cols.map(c => `<td>${escapeHtml(r[c] !== null && r[c] !== undefined ? r[c] : "")}</td>`).join("");
        return `<tr>${cells}</tr>`;
      }).join("");

      innerContent += `
        <div class="analysis-table-wrapper" style="margin-top: 10px;">
          <table class="analysis-table">
            <thead>
              <tr>${headerHtml}</tr>
            </thead>
            <tbody>${tableRows}</tbody>
          </table>
        </div>
      `;
    } else if (res.summary && res.rows) {
      let tableRows = res.rows.map(r => {
        const keys = Object.keys(r).filter(k => k !== "formatted_value");
        return `<tr><td>${escapeHtml(r[keys[0]])}</td><td style="font-weight: 700; text-align: right;">${escapeHtml(r.formatted_value || r[keys[1]])}</td></tr>`;
      }).join("");

      innerContent += `
        <div class="analysis-table-wrapper" style="margin-top: 10px;">
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
          <span><iconify-icon icon="material-symbols-light:bar-chart-outline"></iconify-icon> ${escapeHtml(data.chart_type || "Visualization")}</span>
          <a href="${data.chart_url}" target="_blank" class="btn-secondary" style="font-size: 11px; padding: 4px 10px; text-decoration: none;">
            <iconify-icon icon="material-symbols-light:open-in-full"></iconify-icon> View Full Resolution
          </a>
        </div>
      </div>
    `;
  }

  // Modified Excel Download Link
  if (data.modified_file_url) {
    innerContent += `
      <div style="margin-top: 10px;">
        <a href="${data.modified_file_url}" class="btn-primary" style="background: var(--color-success); text-decoration: none; display: inline-flex; font-size: 12px;">
          <iconify-icon icon="material-symbols-light:download"></iconify-icon> Download Enhanced Excel (.xlsx)
        </a>
      </div>
    `;
  }

  row.innerHTML = `
    <div class="message-avatar"><iconify-icon icon="material-symbols-light:smart-toy-outline" width="20" height="20"></iconify-icon></div>
    <div class="message-bubble">${innerContent}</div>
  `;
  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
}

// Load Chat Sessions from Database
async function loadChatSessions() {
  if (!token) return;
  try {
    const res = await fetch("/api/chat/sessions", { headers: getAuthHeaders() });
    if (!res.ok) return;
    const sessions = await res.json();
    chatHistoryList.innerHTML = "";

    if (sessions.length === 0) {
      chatHistoryList.innerHTML = `
        <div style="font-size: 12px; color: var(--color-text-dim); padding: 12px; text-align: center;">
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
        <div class="item-info-col">
          <div class="item-title">${escapeHtml(s.title)}</div>
          <div class="item-meta">
            <span><iconify-icon icon="material-symbols-light:chat-bubble-outline"></iconify-icon> ${s.message_count} msgs</span>
            ${s.filename ? `<span>•</span><span>${escapeHtml(s.filename)}</span>` : ''}
          </div>
        </div>
        <button class="btn-item-delete" onclick="event.stopPropagation(); deleteSessionById(${s.id})" title="Delete Conversation">
          <iconify-icon icon="material-symbols-light:delete-outline" width="14" height="14"></iconify-icon>
        </button>
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

// Delete Chat Session from Database
async function deleteSessionById(sessionId) {
  if (!confirm("Are you sure you want to delete this conversation?")) return;

  try {
    const res = await fetch(`/api/chat/sessions/${sessionId}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error("Failed to delete session.");

    showNotification("Conversation deleted.", "success");
    if (activeSessionId === sessionId) {
      startNewChat();
    }
    loadChatSessions();
  } catch (err) {
    showNotification("Error: " + err.message, "error");
  }
}

// ==========================================================================
// 5. MODALS (SCHEMA INSPECTOR & HISTORY DELETION)
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
              <td><b style="color: var(--color-cyan);">${c.column_letter}</b></td>
              <td><b>${escapeHtml(c.name)}</b></td>
              <td><span class="doc-type-badge-below" style="font-size: 10px; margin-top: 0;">${c.data_type}</span></td>
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
  await reloadHistoryModalContent();
}

async function reloadHistoryModalContent() {
  const container = document.getElementById("history-content-area");
  container.innerHTML = `<p style="color: var(--color-text-muted);">Loading SQL analysis records from database...</p>`;

  try {
    const res = await fetch("/api/history", { headers: getAuthHeaders() });
    const records = await res.json();

    if (!records || records.length === 0) {
      container.innerHTML = `<p style="color: var(--color-text-muted); text-align: center; padding: 24px;">No analysis history recorded in database yet.</p>`;
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
              <th>Formula</th>
              <th>Chart</th>
              <th>Time</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${records.map(r => `
              <tr>
                <td>#${r.id}</td>
                <td style="font-weight: 600;">${escapeHtml(r.question)}</td>
                <td><span class="doc-type-badge-below" style="font-size: 10px; margin-top: 0;">${r.operation_type}</span></td>
                <td><code>${r.formula_generated ? escapeHtml(r.formula_generated) : '-'}</code></td>
                <td>${r.chart_path ? `<a href="${r.chart_path}" target="_blank" style="color: var(--color-cyan);">View</a>` : '-'}</td>
                <td style="font-size: 11px; color: var(--color-text-dim);">${new Date(r.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                <td>
                  <button class="btn-row-delete" onclick="deleteHistoryItem(${r.id})" title="Delete Record">
                    <iconify-icon icon="material-symbols-light:delete-outline"></iconify-icon>
                  </button>
                </td>
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

// Clear All Analysis History from Database
async function clearAllAnalysisHistory() {
  if (!confirm("Are you sure you want to clear all analysis history records?")) return;

  try {
    const res = await fetch("/api/history", {
      method: "DELETE",
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to clear history.");

    showNotification(data.message || "History cleared.", "success");
    reloadHistoryModalContent();
  } catch (err) {
    showNotification("Error: " + err.message, "error");
  }
}

// Delete Single Analysis Record
async function deleteHistoryItem(historyId) {
  try {
    const res = await fetch(`/api/history/${historyId}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error("Failed to delete record.");

    showNotification("Record deleted.", "success");
    reloadHistoryModalContent();
  } catch (err) {
    showNotification("Error: " + err.message, "error");
  }
}

function closeHistoryModal() {
  historyModal.style.display = "none";
}

// ==========================================================================
// 6. UTILITIES
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
  
  const icon = type === "success" ? "material-symbols-light:check-circle-outline" : (type === "error" ? "material-symbols-light:error-outline" : "material-symbols-light:info-outline");
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
