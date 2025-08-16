import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-moi-en-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "png", "jpg", "jpeg", "txt"}
