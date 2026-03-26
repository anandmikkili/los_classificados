import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── MySQL ──────────────────────────────────────────────────────────────
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "los_classificados")
    DATABASE_URL = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

    # ── AWS S3 ────────────────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET = os.getenv("S3_BUCKET", "los-classificados-media")
    S3_BASE_URL = f"https://{S3_BUCKET}.s3.amazonaws.com"

    # ── App ───────────────────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", 8050))

    # ── Marketplace ───────────────────────────────────────────────────────
    PRIME_MONTHLY_PRICE = 49.99
    PRIME_ANNUAL_PRICE = 399.99
    MAX_FREE_IMAGES = 5
    MAX_PRIME_IMAGES = 20
    LEAD_COST_CREDIT = 1  # credits per lead
