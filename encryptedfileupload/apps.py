from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EncryptedfileuploadConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "encryptedfileupload"
    verbose_name = _("Encrypted file upload")
