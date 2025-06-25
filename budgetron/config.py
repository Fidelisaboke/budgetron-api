"""App configuration file."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class."""
    # App secret key
    SECRET_KEY = os.getenv("SECRET_KEY")

    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Authentication Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
