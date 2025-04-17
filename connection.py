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

# -------------------------------
# SQL Server Connection Details (REMOVED)
# -------------------------------
# Configuration for the 'umesh.v' SQL Server database has been removed
# as requested, focusing on CSV uploads.

# Removed the check for the placeholder key
# if SECRET_KEY == "..." and os.environ.get("FLASK_ENV") == "production":
#      print("WARNING: Using default Superset SECRET_KEY in production environment!")

print(f"Metadata DB URI configured: {SQLALCHEMY_DATABASE_URI}") # Optional: Confirm URI is set