// State
let token = localStorage.getItem("token") || null;
let currentUser = null;
let activeFile = null;
let activeSessionId = null;
let currentPendingEmail = null;

// DOM Elements
const authModal = document.getElementById("auth-modal");
const schemaModal = document.getElementById("schema-modal");
const historyModal = document.getElementById("history-modal");
const fileInput = document.getElementById("file-input");
const btnUpload = document.getElementById("btn-upload-file");
const btnLoadSample = document.getElementById("btn-load-sample");
const activeFileCard = document.getElementById("active-file-card");
const fileNameDisplay = document.getElementById("file-name-display");
const fileSizeDisplay = document.getElementById("file-size-display");
const sheetDropdown = document.getElementById("sheet-dropdown");
const btnInspectSchema = document.getElementById("btn-inspect-schema");
const btnDownloadOriginal = document.getElementById("btn-download-original");
const btnDownloadModified = document.getElementById("btn-download-modified");
const chatStream = document.getElementById("chat-stream");
const welcomeHero = document.getElementById("welcome-hero");
const questionInput = document.getElementById("question-input");
const btnSubmitQuestion = document.getElementById("btn-submit-question");
const btnNewChat = document.getElementById("btn-new-chat");
const chatHistoryList = document.getElementById("chat-history-list");
const userBadge = document.getElementById("user-badge");
const userName = document.getElementById("user-name");
const userStatusText = document.getElementById("user-status-text");
const userAvatar = document.getElementById("user-avatar");
const btnLogout = document.getElementById("btn-logout");
const btnHistoryView = document.getElementById("btn-history-view");

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  if (token) {
    loadUserProfile();
  }
  loadChatSessions();
  loadRecentFiles();
});

function setupEventListeners() {
  btnUpload.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", handleFileUpload);
  btnLoadSample.addEventListener("click", handleLoadSample);
  const btnStartAll = document.getElementById("btn-start-all-demo");
  if (btnStartAll) btnStartAll.addEventListener("click", runStartAllDemo);
  btnSubmitQuestion.addEventListener("click", sendQuestion);
  btnNewChat.addEventListener("click", startNewChat);
  btnInspectSchema.addEventListener("click", openSchemaModal);
  btnHistoryView.addEventListener("click", openHistoryModal);
  btnLogout.addEventListener("click", logout);

  // Enter to send (Shift+Enter for newline)
  questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  });

  // Auth form submissions
  document.getElementById("btn-submit-signin").addEventListener("click", handleSignIn);
  document.getElementById("btn-submit-signup").addEventListener("click", handleSignUp);
  document.getElementById("btn-submit-otp").addEventListener("click", handleVerifyOTP);
}

// Headers Helper
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

// ----------------- AUTHENTICATION FLOW -----------------

function openAuthModal() {
  if (currentUser) return;
  authModal.style.display = "flex";
  showSignInView();
}

function closeAuthModal() {
  authModal.style.display = "none";
}

function showSignInView() {
  document.getElementById("auth-signin-view").style.display = "block";
  document.getElementById("auth-signup-view").style.display = "none";
  document.getElementById("auth-otp-view").style.display = "none";
  document.getElementById("auth-modal-title").innerText = "Sign In";
}

function showSignUpView() {
  document.getElementById("auth-signin-view").style.display = "none";
  document.getElementById("auth-signup-view").style.display = "block";
  document.getElementById("auth-otp-view").style.display = "none";
  document.getElementById("auth-modal-title").innerText = "Create an Account";
}

function showOTPView(email, devOtp) {
  currentPendingEmail = email;
  document.getElementById("auth-signin-view").style.display = "none";
  document.getElementById("auth-signup-view").style.display = "none";
  document.getElementById("auth-otp-view").style.display = "block";
  document.getElementById("auth-modal-title").innerText = "Verify Email OTP";
  document.getElementById("otp-target-email").innerText = email;

  if (devOtp) {
    document.getElementById("otp-dev-hint").style.display = "block";
    document.getElementById("dev-otp-value").innerText = devOtp;
    document.getElementById("input-otp").value = devOtp; // auto-fill for convenience
  }
}

async function handleSignUp() {
  const name = document.getElementById("signup-name").value.trim();
  const email = document.getElementById("signup-email").value.trim();
  const password = document.getElementById("signup-password").value;

  if (!email || !password || !name) {
    alert("Please fill in all registration fields.");
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
    showOTPView(email, data.dev_otp);
  } catch (err) {
    alert(err.message);
  }
}

async function handleVerifyOTP() {
  const otp = document.getElementById("input-otp").value.trim();
  if (!otp || !currentPendingEmail) {
    alert("Please enter the 6-digit OTP code.");
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
    updateUserUI();
    closeAuthModal();
    alert("Account successfully activated! Welcome to AI Excel Assistant.");
    loadUserProfile();
  } catch (err) {
    alert(err.message);
  }
}

async function handleSignIn() {
  const email = document.getElementById("signin-email").value.trim();
  const password = document.getElementById("signin-password").value;

  if (!email || !password) {
    alert("Please enter email and password.");
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
        // Unverified email, show OTP screen
        const devOtp = res.headers.get("X-Dev-OTP");
        showOTPView(email, devOtp);
        return;
      }
      throw new Error(data.detail || "Sign in failed.");
    }

    token = data.access_token;
    localStorage.setItem("token", token);
    currentUser = data.user;
    updateUserUI();
    closeAuthModal();
    loadUserProfile();
  } catch (err) {
    alert(err.message);
  }
}

async function loadUserProfile() {
  if (!token) return;
  try {
    const res = await fetch("/api/auth/me", { headers: getAuthHeaders() });
    if (!res.ok) {
      logout();
      return;
    }
    currentUser = await res.json();
    updateUserUI();
  } catch {
    logout();
  }
}

function updateUserUI() {
  if (currentUser) {
    userName.innerText = currentUser.full_name || currentUser.email;
    userStatusText.innerText = "Verified Account";
    userAvatar.innerText = (currentUser.full_name || currentUser.email)[0].toUpperCase();
    btnLogout.style.display = "block";
  } else {
    userName.innerText = "Guest User";
    userStatusText.innerText = "Click to Sign In";
    userAvatar.innerText = "?";
    btnLogout.style.display = "none";
  }
}

function logout() {
  token = null;
  currentUser = null;
  localStorage.removeItem("token");
  updateUserUI();
}

// ----------------- SPREADSHEET HANDLING -----------------

async function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    showNotification("Uploading and analyzing spreadsheet...", "info");
    const res = await fetch("/api/excel/upload", {
      method: "POST",
      headers: getAuthHeaders(true),
      body: formData
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed.");

    setActiveFile(data);
    showNotification(data.message, "success");
    fileInput.value = "";
  } catch (err) {
    alert("Upload failed: " + err.message);
  }
}

async function handleLoadSample() {
  try {
    showNotification("Loading sample sales dataset...", "info");
    const res = await fetch("/api/excel/load-sample", {
      method: "POST",
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to load sample dataset.");

    setActiveFile(data);
    showNotification("Sample sales workbook loaded! Ask questions below.", "success");
    return data;
  } catch (err) {
    showNotification("Error: " + err.message, "info");
    return null;
  }
}

async function runStartAllDemo() {
  showNotification("🚀 Starting full AI Excel Assistant demo walkthrough...", "info");

  // Step 1: Ensure active file is loaded
  if (!activeFile) {
    const loaded = await handleLoadSample();
    if (!loaded) return;
    await new Promise(r => setTimeout(r, 800));
  }

  // Demo Questions to run in sequence
  const demoQuestions = [
    "What is the total sales amount?",
    "Calculate the average sales for each region.",
    "Give me an Excel formula to calculate profit margin.",
    "Create a bar chart comparing sales by region."
  ];

  for (let i = 0; i < demoQuestions.length; i++) {
    const q = demoQuestions[i];
    questionInput.value = q;
    await sendQuestion();
    await new Promise(r => setTimeout(r, 1200));
  }

  showNotification("🎉 All operations completed! View the formulas, summaries, and chart above.", "success");
}

function setActiveFile(fileData) {
  activeFile = fileData;
  activeFileCard.style.display = "flex";
  fileNameDisplay.innerText = fileData.filename;
  fileSizeDisplay.innerText = formatBytes(fileData.file_size || 0);

  // Populate sheet dropdown
  sheetDropdown.innerHTML = "";
  const sheets = fileData.sheet_names || [];
  sheets.forEach((sheet) => {
    const opt = document.createElement("option");
    opt.value = sheet;
    opt.innerText = `Sheet: ${sheet}`;
    sheetDropdown.appendChild(opt);
  });

  btnDownloadOriginal.href = `/api/excel/${fileData.file_id}/download`;
  document.getElementById("active-sheet-pill").innerHTML = `<i class="fa-solid fa-file-excel"></i> ${fileData.filename}`;

  loadRecentFiles();
}

async function loadRecentFiles() {
  try {
    const res = await fetch("/api/excel/files", { headers: getAuthHeaders() });
    if (res.ok) {
      const files = await res.json();
      if (files.length > 0 && !activeFile) {
        // Automatically set most recent file as active
        const metaRes = await fetch(`/api/excel/${files[0].id}/metadata`);
        if (metaRes.ok) {
          const meta = await metaRes.json();
          setActiveFile(meta);
        }
      }
    }
  } catch (e) {
    console.warn("Could not load recent files:", e);
  }
}

// ----------------- CHAT & QUESTION ANSWERING -----------------

function startNewChat() {
  activeSessionId = null;
  chatStream.innerHTML = "";
  chatStream.appendChild(welcomeHero);
  welcomeHero.style.display = "block";
  document.getElementById("chat-title-header").innerText = "AI Excel Assistant";
  btnDownloadModified.style.display = "none";
}

function askSampleQuestion(q) {
  questionInput.value = q;
  sendQuestion();
}

async function sendQuestion() {
  const question = questionInput.value.trim();
  if (!question) return;

  questionInput.value = "";
  welcomeHero.style.display = "none";

  // Append user message bubble
  appendUserMessage(question);

  const fileId = activeFile ? activeFile.file_id : null;
  const sheetName = sheetDropdown ? sheetDropdown.value : null;
  const enableWeb = document.getElementById("check-web-research").checked;
  const modifyExcel = document.getElementById("check-modify-excel").checked;

  // Append loading indicator
  const loadingIndicator = appendLoadingBubble();

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
    loadingIndicator.remove();

    if (!res.ok) throw new Error(data.detail || "Error answering question.");

    activeSessionId = data.session_id;
    appendAssistantMessage(data);
    loadChatSessions();

    if (data.modified_file_url) {
      btnDownloadModified.href = data.modified_file_url;
      btnDownloadModified.style.display = "inline-flex";
    }
  } catch (err) {
    loadingIndicator.remove();
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
    <div class="message-bubble">
      <div class="message-text">${escapeHtml(text)}</div>
    </div>
  `;
  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
}

function appendLoadingBubble() {
  const row = document.createElement("div");
  row.className = "message-row assistant";
  row.innerHTML = `
    <div class="message-avatar"><i class="fa-solid fa-robot"></i></div>
    <div class="message-bubble">
      <div class="message-text" style="color: var(--text-muted);">
        <i class="fa-solid fa-spinner fa-spin"></i> Analyzing spreadsheet & generating response...
      </div>
    </div>
  `;
  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
  return row;
}

function appendAssistantMessage(data) {
  const row = document.createElement("div");
  row.className = "message-row assistant";

  let innerContent = `<div class="message-text">${escapeHtml(data.content)}</div>`;

  // Formula Card
  if (data.formula) {
    innerContent += `
      <div class="formula-card">
        <div class="formula-header">
          <span><i class="fa-solid fa-square-root-variable"></i> EXCEL FORMULA</span>
          <button class="copy-btn" onclick="copyToClipboard('${escapeHtml(data.formula)}')">
            <i class="fa-solid fa-copy"></i> Copy
          </button>
        </div>
        <div class="formula-code">${escapeHtml(data.formula)}</div>
        ${data.formula_explanation ? `<div class="formula-explanation">${escapeHtml(data.formula_explanation)}</div>` : ''}
      </div>
    `;
  }

  // Analysis Result (Metrics Cards / Table)
  if (data.analysis_result) {
    const res = data.analysis_result;
    if (res.summary && res.rows) {
      // Group-by or Top N Table
      let tableRows = res.rows.map(r => {
        const keys = Object.keys(r).filter(k => k !== "formatted_value");
        return `<tr><td>${escapeHtml(r[keys[0]])}</td><td style="font-weight: 700; text-align: right;">${escapeHtml(r.formatted_value || r[keys[1]])}</td></tr>`;
      }).join("");

      innerContent += `
        <div class="analysis-table-wrapper">
          <table class="analysis-table">
            <thead>
              <tr><th>${escapeHtml(res.group_column || "Entity")}</th><th style="text-align: right;">${escapeHtml(res.value_column || "Total")}</th></tr>
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
          ${res.entity !== undefined ? `<div class="metric-card"><div class="metric-label">Highest</div><div class="metric-value">${escapeHtml(res.entity)} ($${formatNumber(res.value)})</div></div>` : ''}
        </div>
      `;
    }
  }

  // Chart Image Card
  if (data.chart_url) {
    innerContent += `
      <div class="chart-display-card">
        <img src="${data.chart_url}" alt="Generated Chart">
        <div class="chart-card-footer">
          <span><i class="fa-solid fa-chart-column"></i> ${escapeHtml(data.chart_type || "Chart")}</span>
          <a href="${data.chart_url}" target="_blank" class="btn-secondary" style="font-size: 11px; padding: 3px 8px; text-decoration: none;">
            <i class="fa-solid fa-expand"></i> View Full
          </a>
        </div>
      </div>
    `;
  }

  // Modified Excel Download Link
  if (data.modified_file_url) {
    innerContent += `
      <div style="margin-top: 6px;">
        <a href="${data.modified_file_url}" class="btn-primary" style="background: #059669; text-decoration: none; display: inline-flex; font-size: 12px;">
          <i class="fa-solid fa-file-excel"></i> Download Enhanced Excel (.xlsx)
        </a>
      </div>
    `;
  }

  row.innerHTML = `
    <div class="message-avatar"><i class="fa-solid fa-robot"></i></div>
    <div class="message-bubble">${innerContent}</div>
  `;
  chatStream.appendChild(row);
  chatStream.scrollTop = chatStream.scrollHeight;
}

// ----------------- SESSIONS & HISTORY -----------------

async function loadChatSessions() {
  try {
    const res = await fetch("/api/chat/sessions", { headers: getAuthHeaders() });
    if (res.ok) {
      const sessions = await res.json();
      chatHistoryList.innerHTML = "";
      sessions.forEach(s => {
        const item = document.createElement("div");
        item.className = `history-item ${s.id === activeSessionId ? 'active' : ''}`;
        item.onclick = () => loadSession(s.id);
        item.innerHTML = `
          <div class="history-title">${escapeHtml(s.title)}</div>
          <div class="history-meta">${s.filename ? `📁 ${s.filename} • ` : ''}${s.message_count} msgs</div>
        `;
        chatHistoryList.appendChild(item);
      });
    }
  } catch (e) {
    console.warn("Could not load sessions:", e);
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
    document.getElementById("chat-title-header").innerText = session.title;

    session.messages.forEach(m => {
      if (m.role === "user") {
        appendUserMessage(m.content);
      } else {
        appendAssistantMessage(m);
      }
    });

    loadChatSessions();
  } catch (err) {
    alert("Could not load session: " + err.message);
  }
}

// ----------------- MODALS (SCHEMA & HISTORY) -----------------

function openSchemaModal() {
  if (!activeFile || !activeFile.metadata) {
    alert("Please upload or select an Excel file first.");
    return;
  }
  const meta = activeFile.metadata;
  const currentSheet = sheetDropdown.value;
  const sheetMeta = meta.sheets[currentSheet];

  if (!sheetMeta) {
    alert("No metadata available for selected sheet.");
    return;
  }

  const container = document.getElementById("schema-content-area");
  container.innerHTML = `
    <div style="margin-bottom: 12px; font-size: 13px; color: var(--text-muted);">
      Sheet: <b>${escapeHtml(currentSheet)}</b> | Total Rows: <b>${sheetMeta.row_count}</b> | Columns: <b>${sheetMeta.column_count}</b>
    </div>
    <div class="analysis-table-wrapper">
      <table class="analysis-table">
        <thead>
          <tr>
            <th>Col</th>
            <th>Header Name</th>
            <th>Data Type</th>
            <th>Non-Null</th>
            <th>Mean / Range</th>
            <th>Sample Values</th>
          </tr>
        </thead>
        <tbody>
          ${sheetMeta.columns.map(c => `
            <tr>
              <td><b>${c.column_letter}</b></td>
              <td><b>${escapeHtml(c.name)}</b></td>
              <td><span style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 10px;">${c.data_type}</span></td>
              <td>${c.non_null_count}</td>
              <td>${c.mean_val ? `Avg: ${c.mean_val}` : (c.min_val !== null ? `${c.min_val} ~ ${c.max_val}` : '-')}</td>
              <td style="color: var(--text-muted); font-size: 11px;">${escapeHtml(c.sample_values.slice(0, 3).join(", "))}</td>
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
  container.innerHTML = "<p style='color: var(--text-muted);'>Loading SQL history...</p>";

  try {
    const res = await fetch("/api/history", { headers: getAuthHeaders() });
    const records = await res.json();
    if (records.length === 0) {
      container.innerHTML = "<p style='color: var(--text-muted);'>No analysis queries recorded yet.</p>";
      return;
    }
    container.innerHTML = `
      <div class="analysis-table-wrapper">
        <table class="analysis-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Question</th>
              <th>Operation</th>
              <th>Formula</th>
              <th>Chart</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            ${records.map(r => `
              <tr>
                <td>#${r.id}</td>
                <td style="font-weight: 600;">${escapeHtml(r.question)}</td>
                <td><span style="background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-size: 10px;">${r.operation_type}</span></td>
                <td><code>${r.formula_generated ? escapeHtml(r.formula_generated) : '-'}</code></td>
                <td>${r.chart_path ? `<a href="${r.chart_path}" target="_blank">View Chart</a>` : '-'}</td>
                <td style="font-size: 11px; color: var(--text-muted);">${new Date(r.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<p style="color: red;">Error: ${err.message}</p>`;
  }
}

function closeHistoryModal() {
  historyModal.style.display = "none";
}

// ----------------- UTILITIES -----------------

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showNotification("Excel Formula copied to clipboard!", "success");
  });
}

function showNotification(msg, type = "info") {
  const notif = document.createElement("div");
  notif.style.position = "fixed";
  notif.style.bottom = "24px";
  notif.style.right = "24px";
  notif.style.padding = "10px 18px";
  notif.style.background = type === "success" ? "#10b981" : "#2563eb";
  notif.style.color = "white";
  notif.style.borderRadius = "8px";
  notif.style.fontSize = "13px";
  notif.style.fontWeight = "600";
  notif.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
  notif.style.zIndex = "999";
  notif.innerText = msg;
  document.body.appendChild(notif);
  setTimeout(() => notif.remove(), 3200);
}

function formatBytes(bytes) {
  if (bytes === 0) return "0 Bytes";
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
