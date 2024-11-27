from django.urls import path, include


from rest_framework.authtoken.views import obtain_auth_token

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import router

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(),
        name="redoc",
    ),
    path("auth/", obtain_auth_token),
    path("", include(router.urls), name="private-document"),
]
