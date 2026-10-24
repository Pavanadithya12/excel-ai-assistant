import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def build_pdf():
    pdf_filename = "AI_Excel_Assistant_Code_Guide.pdf"
    
    # 0.5 inch margins = 36 pt
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette: Vibrant Red, Slate Charcoal, Clean Backgrounds
    C_PRIMARY = colors.HexColor("#dc2626")      # Vibrant Crimson Red
    C_PRIMARY_DARK = colors.HexColor("#991b1b") # Deep Red
    C_PRIMARY_LIGHT = colors.HexColor("#fee2e2")# Light Red Tint
    C_TEXT = colors.HexColor("#0f172a")         # Dark Slate Charcoal
    C_MUTED = colors.HexColor("#475569")        # Slate Muted
    C_BORDER = colors.HexColor("#e2e8f0")       # Light Slate Border
    C_BG_ROW = colors.HexColor("#f8fafc")       # Soft Alternate Row
    C_CODE_BG = colors.HexColor("#1e293b")      # Code Block Background
    C_CODE_TXT = colors.HexColor("#f8fafc")     # Code Block Text

    # Custom Paragraph Styles
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.white,
        alignment=1
    )
    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#fef2f2"),
        alignment=1
    )
    style_meta = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#fca5a5"),
        alignment=1
    )
    style_h1 = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.white
    )
    style_cell = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=C_TEXT
    )
    style_cell_bold = ParagraphStyle(
        'CellTextBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=C_TEXT
    )
    style_cell_header = ParagraphStyle(
        'CellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white
    )
    style_code = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.5,
        leading=8.5,
        textColor=C_CODE_TXT
    )
    style_prose = ParagraphStyle(
        'ProseText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=C_TEXT
    )
    style_prose_bold = ParagraphStyle(
        'ProseTextBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=C_PRIMARY_DARK
    )

    def make_section_banner(title_text):
        p = Paragraph(f"<b>{title_text.upper()}</b>", style_h1)
        t = Table([[p]], colWidths=[540])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), C_PRIMARY),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        return t

    story = []

    # =========================================================================
    # PAGE 1: TITLE, AI MODELS, TECH STACK, SYSTEM & DATA FLOW
    # =========================================================================
    header_content = [
        [Paragraph("AI EXCEL ASSISTANT — COMPLETE ARCHITECTURE & CODE MANUAL", style_title)],
        [Paragraph("Full-Stack Natural Language Spreadsheet Analysis • Formula Engineering • Data Visualization • Cloud Ready", style_subtitle)],
        [Paragraph("Author: Pavan Adithya | Target: Boss & Personal GitHub Repos | Theme: Vibrant Red & White", style_meta)]
    ]
    t_header = Table(header_content, colWidths=[540])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_PRIMARY_DARK),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 8))

    # Section 1: AI Models
    story.append(make_section_banner("1. AI Models & API Keys Used in this Project"))
    story.append(Spacer(1, 3))
    models_data = [
        [
            Paragraph("LLM Tier", style_cell_header),
            Paragraph("Provider", style_cell_header),
            Paragraph("Exact Model Identifier", style_cell_header),
            Paragraph("Python SDK", style_cell_header),
            Paragraph("Env Variable", style_cell_header),
            Paragraph("Operational Role in Application", style_cell_header)
        ],
        [
            Paragraph("<b>PRIMARY</b>", style_cell_bold),
            Paragraph("Google", style_cell),
            Paragraph("gemini-2.5-flash<br/>gemini-1.5-flash", style_cell),
            Paragraph("google-genai==2.31.0", style_cell),
            Paragraph("<code>GEMINI_API_KEY</code>", style_cell),
            Paragraph("Answers spreadsheet questions, validates schema columns, generates Excel formulas (=SUM, =AVERAGE, =XLOOKUP), recommends charts, explains analysis.", style_cell)
        ],
        [
            Paragraph("<b>FALLBACK</b>", style_cell_bold),
            Paragraph("OpenAI", style_cell),
            Paragraph("gpt-4o-mini", style_cell),
            Paragraph("openai==3.33.0", style_cell),
            Paragraph("<code>OPENAI_API_KEY</code>", style_cell),
            Paragraph("Automatic fallback service. Engages seamlessly if Gemini key is missing or quota/rate limits are hit. Guarantees zero downtime.", style_cell)
        ],
        [
            Paragraph("<b>OFFLINE</b>", style_cell_bold),
            Paragraph("Native", style_cell),
            Paragraph("Smart Heuristic Rule Engine", style_cell),
            Paragraph("Built-in (FastAPI + Pandas)", style_cell),
            Paragraph("<i>None (Autonomous)</i>", style_cell),
            Paragraph("Schema-grounded deterministic engine: computes direct Pandas previews, unique counts, distributions, summaries, and formula generation without API keys.", style_cell)
        ]
    ]
    t_models = Table(models_data, colWidths=[55, 50, 95, 95, 80, 165])
    t_models.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_ROW])
    ]))
    story.append(t_models)
    story.append(Spacer(1, 8))

    # Section 2: Complete Tech Stack
    story.append(make_section_banner("2. Complete Technology Stack & Exact Versions"))
    story.append(Spacer(1, 3))
    stack_data = [
        [Paragraph("Category", style_cell_header), Paragraph("Component", style_cell_header), Paragraph("Version", style_cell_header), Paragraph("Function & Practical Responsibility", style_cell_header)],
        [Paragraph("Language", style_cell_bold), Paragraph("Python", style_cell), Paragraph("3.11+", style_cell), Paragraph("Underlying asynchronous execution runtime for backend processing and data calculations.", style_cell)],
        [Paragraph("Web Framework", style_cell_bold), Paragraph("FastAPI", style_cell), Paragraph("0.143.3", style_cell), Paragraph("High performance asynchronous REST API with automatic OpenAPI Swagger docs (/docs).", style_cell)],
        [Paragraph("ASGI Server", style_cell_bold), Paragraph("Uvicorn", style_cell), Paragraph("0.54.0", style_cell), Paragraph("Production ASGI web server handling HTTP requests and static asset streaming.", style_cell)],
        [Paragraph("Spreadsheet Core", style_cell_bold), Paragraph("Pandas", style_cell), Paragraph("3.0.6", style_cell), Paragraph("High-speed DataFrame ingestion, aggregations, multi-column group-by, min/max/mean calculations.", style_cell)],
        [Paragraph("Numerical Arrays", style_cell_bold), Paragraph("NumPy", style_cell), Paragraph("2.4.6", style_cell), Paragraph("Vectorized numeric calculations and smart column data type inference.", style_cell)],
        [Paragraph("Excel File Engine", style_cell_bold), Paragraph("openpyxl", style_cell), Paragraph("3.1.5", style_cell), Paragraph("Direct read/write access to .xlsx files, sheet metadata, formatting, formula writing, chart embedding.", style_cell)],
        [Paragraph("Data Plotting", style_cell_bold), Paragraph("Matplotlib", style_cell), Paragraph("3.11.2", style_cell), Paragraph("Core plotting engine creating bar, line, pie, and scatter charts saved as high-res PNG.", style_cell)],
        [Paragraph("Plot Styling", style_cell_bold), Paragraph("Seaborn", style_cell), Paragraph("0.13.2", style_cell), Paragraph("Statistical palette and theme styling applied over Matplotlib graphs.", style_cell)],
        [Paragraph("Database ORM", style_cell_bold), Paragraph("SQLAlchemy", style_cell), Paragraph("2.1.5", style_cell), Paragraph("Object-relational mapping models, query builder, and relationship links.", style_cell)],
        [Paragraph("SQL Database", style_cell_bold), Paragraph("SQLite (ai_excel.db)", style_cell), Paragraph("3.x (Built-in)", style_cell), Paragraph("Persistent database storing users, uploaded files, chat logs, and analysis history.", style_cell)],
        [Paragraph("Security & Hash", style_cell_bold), Paragraph("bcrypt", style_cell), Paragraph("5.0.0", style_cell), Paragraph("Direct password hashing with salt generation for tamper-proof credentials.", style_cell)],
        [Paragraph("Tokens & JWT", style_cell_bold), Paragraph("python-jose", style_cell), Paragraph("3.5.0", style_cell), Paragraph("Signed HMAC-SHA256 JWT generation and validation for session authentication.", style_cell)],
        [Paragraph("Email OTP Mailer", style_cell_bold), Paragraph("smtplib (Standard)", style_cell), Paragraph("Built-in", style_cell), Paragraph("Real-time TLS/SSL SMTP transmission of 6-digit verification codes to user mailboxes.", style_cell)],
        [Paragraph("Testing Suite", style_cell_bold), Paragraph("pytest + httpx", style_cell), Paragraph("9.1.1 / 0.28.1", style_cell), Paragraph("Automated unit and integration test suite across auth, spreadsheets, chat, and history.", style_cell)],
        [Paragraph("Frontend UI", style_cell_bold), Paragraph("HTML5 + CSS3 + JS", style_cell), Paragraph("ES6 Vanilla", style_cell), Paragraph("Vibrant Red & White Single Page App (SPA) featuring Chat, Uploads, Material Symbols Light.", style_cell)],
        [Paragraph("Deployment 1", style_cell_bold), Paragraph("Render Cloud", style_cell), Paragraph("Blueprint", style_cell), Paragraph("PaaS hosting configured via render.yaml for automated web service build.", style_cell)],
        [Paragraph("Deployment 2", style_cell_bold), Paragraph("Vercel Serverless", style_cell), Paragraph("WSGI Edge", style_cell), Paragraph("Edge serverless deployment configured via vercel.json + api/index.py.", style_cell)]
    ]
    t_stack = Table(stack_data, colWidths=[80, 95, 65, 300])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_ROW])
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 8))

    # Section 3: System Architecture & Flow
    story.append(make_section_banner("3. System Application & Data Processing Flow"))
    story.append(Spacer(1, 3))
    flow_p = Paragraph(
        "<b>Step 1: Sign Up / Sign In Request</b> (User provides credentials) • "
        "<b>Step 2: Real OTP Email Dispatch</b> (Server generates 6-digit code with 10-minute validity and delivers via TLS SMTP to user's real email) • "
        "<b>Step 3: User Verification</b> (User copies OTP from their email inbox, submits to frontend, server validates and issues signed JWT bearer token) • "
        "<b>Step 4: Spreadsheet Ingestion</b> (User uploads .xlsx/.xls/.csv ➔ Pandas extracts sheet metadata, detects domains, computes column stats ➔ saved to SQL) • "
        "<b>Step 5: Natural Language Query & Direct Dataframe Routing</b> (User asks question in chat or clicks suggested question ➔ routed to direct Pandas preview, unique counter, aggregation, formula builder, or Matplotlib visualizer) • "
        "<b>Step 6: Real-time UI Rendering & SQL History Persistence</b> (Formatted answer displayed with interactive table or chart, logged to SQLite database table <code>analysis_history</code>).",
        style_prose
    )
    t_flow = Table([[flow_p]], colWidths=[540])
    t_flow.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_PRIMARY_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, C_PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_flow)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: REAL EMAIL OTP TWO-FACTOR AUTHENTICATION DEEP-DIVE
    # =========================================================================
    story.append(make_section_banner("4. Real Email OTP & Two-Factor Authentication (2FA) Deep-Dive"))
    story.append(Spacer(1, 4))

    otp_intro = Paragraph(
        "To provide institutional-grade account security and prevent unauthorized access, the application enforces <b>Real Email Two-Factor Authentication (OTP)</b> on every user login and registration. The system connects directly to standard TLS/SSL SMTP mail servers (such as Google Gmail, Microsoft Outlook, or corporate mail gateways) to transmit a branded, tamper-resistant 6-digit confirmation code directly to the user's inbox.",
        style_prose
    )
    story.append(otp_intro)
    story.append(Spacer(1, 6))

    # Diagram Table for OTP
    otp_steps_data = [
        [
            Paragraph("<b>Stage</b>", style_cell_header),
            Paragraph("<b>Actor</b>", style_cell_header),
            Paragraph("<b>Action & Technical Implementation Details</b>", style_cell_header)
        ],
        [
            Paragraph("1. Credential Submission", style_cell_bold),
            Paragraph("User ➔ Client", style_cell),
            Paragraph("User enters email and password into the direct sign-in form. Frontend transmits JSON payload to <code>POST /api/auth/login</code>.", style_cell)
        ],
        [
            Paragraph("2. Bcrypt Validation", style_cell_bold),
            Paragraph("FastAPI ➔ DB", style_cell),
            Paragraph("Backend verifies password hash against database record using salted bcrypt. If invalid, returns 401 Unauthorized immediately.", style_cell)
        ],
        [
            Paragraph("3. OTP Generation & DB Lock", style_cell_bold),
            Paragraph("Auth Service", style_cell),
            Paragraph("Server generates a cryptographically random 6-digit numeric OTP code (<code>secrets.randbelow</code>). Sets <code>otp_code</code> and <code>otp_expires_at = UTC + 10 minutes</code> in the User SQL table.", style_cell)
        ],
        [
            Paragraph("4. Real SMTP Transmission", style_cell_bold),
            Paragraph("Email Service", style_cell),
            Paragraph("<code>email_service.send_otp_email()</code> builds a multipart (HTML + plain text) email with vibrant Red & White styling and connects to SMTP host (e.g. <code>smtp.gmail.com:587</code> with STARTTLS) to deliver the code.", style_cell)
        ],
        [
            Paragraph("5. Inbox Retrieval", style_cell_bold),
            Paragraph("User Mailbox", style_cell),
            Paragraph("User receives email from <b>Excel AI Assistant</b>, opens the message, and copies the prominent 6-digit verification code.", style_cell)
        ],
        [
            Paragraph("6. Code Verification & JWT Issuance", style_cell_bold),
            Paragraph("Client ➔ Server", style_cell),
            Paragraph("User pastes the 6-digit code into the verification modal (<code>POST /api/auth/verify-otp</code>). Server checks expiration and match. Upon success, clears the OTP, marks account verified, and issues signed HMAC-SHA256 JWT.", style_cell)
        ]
    ]
    t_otp_steps = Table(otp_steps_data, colWidths=[110, 75, 355])
    t_otp_steps.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_ROW])
    ]))
    story.append(t_otp_steps)
    story.append(Spacer(1, 8))

    # Configuration Guide for Gmail & SMTP
    story.append(make_section_banner("How to Configure Real Gmail / SMTP Email Delivery in .env"))
    story.append(Spacer(1, 4))
    
    gmail_guide = Paragraph(
        "<b>Configuring Google Gmail App Passwords (Recommended for Instant Setup):</b><br/>"
        "1. Open Google Account Security (<b>https://myaccount.google.com/security</b>) ➔ Turn 2-Step Verification <b>ON</b>.<br/>"
        "2. Search for <b>App Passwords</b> in Google Account search bar ➔ Name it <b>'Excel AI Assistant'</b>.<br/>"
        "3. Google gives a 16-letter code (e.g. <code>abcd efgh ijkl mnop</code>). In <code>.env</code> (or Render/Vercel settings), enter:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<code>SMTP_HOST=\"smtp.gmail.com\" &nbsp;|&nbsp; SMTP_PORT=587 &nbsp;|&nbsp; SMTP_USER=\"you@gmail.com\" &nbsp;|&nbsp; SMTP_PASSWORD=\"your-16-char-code\"</code><br/>"
        "4. Save and restart server. Real verification emails will instantly arrive in your mailbox on every login!",
        style_prose
    )
    t_gmail = Table([[gmail_guide]], colWidths=[540])
    t_gmail.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_ROW),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_gmail)
    story.append(Spacer(1, 5))

    # Section 5: Codebase Map
    story.append(make_section_banner("5. Complete Codebase Map — Every File, Location & Responsibility"))
    story.append(Spacer(1, 2))
    code_map_data = [
        [Paragraph("File Path / Location", style_cell_header), Paragraph("Layer", style_cell_header), Paragraph("Key Classes & Functions", style_cell_header), Paragraph("Purpose & Implementation Details", style_cell_header)],
        [Paragraph("app/main.py", style_cell_bold), Paragraph("Entry Point", style_cell), Paragraph("app, lifespan(), mount()", style_cell), Paragraph("Main FastAPI initialization, CORS with expose_headers, router registration, static files mounting.", style_cell)],
        [Paragraph("app/config.py", style_cell_bold), Paragraph("Config", style_cell), Paragraph("Settings, settings", style_cell), Paragraph("Pydantic BaseSettings loading .env, database URLs, SMTP keys, LLM keys, and cloud flags.", style_cell)],
        [Paragraph("app/database.py", style_cell_bold), Paragraph("Database", style_cell), Paragraph("Base, engine, get_db()", style_cell), Paragraph("SQLAlchemy engine, SessionLocal factory, declarative base, and request-scoped session injection.", style_cell)],
        [Paragraph("app/models/*.py", style_cell_bold), Paragraph("ORM Models", style_cell), Paragraph("User, ExcelFile, ChatSession, History", style_cell), Paragraph("Relational database schema definitions mapping users, spreadsheets, chat threads, and analysis records.", style_cell)],
        [Paragraph("app/services/email_service.py", style_cell_bold), Paragraph("Mailing", style_cell), Paragraph("EmailService.send_otp_email()", style_cell), Paragraph("Dispatches multipart HTML/text emails containing 6-digit codes via TLS/SSL SMTP (Gmail, Outlook, SES).", style_cell)],
        [Paragraph("app/services/auth_service.py", style_cell_bold), Paragraph("Security", style_cell), Paragraph("hash_password(), create_jwt()", style_cell), Paragraph("Bcrypt salted hashing, 6-digit OTP generation, HMAC-SHA256 JWT token creation, and auth guards.", style_cell)],
        [Paragraph("app/services/excel_service.py", style_cell_bold), Paragraph("Spreadsheet", style_cell), Paragraph("inspect_excel(), domain_suggest()", style_cell), Paragraph("Reads .xlsx/.xls/.csv, infers data types, detects domains (Project Mgmt, Finance), generates prompts.", style_cell)],
        [Paragraph("app/services/chat_service.py", style_cell_bold), Paragraph("Orchestrate", style_cell), Paragraph("process_user_query(), df_query()", style_cell), Paragraph("Routes queries to direct Pandas computation (previews, unique counts, distributions) or LLM reasoning.", style_cell)],
        [Paragraph("app/services/formula_service.py", style_cell_bold), Paragraph("Formulas", style_cell), Paragraph("generate_formula(), validate()", style_cell), Paragraph("Generates syntactically validated formulas (SUM, AVERAGE, XLOOKUP, IF) mapped strictly to real headers.", style_cell)],
        [Paragraph("app/services/chart_service.py", style_cell_bold), Paragraph("Visuals", style_cell), Paragraph("render_chart(), save_png()", style_cell), Paragraph("Headless Matplotlib/Seaborn rendering of Bar, Line, Pie, and Scatter plots saved to static charts directory.", style_cell)],
        [Paragraph("app/routers/*.py", style_cell_bold), Paragraph("REST API", style_cell), Paragraph("auth, excel, chat, formula, history", style_cell), Paragraph("FastAPI route controllers handling registration, login, OTP verification, file upload, chat, and history.", style_cell)],
        [Paragraph("app/static/css/style.css", style_cell_bold), Paragraph("UI Styling", style_cell), Paragraph("Red & White Studio Theme", style_cell), Paragraph("Complete CSS stylesheet: crisp white canvas, radiant crimson accents, high contrast slate, smooth cards.", style_cell)],
        [Paragraph("app/static/index.html", style_cell_bold), Paragraph("UI Template", style_cell), Paragraph("Single Page App (SPA)", style_cell), Paragraph("Direct auth screen, 3-column workspace, unique custom SVG emblem, Material Symbols Light icons.", style_cell)],
        [Paragraph("app/static/js/app.js", style_cell_bold), Paragraph("UI Controller", style_cell), Paragraph("Application Controller", style_cell), Paragraph("Handles auth state, file uploads, chat stream rendering, interactive table previews, and document deletion.", style_cell)]
    ]
    t_code_map = Table(code_map_data, colWidths=[95, 60, 120, 265])
    t_code_map.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_ROW])
    ]))
    story.append(t_code_map)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: CORE CODE LOGIC IMPLEMENTATIONS
    # =========================================================================
    story.append(make_section_banner("6. Core Code Logic from Scratch — How the Engine Works"))
    story.append(Spacer(1, 4))

    # Code block 1: Real Email Service
    story.append(Paragraph("<b>6.1 Real Email Service with TLS SMTP (app/services/email_service.py)</b>", style_prose_bold))
    code_email = (
        "import smtplib\n"
        "from email.mime.multipart import MIMEMultipart\n"
        "from email.mime.text import MIMEText\n"
        "from app.config import settings\n\n"
        "class EmailService:\n"
        "    @staticmethod\n"
        "    def send_otp_email(to_email: str, otp_code: str) -> bool:\n"
        "        subject = f'Your Verification Code: {otp_code} — {settings.PROJECT_NAME}'\n"
        "        body_html = f'''<div style=\"border:2px dashed #dc2626; padding:20px; text-align:center;\">\n"
        "                           <h2>Your 6-Digit OTP: <span style=\"color:#dc2626;\">{otp_code}</span></h2>\n"
        "                           <p>Valid for 10 minutes. Copy this code into the login prompt.</p></div>'''\n"
        "        if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD:\n"
        "            msg = MIMEMultipart('alternative')\n"
        "            msg['From'] = f'{settings.PROJECT_NAME} <{settings.FROM_EMAIL}>'\n"
        "            msg['To'], msg['Subject'] = to_email, subject\n"
        "            msg.attach(MIMEText(body_html, 'html'))\n"
        "            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:\n"
        "                server.starttls()\n"
        "                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)\n"
        "                server.send_message(msg)\n"
        "            return True\n"
        "        return False"
    )
    def escape_code(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>').replace(' ', '&nbsp;')

    t_code1 = Table([[Paragraph(escape_code(code_email), style_code)]], colWidths=[540])
    t_code1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_CODE_BG),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code1)
    story.append(Spacer(1, 6))

    # Code block 2: Direct DataFrame Query Engine
    story.append(Paragraph("<b>6.2 Direct DataFrame Query & Preview Engine (app/services/chat_service.py)</b>", style_prose_bold))
    code_df = (
        "def _handle_direct_dataframe_query(self, question: str, df: pd.DataFrame, file_record, session_id):\n"
        "    q = question.lower().strip()\n"
        "    # 1. Preview first N rows (Returns structured table for HTML rendering)\n"
        "    if re.search(r'preview|first \\d+ rows', q):\n"
        "        preview_df = df.head(10).fillna('')\n"
        "        return {'role': 'assistant', 'content': 'Here is a preview of the first 10 rows:',\n"
        "                'analysis_result': {'is_table': True, 'columns': list(preview_df.columns),\n"
        "                                   'rows': preview_df.to_dict(orient='records')}}\n"
        "    # 2. Count unique entries for specific column\n"
        "    match_uniq = re.search(r'how many unique (.+?) entries', q)\n"
        "    if match_uniq:\n"
        "        col = match_uniq.group(1).strip()\n"
        "        return {'role': 'assistant', 'content': f'Found {df[col].nunique()} unique entries in {col}.'}\n"
        "    # 3. Column Data Types Breakdown\n"
        "    if 'data type' in q or 'data types' in q:\n"
        "        types_rows = [{'Column Name': col, 'Data Type': str(df[col].dtype)} for col in df.columns]\n"
        "        return {'role': 'assistant', 'content': 'Column Data Types Breakdown:',\n"
        "                'analysis_result': {'is_table': True, 'columns': ['Column Name', 'Data Type'], 'rows': types_rows}}"
    )
    t_code2 = Table([[Paragraph(escape_code(code_df), style_code)]], colWidths=[540])
    t_code2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_CODE_BG),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code2)
    story.append(Spacer(1, 6))

    # Code block 3: Domain Aware Prompt Engineering
    story.append(Paragraph("<b>6.3 Domain Detection & Dynamic Question Suggestions (app/services/excel_service.py)</b>", style_prose_bold))
    code_domain = (
        "def _infer_document_domain(columns: list) -> str:\n"
        "    col_names = [c.lower() for c in columns]\n"
        "    if any(k in col_names for k in ['task', 'assignee', 'progress', 'start date', 'deadline']):\n"
        "        return 'Project Management & Operations'\n"
        "    elif any(k in col_names for k in ['revenue', 'sales', 'profit', 'margin', 'price', 'cost']):\n"
        "        return 'Financial & Sales Analytics'\n"
        "    return 'General Tabular Dataset'\n\n"
        "def generate_dynamic_suggestions(meta: dict) -> list:\n"
        "    domain = meta.get('inferred_domain')\n"
        "    # Generates domain-tailored questions without repeating generic dimensions"
    )
    t_code3 = Table([[Paragraph(escape_code(code_domain), style_code)]], colWidths=[540])
    t_code3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_CODE_BG),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code3)
    story.append(Spacer(1, 6))

    # Code block 4: Headless Chart Generation
    story.append(Paragraph("<b>6.4 Headless Visualization Engine (app/services/chart_service.py)</b>", style_prose_bold))
    code_chart = (
        "import matplotlib\n"
        "matplotlib.use('Agg') # Thread-safe non-GUI server backend\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n\n"
        "def render_chart(df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, title: str, output_path: str):\n"
        "    plt.figure(figsize=(8, 4.5))\n"
        "    sns.set_theme(style='whitegrid', palette='Reds_r') # Vibrant Crimson Palette\n"
        "    if chart_type == 'bar':\n"
        "        sns.barplot(data=df.head(15), x=x_col, y=y_col, color='#dc2626')\n"
        "        plt.xticks(rotation=40, ha='right')\n"
        "    plt.title(title, fontsize=12, fontweight='bold', pad=12)\n"
        "    plt.tight_layout()\n"
        "    plt.savefig(output_path, dpi=160)\n"
        "    plt.close()"
    )
    t_code4 = Table([[Paragraph(escape_code(code_chart), style_code)]], colWidths=[540])
    t_code4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_CODE_BG),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_code4)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: REST API SPEC, LOCAL SETUP, DEPLOYMENT & VERIFICATION
    # =========================================================================
    story.append(make_section_banner("7. REST API Specification (FastAPI Swagger / OpenAPI)"))
    story.append(Spacer(1, 3))
    api_data = [
        [Paragraph("HTTP", style_cell_header), Paragraph("Route Endpoint", style_cell_header), Paragraph("Auth Required", style_cell_header), Paragraph("Payload / Parameters", style_cell_header), Paragraph("Response Description", style_cell_header)],
        [Paragraph("POST", style_cell_bold), Paragraph("/api/auth/register", style_cell), Paragraph("No", style_cell), Paragraph("{email, full_name, password}", style_cell), Paragraph("Registers user & dispatches real 6-digit OTP code to email.", style_cell)],
        [Paragraph("POST", style_cell_bold), Paragraph("/api/auth/login", style_cell), Paragraph("No", style_cell), Paragraph("{email, password}", style_cell), Paragraph("Verifies credentials & sends 6-digit 2FA login OTP to email.", style_cell)],
        [Paragraph("POST", style_cell_bold), Paragraph("/api/auth/verify-otp", style_cell), Paragraph("No", style_cell), Paragraph("{email, otp}", style_cell), Paragraph("Validates OTP, marks account verified, returns signed JWT token.", style_cell)],
        [Paragraph("POST", style_cell_bold), Paragraph("/api/auth/resend-otp", style_cell), Paragraph("No", style_cell), Paragraph("{email}", style_cell), Paragraph("Generates and dispatches a fresh 6-digit OTP to the email address.", style_cell)],
        [Paragraph("GET", style_cell_bold), Paragraph("/api/auth/me", style_cell), Paragraph("Bearer JWT", style_cell), Paragraph("None", style_cell), Paragraph("Returns current authenticated user profile and database usage stats.", style_cell)],
        [Paragraph("POST", style_cell_bold), Paragraph("/api/excel/upload", style_cell), Paragraph("Bearer JWT", style_cell), Paragraph("multipart/form-data (.xlsx, .csv)", style_cell), Paragraph("Parses sheet names, column headers, datatypes, row counts into SQL.", style_cell)],
        [Paragraph("GET", style_cell_bold), Paragraph("/api/excel/files", style_cell), Paragraph("Bearer JWT", style_cell), Paragraph("None", style_cell), Paragraph("Lists all user uploaded documents stored in the database.", style_cell)],
        [Paragraph("DELETE", style_cell_bold), Paragraph("/api/excel/{file_id}", style_cell), Paragraph("Bearer JWT", style_cell), Paragraph("file_id in path", style_cell), Paragraph("Permanently deletes uploaded spreadsheet from database & disk.", style_cell)],
        [Paragraph("POST", style_cell_bold), Paragraph("/api/chat/ask", style_cell), Paragraph("Bearer JWT", style_cell), Paragraph("{file_id, question, session_id}", style_cell), Paragraph("Executes natural language analysis: returns table preview, metric, or chart.", style_cell)],
        [Paragraph("GET", style_cell_bold), Paragraph("/api/chat/sessions", style_cell), Paragraph("Bearer JWT", style_cell), Paragraph("None", style_cell), Paragraph("Returns all user conversation threads from SQL database.", style_cell)],
        [Paragraph("DELETE", style_cell_bold), Paragraph("/api/chat/sessions/{id}", style_cell), Paragraph("Bearer JWT", style_cell), Paragraph("id in path", style_cell), Paragraph("Deletes conversation thread safely and idempotently without errors.", style_cell)],
        [Paragraph("GET", style_cell_bold), Paragraph("/api/history", style_cell), Paragraph("Bearer JWT", style_cell), Paragraph("None", style_cell), Paragraph("Returns chronological log of all formula & analysis records.", style_cell)],
        [Paragraph("DELETE", style_cell_bold), Paragraph("/api/history/{id}", style_cell), Paragraph("Bearer JWT", style_cell), Paragraph("id in path", style_cell), Paragraph("Deletes single analysis record from database.", style_cell)],
        [Paragraph("GET", style_cell_bold), Paragraph("/health", style_cell), Paragraph("No", style_cell), Paragraph("None", style_cell), Paragraph("Health check returning DB connectivity and configured LLM providers.", style_cell)]
    ]
    t_api = Table(api_data, colWidths=[40, 115, 65, 125, 195])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, C_BG_ROW])
    ]))
    story.append(t_api)
    story.append(Spacer(1, 6))

    # Section 8: Local Setup & Run
    story.append(make_section_banner("8. Local Setup & 1-Click Launch Instructions"))
    story.append(Spacer(1, 3))
    setup_p = Paragraph(
        "<b>Step 1: Clone Repositories</b><br/>"
        "<code>git clone https://github.com/Pavanadithya12/excel-ai-assistant.git</code><br/>"
        "<b>Step 2: Automated 1-Click Launch (Windows)</b><br/>"
        "Double-click <code>start.bat</code> (or run <code>.\\start.ps1</code>). Automatically verifies Python 3.11, initializes virtual environment, installs dependencies, and launches Uvicorn at <b>http://localhost:8000</b>.<br/>"
        "<b>Step 3: Manual Startup</b><br/>"
        "<code>python -m venv .venv &nbsp;|&nbsp; .\\.venv\\Scripts\\activate &nbsp;|&nbsp; pip install -r requirements.txt</code><br/>"
        "<code>uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload</code>",
        style_prose
    )
    t_setup = Table([[setup_p]], colWidths=[540])
    t_setup.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_BG_ROW),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_setup)
    story.append(Spacer(1, 6))

    # Section 9: Cloud Deployment & Test Suite
    story.append(make_section_banner("9. Cloud Deployment & Automated Testing"))
    story.append(Spacer(1, 3))
    deploy_p = Paragraph(
        "<b>Render Deployment (Blueprint PaaS):</b><br/>"
        "1. In <b>dashboard.render.com</b> ➔ Click <b>New +</b> ➔ <b>Blueprint</b> ➔ Connect GitHub repository.<br/>"
        "2. Render reads <code>render.yaml</code>, installs packages from UTF-8 <code>requirements.txt</code>, and launches Uvicorn on <code>$PORT</code>.<br/>"
        "3. In Environment Variables, configure <code>SMTP_USER</code>, <code>SMTP_PASSWORD</code>, and <code>GEMINI_API_KEY</code>.<br/>"
        "<i>*Note on Free Tier: Render sleeps after 15m inactivity. Allow 50-60s on first request to wake up the service.</i><br/>"
        "<b>Vercel Serverless Deployment:</b><br/>"
        "Run <code>vercel --prod</code> or connect Git. Automatically builds via <code>api/index.py</code> with ephemeral SQLite routing.<br/>"
        "<b>Automated Test Suite:</b><br/>"
        "Run <code>pytest -v</code>. Executes 15 comprehensive unit tests covering auth, bcrypt hashing, OTP lifecycle, Excel metadata extraction, formula validation, and Pandas calculations.",
        style_prose
    )
    t_deploy = Table([[deploy_p]], colWidths=[540])
    t_deploy.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_PRIMARY_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, C_PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_deploy)
    story.append(Spacer(1, 6))

    # Footer
    footer_table = Table([
        [
            Paragraph("<b>AI Excel Assistant • Code Architecture & Manual</b>", style_cell),
            Paragraph("<b>Repositories:</b> github.com/Pavanadithya12/excel-ai-assistant • github.com/revalsysprashant/AI-Excel-Assistant", style_cell),
            Paragraph("<b>Developer:</b> Pavan Adithya", style_cell)
        ]
    ], colWidths=[180, 260, 100])
    footer_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(footer_table)

    # Build Document
    doc.build(story)
    print(f"Generated {pdf_filename} successfully!")

if __name__ == "__main__":
    build_pdf()
