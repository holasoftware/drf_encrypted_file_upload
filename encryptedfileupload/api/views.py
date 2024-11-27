import io


from django.http import FileResponse


from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser  # , FileUploadParser
from rest_framework.viewsets import GenericViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework import mixins, routers


from encryptedfileupload.models import PrivateDocument

from .serializers import (
    CreateOrUpdatePrivateDocumentSerializer,
    GetPrivateDocumentSerializer,
)


class PrivateDocumentViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):

    authentication_classes = [TokenAuthentication]
    queryset = PrivateDocument.objects.all()
    permission_classes = [IsAuthenticated]
    parser_class = [MultiPartParser]
    lookup_field = "uuid"

    serializer_classes = {
        "retrieve": GetPrivateDocumentSerializer,
        "create": CreateOrUpdatePrivateDocumentSerializer,
        "update": CreateOrUpdatePrivateDocumentSerializer,
        "partial_update": CreateOrUpdatePrivateDocumentSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes[self.action]

    def get_queryset(self):
        return PrivateDocument.objects.filter(user=self.request.user)

    @action(detail=True)
    def download(self, request, uuid=None):
        document = self.get_object()

        file_content = document.get_file_content()

        filename = document.get_filename()
        content_type = document.mime_type

        response = FileResponse(
            io.BytesIO(file_content),
            filename=filename,
            content_type=content_type,
            as_attachment=True,
        )
        return response


router = routers.DefaultRouter()
router.register("private-document", PrivateDocumentViewSet)
