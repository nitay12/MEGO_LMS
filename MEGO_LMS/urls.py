from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from assignments import views

schema_view = get_schema_view(
    openapi.Info(
        title="MeGo LMS API",
        default_version='v1',
        description="REST API for managing MeGo learning management system",
        # TODO: Add TOS and license
        # terms_of_service="https://www.yourapp.com/terms/",
        # license=openapi.License(name="Your License"),
        contact=openapi.Contact(email="nitay@mego.org.il"),

    ),
    public=True,
    permission_classes=(permissions.AllowAny,),

)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('assignments.urls')),

    path('api/activate/', views.activate, name='activate'),

    # DOCS URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
