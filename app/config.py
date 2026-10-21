import os

from dotenv import load_dotenv

# Load .env from the project root
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@portal.com").lower()
    S3_BUCKET = os.getenv("S3_BUCKET", "")
    AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "docx", "jpg", "jpeg", "png"}
