import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from sample_data.create_sample_excel import generate_sample_sales_data

TEST_DATABASE_URL = "sqlite:///./test_ai_excel.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    Base.metadata.create_all(bind=test_engine)
    sample_file = "sample_data/sample_sales_data.xlsx"
    if not os.path.exists(sample_file):
        generate_sample_sales_data(sample_file)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("test_ai_excel.db"):
        try:
            os.remove("test_ai_excel.db")
        except Exception:
            pass

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
