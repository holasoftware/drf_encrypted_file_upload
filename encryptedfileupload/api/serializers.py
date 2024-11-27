import base64
import mimetypes

from django.urls import reverse

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


from encryptedfileupload.models import PrivateDocument
from encryptedfileupload import app_settings


class CreateOrUpdatePrivateDocumentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    title = serializers.CharField(max_length=255, write_only=True)
    file = serializers.FileField(write_only=True)

    class Meta:
        model = PrivateDocument
        fields = ("uuid", "user", "title", "file")

    def validate_file(self, value):
        if not self.is_supported_file(value.name):
            raise ValidationError("Invalid file format.")

        if not self.respects_file_size_limit(value.size):
            raise ValidationError("File too large.")

        return value

    def is_supported_file(self, filename):
        allowed_formats = app_settings.ALLOWED_FORMATS
        if allowed_formats is None:
            return True

        mimetype = mimetypes.guess_type(filename)[0]
        return mimetype in allowed_formats

    def respects_file_size_limit(self, size):
        max_file_size = app_settings.MAX_FILE_SIZE
        if max_file_size is None:
            return True

        return size <= max_file_size

    def update(self, instance, validated_data):
        updated_data = {}

        if "title" in validated_data:
            updated_data["title"] = validated_data["title"]

        if "user" in validated_data:
            updated_data["user"] = validated_data["user"]

        if "file" in validated_data:
            document_file = validated_data["file"]
            filename = document_file.name
            updated_data["filename"] = validated_data["filename"]

            # TODO: Handle properly big files
            file_content = document_file.read()
            updated_data["file_content"] = validated_data["file_content"]

        instance.update(**updated_data)
        return instance

    def create(self, validated_data):
        title = validated_data["title"]
        user = validated_data["user"]
        document_file = validated_data["file"]
        filename = document_file.name

        # TODO: Handle properly big files
        file_content = document_file.read()

        # file.file.size
        private_document = PrivateDocument.objects.create(
            user=user, title=title, file_content=file_content, filename=filename
        )

        return private_document


class GetPrivateDocumentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    title = serializers.CharField(max_length=255)
    filename = serializers.CharField(read_only=True)
    download_file_url_path = serializers.SerializerMethodField()

    class Meta:
        model = PrivateDocument
        fields = (
            "uuid",
            "user",
            "title",
            "download_file_url_path",
            "filename",
            "mime_type",
            "size",
            "created_at",
            "updated_at",
        )
        # Quizas no hace falt estos
        read_only_fields = (
            "uuid",
            "user",
            "mime_type",
            "size",
            "created_at",
            "updated_at",
        )

    def get_download_file_url_path(self, obj):
        return reverse("privatedocument-download", args=(str(obj.uuid),))
