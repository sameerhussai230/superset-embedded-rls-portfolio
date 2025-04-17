# superset/connection.py

import os
from urllib.parse import quote_plus

# -------------------------------
# Superset & Metadata Database
# -------------------------------

# Use a strong secret key; override via environment variable if available.
# Using the key you requested for development.
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "a-very-secure-secret-key")

# Superset metadata database URI (using PostgreSQL as backend)
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "METADATA_DB_URI",
    "postgresql+psycopg2://superset:superset@db:5432/superset"
)



print(f"Metadata DB URI configured: {SQLALCHEMY_DATABASE_URI}") # Optional: Confirm URI is set
