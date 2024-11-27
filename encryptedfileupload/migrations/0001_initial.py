# Generated by Django 4.2.14 on 2024-11-26 10:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import encryptedfileupload.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PrivateDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("salt", models.BinaryField(verbose_name="salt")),
                ("encrypted_title", models.BinaryField(verbose_name="title")),
                (
                    "encrypted_file",
                    models.FileField(
                        upload_to=encryptedfileupload.models.private_document_path,
                        verbose_name="file",
                    ),
                ),
                (
                    "encrypted_original_file_name",
                    models.BinaryField(verbose_name="original file name"),
                ),
                ("encrypted_key", models.BinaryField(verbose_name="encrypted key")),
                (
                    "mime_type",
                    models.CharField(
                        db_index=True,
                        editable=False,
                        max_length=255,
                        verbose_name="MIME Type",
                    ),
                ),
                (
                    "size",
                    models.PositiveBigIntegerField(
                        editable=False,
                        help_text="Size of this file in bytes",
                        verbose_name="Size",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        editable=False, null=True, verbose_name="updated time"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="created time"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="private_documents",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "private document",
                "verbose_name_plural": "private documents",
                "ordering": ("created_at",),
            },
        ),
    ]