import os
import sys

# Ensure project root is in sys.path even when app/main.py is executed directly
current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_file_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import engine, Base
import app.models  # Ensure all models are registered with Base

# Routers
from app.routers import auth, excel, chat, formula, history

# Create database tables automatically
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure upload and chart directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHARTS_DIR, exist_ok=True)
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
# 🚀 AI Excel Assistant API
### Python + FastAPI + SQL + LLM + Spreadsheet Processing

Interact with Excel workbooks in natural language!
- 📊 **Spreadsheet Structure & Metadata Inspection**: Read sheets, column data types, distributions, and previews.
- 💡 **AI Formula Generation**: Generate and validate formulas (SUM, AVERAGE, IF, SUMIF, COUNTIF, XLOOKUP, VLOOKUP, etc.).
- 📈 **Pandas Computational Summaries**: Totals, averages, top N rankings, group-by aggregations, variance calculations.
- 🎨 **Matplotlib Chart Visualizations**: Bar, line, pie, and scatter charts rendered dynamically.
- 📁 **Modified Workbook Generation**: Injects calculated formulas, adds AI summary tables, and embeds chart images directly into Excel!
- 🔐 **Authentication & History**: Complete User Signup, Email OTP Verification, JWT auth, and SQL Analysis History tracking.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Dedicated route to serve charts from settings.CHARTS_DIR (supports /tmp/charts on Vercel)
current_file_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_file_dir, "static")

@app.get("/static/charts/{filename}", include_in_schema=False)
def serve_chart_image(filename: str):
    file_path = os.path.join(settings.CHARTS_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    fallback_path = os.path.join(static_dir, "charts", filename)
    if os.path.exists(fallback_path):
        return FileResponse(fallback_path, media_type="image/png")
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Chart not found")

# Mount Static Files (Frontend UI and Generated Assets)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(auth.router)
app.include_router(excel.router)
app.include_router(chat.router)
app.include_router(formula.router)
app.include_router(history.router)

@app.get("/", include_in_schema=False)
def serve_frontend():
    """Serves the interactive AI Excel Assistant Single Page Application"""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "AI Excel Assistant API is running. Access /docs for Swagger UI."}

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "database": "connected",
        "llm_provider": settings.LLM_PROVIDER,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "openai_configured": bool(settings.OPENAI_API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
