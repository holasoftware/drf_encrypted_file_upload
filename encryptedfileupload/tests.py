from uuid import UUID


from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile


from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status


from .models import PrivateDocument


User = get_user_model()


class TestDocumentEncryptionDecryption(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="root")

    def test_encryption1(self):
        doc_uuid = PrivateDocument.objects.create(user=self.user, filename="test.pdf", file_content=b"test", title="this is a title").uuid

        document = PrivateDocument.objects.get(uuid=doc_uuid)

        self.assertEqual(document.title, "this is a title")
        self.assertEqual(document.file_content, b"test")
        self.assertEqual(document.filename, "test.pdf")


class TestAPI(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="root")
        self.user_token = Token.objects.create(user=self.user)

    def test_upload_and_download_file(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + self.user_token.key)

        document_file = SimpleUploadedFile("document.pdf", b"this is the content")

        response = client.post("/api/v1/private-document/", {"title": "document title", "file": document_file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("uuid", response.data)

        try:
            UUID(response.data["uuid"])
        except ValueError:
            self.fail("document has no valid uuid")

        response = client.get("/api/v1/private-document/%s/download/" % response.data["uuid"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.filename, "document.pdf")