import os
import uuid
import mimetypes
import io
import base64

import pyaes


from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files import File
from django.conf import settings
from django.contrib.auth.hashers import make_password


from . import app_settings


def private_document_path(instance, filename):
    path = os.path.join(app_settings.PRIVATE_DOCUMENTS_DIR, filename)
    return path


def guess_mimetype(filename, file_content):
    # TODO: If no mimetype detected from filename, guess type using `python-magic`
    mime_type = (
        mimetypes.guess_type(filename, strict=False)[0] or "application/octet-stream"
    )

    return mime_type


class PrivateDocumentManager(models.Manager):

    def encrypt_private_data(self, filename, file_content, title):
        document_key_256 = os.urandom(32)

        document_file_aes = pyaes.AESModeOfOperationCTR(document_key_256)

        encrypted_title = document_file_aes.encrypt(title.encode("utf-8"))
        encrypted_original_filename = document_file_aes.encrypt(
            filename.encode("utf-8")
        )
        encrypted_file_content = document_file_aes.encrypt(file_content)

        salt = os.urandom(16)

        master_key = base64.b64decode(
            make_password(
                app_settings.ENCRYPTION_MASTER_PASSWORD,
                base64.b64encode(salt).decode(),
                app_settings.ENCRYPTION_MASTER_PASSWORD_HASHER,
            ).rsplit("$", 1)[1]
        )

        master_aes = pyaes.AESModeOfOperationCTR(master_key)
        encrypted_key = master_aes.encrypt(document_key_256)

        encrypted_file = File(io.BytesIO(encrypted_file_content), name=uuid.uuid4().hex)

        return {
            "encrypted_title": encrypted_title,
            "encrypted_original_filename": encrypted_original_filename,
            "encrypted_file": encrypted_file,
            "salt": salt,
            "encrypted_key": encrypted_key,
        }

    def create(self, user, filename, file_content, title=None, mime_type=None):
        size = len(file_content)

        if title is None:
            title = filename

        if mime_type is None:
            mime_type = guess_mimetype(filename=filename, file_content=file_content)

        encrypted_private_data = self.encrypt_private_data(
            filename, file_content, title
        )

        return super().create(
            user=user, mime_type=mime_type, size=size, **encrypted_private_data
        )


class PrivateDocument(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="private_documents",
    )

    salt = models.BinaryField(_("salt"))

    encrypted_title = models.BinaryField(_("title"))
    encrypted_file = models.FileField(_("file"), upload_to=private_document_path)

    encrypted_original_filename = models.BinaryField(
        _("original file name"), editable=False
    )
    encrypted_key = models.BinaryField(_("encrypted key"), editable=False)
    mime_type = models.CharField(
        _("MIME Type"), max_length=255, db_index=True, editable=False
    )
    size = models.PositiveBigIntegerField(
        _("Size"), help_text=_("Size of this file in bytes"), editable=False
    )

    updated_at = models.DateTimeField(_("updated time"), null=True, editable=False)
    created_at = models.DateTimeField(_("created time"), auto_now_add=True)

    objects = PrivateDocumentManager()

    _title = None
    _filename = None
    _file_content = None

    _private_data_modified = False

    _decrypted = False

    class Meta:
        verbose_name = _("private document")
        verbose_name_plural = _("private documents")
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.uuid}"

    def delete(self, *args, **kwargs):
        self.encrypted_file.delete()
        return super().delete(*args, **kwargs)

    def _decrypt_private_data(self):
        encrypted_key = self.encrypted_key
        salt = self.salt

        master_key = base64.b64decode(
            make_password(
                app_settings.ENCRYPTION_MASTER_PASSWORD,
                base64.b64encode(salt).decode(),
                app_settings.ENCRYPTION_MASTER_PASSWORD_HASHER,
            ).rsplit("$", 1)[1]
        )

        master_aes = pyaes.AESModeOfOperationCTR(master_key)

        key = master_aes.decrypt(encrypted_key)

        private_document_aes = pyaes.AESModeOfOperationCTR(key)
        title = private_document_aes.decrypt(self.encrypted_title).decode("utf-8")
        self._title = title

        original_filename = private_document_aes.decrypt(
            self.encrypted_original_filename
        ).decode("utf-8")
        self._filename = original_filename

        encrypted_file_content = self.encrypted_file.read()
        file_content = private_document_aes.decrypt(encrypted_file_content)
        self._file_content = file_content
        self._decrypted = True

    def get_title(self):
        if self._title is None:
            if not self._decrypted:
                self._decrypt_private_data()

        return self._title

    @property
    def title(self):
        return self.get_title()

    @title.setter
    def title(self, value):
        self._private_data_modified = True
        self._title = value

    def get_filename(self):
        if self._filename is None:
            if not self._decrypted:
                self._decrypt_private_data()

        return self._filename

    @property
    def filename(self):
        return self.get_filename()

    @filename.setter
    def filename(self, value):
        self._private_data_modified = True
        self._filename = value

    def get_file_content(self):
        if self._file_content is None:
            if not self._decrypted:
                self._decrypt_private_data()

        return self._file_content

    @property
    def file_content(self):
        return self.get_file_content()

    @file_content.setter
    def file_content(self, value):
        self._private_data_modified = True
        self._file_content = value

    def update(
        self, filename=None, file_content=None, title=None, user=None, mime_type=None
    ):
        if filename is not None:
            self.filename = filename

        if file_content is not None:
            self.file_content = file_content

        if title is not None:
            self.title = title

        update_fields = []

        if user is not None:
            self.user = user
            update_fields.append("user")

        if self._private_data_modified:
            update_fields.append("mime_type")
            update_fields.append("size")

            filename, file_content, title = (
                self.filename,
                self.file_content,
                self.title,
            )
            encrypted_private_data = self.__class__.objects.encrypt_private_data(
                filename=filename, file_content=file_content, title=title
            )
            self.size = len(file_content)

            if mime_type is None:
                mime_type = guess_mimetype(
                    filename=filename, file_content=file_content
                )
            self.mime_type = mime_type

            encrypted_private_data_fields = list(encrypted_private_data.keys())
            update_fields += encrypted_private_data_fields

            for field_name in encrypted_private_data_fields:
                setattr(self, field_name, encrypted_private_data[field_name])
        else:
            if mime_type is not None:
                self.mime_type = mime_type
                update_fields.append("mime_type")

        self.save(update_fields=update_fields)


@receiver(pre_save, sender=PrivateDocument)
def on_pre_save(sender, instance, **kwargs):
    if not instance._state.adding:
        instance.updated_at = now()
