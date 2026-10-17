# 🚀 AI Excel Assistant
### Python • FastAPI • SQL • LLM • Spreadsheet Processing

An intelligent, production-ready AI Excel Assistant that allows users to upload spreadsheets (`.xlsx`, `.xls`, `.csv`) and interact with their data using natural language. The system inspects spreadsheet structure, generates Excel formulas, calculates analytical summaries with Pandas, visualizes data using Matplotlib/Seaborn, supports AI Web Research, embeds results into modified workbooks, and tracks conversation history in a SQL database.

---

## 📋 Features

- 🔐 **Complete Authentication & User Flow**: Sign up, email OTP verification, JWT access tokens, and authenticated user profile metrics.
- 📊 **Spreadsheet Metadata Inspection**: Automated extraction of sheet names, row/column counts, inferred data types, null distributions, statistics (min, max, mean), and sample preview rows.
- 💡 **AI Formula Generation & Validation**:
  - Generates formulas for `SUM`, `AVERAGE`, `COUNTIF`, `SUMIF`, `XLOOKUP`, `VLOOKUP`, `IF`, row-level differences, and profit margins.
  - Built-in syntax validator verifying parentheses balancing, quote closures, and valid function names.
- 📈 **Pandas Computational Summaries**: High-speed numerical calculations including grand totals, averages, multi-column group-by, top-N rankings, and actual-vs-target variance.
- 🎨 **Data Visualizations**: Matplotlib & Seaborn rendering of Bar, Line, Pie, and Scatter charts, returning both high-resolution URLs and Base64 URIs.
- 📁 **Enhanced Excel Workbook Generation**: Injects generated formulas into new worksheet columns, creates formatted summary sheets, and embeds chart images directly into downloadable `.xlsx` files using `openpyxl`.
- 🔍 **AI Web Research**: Synthesizes multi-source knowledge and domain benchmarks for business inquiries and Excel modeling practices.
- 💾 **SQL Persistence**: Stores user accounts, uploaded files, chat sessions, message transcripts, and analysis history in SQLite / PostgreSQL / MySQL using SQLAlchemy.
- 🖥️ **Interactive Web Interface**: Complete Single Page Application (SPA) served directly at `/`, alongside interactive Swagger OpenAPI docs at `/docs`.
- 🧠 **Dual LLM & Smart Fallback**: Native support for Google Gemini (`google-genai`) and OpenAI (`openai`), with an integrated Smart Rule & Heuristic Engine providing 100% functionality out-of-the-box even before API keys are configured.

---

## 🏗️ Application Flow

```
                  ┌──────────┴──────────┐
                  │                     │
               Sign Up               Sign In
                  │                     │
                  ▼                     │
          Enter Registration            │
             Information                │
                  │                     │
                  ▼                     │
          Send Email OTP               │
          (Email Service)              │
                  │                     │
                  ▼                     │
          Verify Email OTP             │
                  │                     │
                  ▼                     │
          Account Activated            │
                  │                     │
                  └──────────┬──────────┘
                             │
                             ▼
                    Authenticate User
                             │
                             ▼
                    Generate JWT Token
                             │
                             ▼
                    Store Token Securely
                             │
                             ▼
                    ┌────────────────┐
                    │   Chat Section │
                    └───────┬────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
        New Chat       Chat History    User Profile
             │              │
             ▼              ▼
       Enter Query      Previous Chats
             │
             ▼
       AI Web Research
             │
             ▼
     Search Multiple Sources
             │
             ▼
       Extract Information
             │
             ▼
      Compare Information
             │
             ▼
      Generate Response (Formula / Summary / Chart)
             │
             ▼
      Save Conversation
             │
             ▼
        Chat History (SQL)
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.11+) | Asynchronous REST API, Swagger/OpenAPI docs |
| **Server** | Uvicorn | ASGI production server |
| **Data Analysis** | Pandas & NumPy | High-performance spreadsheet manipulation |
| **Excel Engine** | openpyxl | Reading, styling, formula injection, chart embedding |
| **Charting** | Matplotlib & Seaborn | Dynamic chart rendering (Agg headless backend) |
| **Database & ORM** | SQLAlchemy | SQL models, relationships, and queries |
| **Database Engine** | SQLite (Default) / PostgreSQL | Relational storage for users, files, history |
| **Security & Auth** | Passlib, direct bcrypt, python-jose | Password hashing and JWT bearer authentication |
| **LLM Integrations** | Google Gemini (`google-genai`), OpenAI | Natural language intent understanding |
| **Frontend** | Vanilla JS, HTML5, Modern CSS | Responsive, zero-dependency interactive UI |
| **Testing** | Pytest, HTTPX | Automated unit and integration test suite |

---

## 📁 Project Structure

```
ai-excel-ass/
├── app/
│   ├── config.py                 # Pydantic settings & environment configuration
│   ├── database.py               # SQLAlchemy engine & session factory
│   ├── main.py                   # FastAPI app entrypoint, CORS, static routes
│   ├── models/                   # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── user.py               # User and OTP credentials
│   │   ├── excel_file.py         # Uploaded files and metadata
│   │   ├── chat.py               # ChatSession and ChatMessage
│   │   └── history.py            # AnalysisHistory records
│   ├── schemas/                  # Pydantic schemas (request/response validation)
│   │   ├── __init__.py
│   │   ├── auth.py               # SignUp, SignIn, VerifyOTP, Token, Profile
│   │   ├── excel.py              # SheetMetadata, ColumnMetadata, UploadResponse
│   │   ├── chat.py               # QuestionRequest, ChatMessageResponse, Sessions
│   │   └── formula.py            # FormulaGenerate, FormulaValidate
│   ├── services/                 # Core business logic services
│   │   ├── auth_service.py       # Password hashing, JWT tokens, OTP generator
│   │   ├── email_service.py      # Email OTP sender (Console log & SMTP option)
│   │   ├── excel_service.py      # openpyxl & pandas reader and workbook modifier
│   │   ├── llm_service.py        # Gemini, OpenAI, and Smart Fallback engine
│   │   ├── formula_service.py    # Excel formula generator and syntax validator
│   │   ├── analysis_service.py   # Pandas aggregation, grouping, summaries, top N
│   │   ├── chart_service.py      # Matplotlib/Seaborn chart generation
│   │   ├── web_research_service.py # Multi-source web research & fact synthesizer
│   │   └── chat_service.py       # End-to-end conversation orchestration
│   ├── routers/                  # FastAPI API route controllers
│   │   ├── auth.py               # /api/auth (register, verify, login, me)
│   │   ├── excel.py              # /api/excel (upload, metadata, download)
│   │   ├── chat.py               # /api/chat (ask, sessions, transcripts)
│   │   ├── formula.py            # /api/formula (generate, validate)
│   │   └── history.py            # /api/history (SQL analysis history)
│   ├── static/                   # Static frontend assets
│   │   ├── css/style.css         # Modern, responsive UI design
│   │   ├── js/app.js             # Client-side state and async API integration
│   │   ├── index.html            # Single Page Application
│   │   └── charts/               # Directory for generated chart PNG files
│   └── uploads/                  # Storage directory for uploaded workbooks
├── sample_data/
│   ├── create_sample_excel.py    # Generator script for sample dataset
│   └── sample_sales_data.xlsx    # Sample 100-row sales & regional targets workbook
├── tests/                        # Comprehensive Pytest suite (15 passing tests)
│   ├── conftest.py               # Test database and client fixtures
│   ├── test_auth.py              # Auth & OTP workflow tests
│   ├── test_excel_service.py     # Metadata inspection & openpyxl modifier tests
│   ├── test_formula.py           # Formula validation and construction tests
│   ├── test_analysis.py          # Pandas metrics, group-by, difference tests
│   ├── test_charts.py            # Matplotlib chart generation tests
│   └── test_api.py               # End-to-end prompt question integration tests
├── .env.example                  # Environment configuration template
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Frozen Python dependencies
└── README.md                     # Documentation
```

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.11.9)
- Git

### 2. Clone Repository & Setup Virtual Environment
```powershell
# Clone repository or navigate to workspace directory
cd c:\Users\pavan\OneDrive\Desktop\ai-excel-ass

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
# source .venv/bin/activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
*(Optional)* Add your Google Gemini or OpenAI API key in `.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
# or
OPENAI_API_KEY=your_openai_api_key_here
```
> **Note**: The application has an intelligent built-in Smart Heuristic Engine. Even without an external LLM API key, all formulas, summaries, and charts will generate accurately for spreadsheet operations.

### 5. Generate Sample Data (Optional)
A realistic 100-row sales dataset is included in `sample_data/sample_sales_data.xlsx`. To regenerate it:
```powershell
python sample_data/create_sample_excel.py
```

### 6. Run the Application
Start the FastAPI server:
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Interactive Web UI**: Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
- **Swagger OpenAPI Docs**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- **ReDoc Documentation**: Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

---

## 🧪 Running Automated Tests

Run the complete test suite with `pytest`:
```powershell
.\.venv\Scripts\pytest -v
```

All **15 tests** pass, verifying:
- Authentication & OTP verification cycle
- Excel schema & metadata extraction
- Openpyxl modified workbook generation
- Formula validation and syntax checking
- Pandas aggregation, top-N, and difference calculations
- Bar, line, pie, and scatter chart rendering
- End-to-end API integration for all sample questions

---

## 📡 REST API Reference

### 🔐 Authentication (`/api/auth`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register new user; generates and sends 6-digit OTP |
| `POST` | `/api/auth/verify-otp` | Verify OTP, activate account, and issue JWT token |
| `POST` | `/api/auth/resend-otp` | Resend fresh OTP to user's email |
| `POST` | `/api/auth/login` | Authenticate with email/password; returns JWT token |
| `GET` | `/api/auth/me` | Retrieve authenticated user profile and stats |

### 📊 Spreadsheet & Metadata (`/api/excel`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/excel/upload` | Upload `.xlsx`, `.xls`, or `.csv` file; parses metadata |
| `GET` | `/api/excel/files` | List uploaded files |
| `GET` | `/api/excel/{file_id}/metadata` | Retrieve detailed sheet schema, columns, and previews |
| `GET` | `/api/excel/{file_id}/download` | Download original uploaded workbook |
| `GET` | `/api/excel/{file_id}/download-modified`| Download AI-enhanced workbook with injected formulas and charts |

### 💬 Chat & Analysis (`/api/chat`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/chat/ask` | Submit natural-language question; returns formula, summary, chart, and explanation |
| `GET` | `/api/chat/sessions` | List user conversation sessions |
| `GET` | `/api/chat/sessions/{session_id}` | Retrieve full conversation transcript and artifacts |
| `DELETE` | `/api/chat/sessions/{session_id}` | Delete a chat session |

### 💡 Excel Formulas (`/api/formula`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/formula/generate` | Generate formula mapped to workbook columns |
| `POST` | `/api/formula/validate` | Validate syntax and balance of an Excel formula string |

### 🕒 Analysis History (`/api/history`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/history` | List SQL-stored analysis history records |
| `GET` | `/api/history/{id}` | Retrieve specific history record detail |
| `DELETE`| `/api/history/{id}` | Delete history record |

---

## 💡 Example User Questions Tested

| Question | Operation Type | Generated Artifact / Output |
| :--- | :--- | :--- |
| **"What is the total sales amount?"** | Analysis (`sum`) | Total calculation card: `$1,824,395.20` |
| **"Calculate the average sales for each region."** | Analysis (`groupby_mean`) | Formatted tabular summary of average sales by North, South, East, West |
| **"Give me an Excel formula to calculate profit margin."** | Formula (`profit_margin`) | `=IF(J2>0, M2/J2, 0)` with copy-to-clipboard button |
| **"Which product has the highest revenue?"** | Analysis (`extreme_highest`)| Identified top revenue product with total earnings |
| **"Show monthly sales as a line chart."** | Chart (`line`) | Time-series trend chart saved and displayed inline |
| **"Create a bar chart comparing sales by region."** | Chart (`bar`) | High-resolution bar chart comparing total regional sales |
| **"Find the top 10 customers by total purchase amount."** | Analysis (`top_n`) | Top 10 customer ranking table sorted by sales revenue |
| **"Add a formula to calculate the difference between Actual and Target."** | Formula & Modification | `={ActualSales}2-{TargetSales}2` injected as new column into modified `.xlsx` |

---

## ⚡ 1-Click Startup ("Start All" Option)

You have two simple ways to start the full application with a single click:

### Option A: Desktop 1-Click Launcher (Windows Batch or PowerShell)
Simply double-click:
```
start.bat
```
*(or right-click `start.ps1` -> "Run with PowerShell")*

**What `start.bat` does automatically:**
1. Checks Python 3.10+ installation.
2. Creates virtual environment (`.venv`) if not present.
3. Automatically installs all dependencies from `requirements.txt`.
4. Creates `.env` configuration from `.env.example`.
5. Pre-generates the sample sales workbook.
6. Launches your default web browser to [http://127.0.0.1:8000](http://127.0.0.1:8000).
7. Boots the Uvicorn FastAPI server.

### Option B: Web UI "⚡ Start All (Demo Run)" Button
Once the web UI opens, click the prominent **"⚡ Start All (Demo Run)"** button in the left sidebar:
- Automatically loads the sample sales dataset.
- Sequentially executes 4 core operations:
  1. Grand total sales calculation.
  2. Regional average group-by analysis.
  3. Profit margin Excel formula generation.
  4. Regional sales bar chart visualization.
- Generates the modified Excel file with embedded formulas, summary sheet, and charts ready for 1-click download!

---

## ☁️ Deployment Guide: Render & Vercel

The application is pre-configured for frictionless deployment to both **Render** and **Vercel**.

---

### 🟣 Deploy to Render (Recommended for full backend & background tasks)

Render provides persistent containers and supports FastAPI with Uvicorn natively.

#### Method 1: Deploy with Git & `render.yaml` (1-Click Blueprint)
1. Push this repository to your GitHub or GitLab account.
2. Go to the [Render Dashboard](https://dashboard.render.com).
3. Click **New +** -> **Blueprint**.
4. Connect your repository.
5. Render will automatically read `render.yaml` and configure:
   - **Environment**: Python 3.11.9
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. (Optional) In the Render Environment Variables tab, enter your `GEMINI_API_KEY` or `OPENAI_API_KEY`.
7. Click **Apply**. Your app will be live at `https://<your-service-name>.onrender.com`!

#### Method 2: Deploy as a Render Web Service (Manual)
1. Click **New +** -> **Web Service**.
2. Select your repository.
3. Set the following settings:
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `PYTHON_VERSION`: `3.11.9`
   - `SECRET_KEY`: `your-random-production-secret-key`
   - `LLM_PROVIDER`: `auto`
   - `DATABASE_URL`: `sqlite:///./ai_excel.db` (or attach a free Render PostgreSQL database URL)
5. Click **Create Web Service**.

---

### ▲ Deploy to Vercel (Serverless Function)

The repository includes `vercel.json` and `api/index.py` configured for Vercel Serverless Python Functions.

#### Method 1: Deploy via Vercel CLI
1. Install Vercel CLI (if not installed):
   ```bash
   npm i -g vercel
   ```
2. In the project directory, run:
   ```bash
   vercel
   ```
3. Follow the prompts. When asked for default settings, accept them.
4. Set production environment variables when prompted or in the dashboard:
   - `SECRET_KEY`: `your-production-secret-key`
   - `GEMINI_API_KEY`: *(optional)*
   - `OPENAI_API_KEY`: *(optional)*
5. Deploy to production:
   ```bash
   vercel --prod
   ```

#### Method 2: Deploy via Vercel Web Dashboard (Git Integration)
1. Push your repository to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new) and import your repository.
3. Framework Preset: **Other**
4. Root Directory: `./`
5. In **Environment Variables**, add:
   - `SECRET_KEY`: `your-secret-key`
   - `LLM_PROVIDER`: `auto`
   - *(Optional)* `GEMINI_API_KEY` or `OPENAI_API_KEY`
6. Click **Deploy**. Vercel will build the serverless functions and serve your application at `https://<project-name>.vercel.app`!

> **Vercel Serverless Note**: On Vercel, the filesystem is ephemeral and read-only except for `/tmp`. The application's `app/config.py` automatically detects Vercel (`VERCEL=1`) and routes SQLite, chart generation, and uploaded files to `/tmp`, ensuring zero filesystem permission errors! For permanent multi-user persistence on Vercel, you can link a cloud PostgreSQL database (such as Supabase, Neon, or Vercel Postgres) via `DATABASE_URL`.

---

## 🛡️ Security & Best Practices

- **Password Hashing**: Utilizes direct `bcrypt` hashing with adaptive salt rounds.
- **Tokens**: Standard JWT bearer tokens signed using HS256 with configurable expiry.
- **Formula Safety**: Formulas are syntactically validated and mapped to existing columns without inventing or hallucinating non-existent headers.
- **Headless Visualization**: Matplotlib is explicitly bound to the non-blocking `Agg` backend to ensure thread-safe, server-safe rendering.
- **SQL Alchemy Parameterization**: All queries use ORM parameterization to prevent SQL injection vulnerabilities.
- **Cloud Readiness**: Seamlessly runs on localhost, Render (Python native), and Vercel (Serverless).

