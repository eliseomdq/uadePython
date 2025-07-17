from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.permissions import IsAuthenticated

# Configuración de Swagger con información adicional y permisos
schema_view = get_schema_view(
    openapi.Info(
        title="API de Iridium Viajes",
        default_version='v1',
        description='Documentación general del proyecto API REST de Iridium Viajes',
        contact=openapi.Contact(email="contacto@iridiumviajes.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[IsAuthenticated],
    authentication_classes=[],
)

# Rutas de documentación Swagger
swagger_urls = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Rutas principales del proyecto
urlpatterns = [
    *swagger_urls,  
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
    path('admin/', admin.site.urls),  
    path('api/', include('api.urls')),  
]

# Servir archivos de medios 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
