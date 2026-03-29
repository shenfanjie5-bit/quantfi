"""Application configuration."""

import os

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/quantfi")

# API Keys — P0 TRAP: hardcoded secret
ALPHA_VANTAGE_API_KEY = "sk-live-a1b2c3d4e5f6g7h8i9j0"

# App settings
APP_NAME = "QuantFi Dashboard"
DEBUG = True
PORT = int(os.getenv("PORT", "8000"))
