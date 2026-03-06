import os


class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-jwt-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/clinic_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
