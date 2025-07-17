from django.urls import path
from . import views


urlpatterns = [
    path('',views.inicio,name='inicio'), 
    path('info/', views.api_info, name='api_info'),
    path('usuarios/',views.UsuarioAPIView.as_view()),
    path('usuarios/<int:id_usuario>',views.UsuarioDetalleAPIView.as_view()),
    path('destinos/',views.DestinoAPIView.as_view(), name='destinos'),
    path('destinos/<int:id_destino>/',views.DestinoDetalleAPIView.as_view(), name='destino_detalle'),
    path('guias/',views.GuiaAPIView.as_view()),
    path('guias/<int:id_guia>', views.GuiaDetalleAPIView.as_view()),
    path('imagenes/', views.ImagenAPIView.as_view()),
    path('imagenes/<int:id_imagen>', views.ImagenDetalleAPIView.as_view()),
]
