import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


ALLOWED_FORMATS = getattr(settings, "PRIVATE_DOCUMENT_ALLOWED_FORMATS", None)
MAX_FILE_SIZE = getattr(settings, "PRIVATE_DOCUMENT_MAX_FILE_SIZE", None)

PRIVATE_DOCUMENTS_DIR = getattr(settings, "PRIVATE_DOCUMENTS_DIR", "private_documents")

ENCRYPTION_MASTER_PASSWORD_HASHER = getattr(
    settings, "ENCRYPTION_MASTER_PASSWORD_HASHER", "pbkdf2_sha256"
)

ENCRYPTION_MASTER_PASSWORD = os.getenv("ENCRYPTION_MASTER_PASSWORD")
if ENCRYPTION_MASTER_PASSWORD is None:
    raise ImproperlyConfigured(
        "Missing master password! Set environment variable ENCRYPTION_MASTER_PASSWORD."
    )
