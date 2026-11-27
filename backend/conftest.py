"""Test bootstrap: satisfy import-time settings requirements (MFA_ENCRYPTION_KEY,
SECRET_KEY) so tests can import Django without a real .env. Override freely."""
import os

os.environ.setdefault("SECRET_KEY", "test-only-secret-key-do-not-use-in-prod")
os.environ.setdefault("MFA_ENCRYPTION_KEY", "test-only-fernet-key-do-not-use-in-prod")
os.environ.setdefault("DB_PASSWORD", "test-only-db-password")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
