from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from .models import Guia,Imagen,Usuario,Destino
from .serializer import UsuarioSerializer, ImagenUpdateDetalleSerializer,UsuarioNewsletterUpdateSerializer, DestinoSerializer,DestinoMasivoPutSerializer,GuiaSerializer,GuiaUpdateDetalleSerializer,GuiaMasivaPutSerializer,ImagenSerializer,DestinoUpdateDetalleSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny, IsAdminUser
# en las clases permission_classes = [isauthenticated o cualquier otra, isadminuser]
from rest_framework.decorators import api_view, permission_classes
from utils.permission import TienePermisoModelo
from rest_framework.pagination import PageNumberPagination
from utils.pagination import CustomPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser

def inicio(request):
    """ Mensaje de bienvenida a la API de Iridium Viajes. Formato HTML"""
    return HttpResponse("<h1> Bienvenido a la API de Iridium Viajes</h1>")


def api_info(request):
    """ informacion sobre la API de Iridium Viajes. Formato JSON """
    response = {
        "message" : "Bienvenido a la API de Iridium Viajes",
        "version" : "1.0"
    }
    return JsonResponse(response)

"""
lt/lte menor o menor igual
gt/gte mayor o mayor igual
__contains para ver si tiene esa palabra o letra, es mayus sensitive. icontains no
nombre__startswith='algo' si algo empieza con lo que quieras. endswith lo mismo

"""

class UsuarioAPIView(APIView):

    model = Usuario
    permission_classes = [IsAuthenticatedOrReadOnly, TienePermisoModelo]


    @swagger_auto_schema(
        operation_description="Obtiene la lista de usuarios",
        responses={200: UsuarioSerializer(many=True)}
    )
    def get(self, request):  # gestiona peticiones get de HTTP

        #le digo a la DB que hacer. en este caso voy a buscar los usuarios a mi DB
        usuarios = Usuario.objects.all() # ejecuta SELECT * FROM Usuarios

        # usas el serializador para convertirlo a JSON
        serializer = UsuarioSerializer(usuarios, many=True) 
         # many=true indica que es una lista de objetos
         # devolver la lista serializada como una respuesta JSON al cliente
        return Response(serializer.data) # serializer(linea 33) es un objeto, de ese objeto me da la data, que es la conversion transformada en JSON
    

    @swagger_auto_schema(
        operation_description="Crea un nuevo usuario",
        request_body=UsuarioSerializer,
        responses={
            201: UsuarioSerializer,
            400: "Datos inválidos"
        }
    )
    def post(self,request):
        # recepciono los datos enviados en la solicitud en formato de diccionario
        datos = request.data

        #serializar los datos recibidos en base a serializador de usuarios
        serializer = UsuarioSerializer(data=datos) # genera una instancia del serializador pero esta basada en los datos que recibe de la peticion (linea 40)
        
        # verifica si cumple con los campos de los modelos
        if serializer.is_valid():
            serializer.save()
            # esto hace un insert into usuarios values ...
            # debo generar una respuesta al cliente
            respuesta = {
                'mensaje':'usuario creado exitosamente',
                'datos': serializer.data
            }
            return Response(respuesta, status=status.HTTP_201_CREATED)


        # si no pasa la validacion, devuelvo los errores encontrados
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    


    @swagger_auto_schema(
        operation_description="Elimina todos los usuarios",
        responses={200: "Todos los usuarios fueron eliminados"}
    )
    def delete(self, request):
        Usuario.objects.all().delete()
        return Response({'mensaje': 'Todos los usuarios fueron eliminados'}, status=status.HTTP_200_OK)
    


    # PUT masivo para modificar el campo newsletter_suscripto
    @swagger_auto_schema(
        operation_description="Actualiza el campo 'newsletter_suscripto' para todos los usuarios",
        request_body=UsuarioNewsletterUpdateSerializer,
        responses={
            200: "Usuarios actualizados correctamente",
            400: "Error de validación"
        }
    )
    def put(self, request):
        serializer = UsuarioNewsletterUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        valor = serializer.validated_data["newsletter_suscripto"]
        actualizados = Usuario.objects.update(newsletter_suscripto=valor)

        return Response({
            "mensaje": f"{actualizados} usuarios actualizados",
            "valor_aplicado": valor
        }, status=status.HTTP_200_OK)


class UsuarioDetalleAPIView(APIView):

    model=Usuario
    permission_classes=[IsAuthenticatedOrReadOnly,TienePermisoModelo]


    @swagger_auto_schema(
        operation_description="Obtiene el detalle de un usuario por ID",
        responses={200: UsuarioSerializer()}
    )
    def get(self,request,id_usuario):
        #ir a buscar en el el modelo de usuario el id que recibo 
        # verificar si existe
        # si existe responder con los datos serializados del usuario
        # si no existe responder error 404


        try:
            # el get en vez de all sirve como filtro. SELECT FROM ... WHERE
            usuario = Usuario.objects.get(pk=id_usuario)
        except Usuario.DoesNotExist:
            return Response({'ERROR' : 'Usuario no existente'},status=status.HTTP_404_NOT_FOUND)
        

        # si encuentra lo serializa y lo devuelve
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Elimina un usuario por ID",
        responses={200: "Usuario eliminado"}
    )
    def delete(self,request, id_usuario):

        try:
            usuario = Usuario.objects.get(pk=id_usuario)
        except Usuario.DoesNotExist:
            return Response({'ERROR' : 'Usuario no existente'},status=status.HTTP_404_NOT_FOUND)
        
        usuario.delete()
        return Response({'mensaje':'El usuario fue eliminado con exito'},status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Actualiza un usuario existente",
        request_body=UsuarioSerializer,
        responses={200: UsuarioSerializer}
    )
    def put(self,request,id_usuario):
        # si existe, serializo los datos 
        # verifico si hay error en la serializacion
        # si es valido actualizo, si es invalido devuelvo errores
        try:
            usuario = Usuario.objects.get(pk=id_usuario)
        except Usuario.DoesNotExist:
            return Response({'ERROR' : 'Usuario no existente'},status=status.HTTP_404_NOT_FOUND)
        

        datos = request.data
        # serializo

        serializer = UsuarioSerializer(usuario,data=datos)  
        if serializer.is_valid():
            # si cumple las validaciones guardo el registro usuario con sus cambios
            serializer.save()
            respuesta = {
                'mensaje':'Usuario actualizado exitosamente',
                'data': serializer.data
            }
            return Response(respuesta)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class DestinoAPIView(APIView):
        
        model=Destino
        permission_classes=[IsAuthenticatedOrReadOnly,TienePermisoModelo]


        @swagger_auto_schema(
                  operation_description="Obtiene la lista de destinos",
                  responses={200:DestinoSerializer(many=True)}
        )
        def get(self,request):
            destinos=Destino.objects.all()
           # paginator=PageNumberPagination()
           # paginator.page_size = 4 # configura la cantidad de elementos por pagina
            paginator=CustomPagination()
            paginated_queryset = paginator.paginate_queryset(destinos,request)
            serializer = DestinoSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        '''
        puedo buscar segun algo solicitado por el usuario en la url

        destino = request.query_params.get('nombre',None)
        if destino
            Destino = Destino.objects.filter(destino__iexact = destino)
        else
            Destino = Destino.objects.all()



        '''

        
        @swagger_auto_schema(
                  operation_description="API para crear un nuevo destino",
                  request_body=DestinoSerializer,
                  responses={201:DestinoSerializer}
        )
        def post(self,request):
            datos = request.data
            serializer = DestinoSerializer(data=datos)
            if serializer.is_valid():
                serializer.save()
                respuesta = {
                'mensaje':'Destino creado exitosamente',
                'datos': serializer.data
                }
                return Response(respuesta, status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        


        @swagger_auto_schema(
        operation_description="Elimina todos los destinos",
        responses={200: "Todos los destinos fueron eliminados"}
        )
        def delete(self, request):
            Destino.objects.all().delete()
            return Response({'mensaje': 'Todos los destinos fueron eliminados'}, status=status.HTTP_200_OK)

        @swagger_auto_schema(
    operation_description="Actualiza el campo 'descripcion' en todos los destinos",
    request_body=DestinoMasivoPutSerializer,
    responses={
        200: "Todos los destinos fueron actualizados exitosamente",
        400: "Error de validación"
    }
)
        def put(self, request):
            serializer = DestinoMasivoPutSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            nueva_descripcion = serializer.validated_data['descripcion']
            actualizados = Destino.objects.update(descripcion=nueva_descripcion)

            return Response({
                "mensaje": f"{actualizados} destinos actualizados exitosamente",
                "descripcion_aplicada": nueva_descripcion
            }, status=status.HTTP_200_OK)



class DestinoDetalleAPIView(APIView):

    model=Destino
    permission_classes=[IsAuthenticatedOrReadOnly,TienePermisoModelo]

    parametro_id = openapi.Parameter(
        'id_destino',
        openapi.IN_PATH,
        description="ID del destino",
        type=openapi.TYPE_INTEGER,
        required=True
    )


    @swagger_auto_schema(
        operation_description="Obtiene el detalle de un destino por ID",
        responses={200: DestinoSerializer()}
    )
    def get(self,request,id_destino):
            try:
                destino = Destino.objects.get(pk=id_destino)
            except Destino.DoesNotExist:
                return Response({'ERROR' : 'Destino no existente'},status=status.HTTP_404_NOT_FOUND)
            serializer = DestinoSerializer(destino)
            return Response(serializer.data)
    


    @swagger_auto_schema(
        operation_description="Elimina un destino por ID",
        manual_parameters=[parametro_id],
        responses={200: "Destino eliminado correctamente", 404: "Destino no existente"}
    )
    def delete(self,request,id_destino):
            try:
                destino = Destino.objects.get(pk=id_destino)
            except Destino.DoesNotExist:
                return Response({'ERROR' : 'Destino no existente'},status=status.HTTP_404_NOT_FOUND)
            destino.delete()
            return Response({'mensaje':'El destino fue eliminado con exito'},status=status.HTTP_200_OK)
    


    @swagger_auto_schema(
    operation_description="Actualiza un destino existente por ID",
    request_body=DestinoUpdateDetalleSerializer,
    responses={
        200: DestinoSerializer,
        400: "Error de validación",
        404: "Destino no existente"
    }
)
    def put(self, request, id_destino):
        try:
            destino = Destino.objects.get(pk=id_destino)
        except Destino.DoesNotExist:
            return Response({'ERROR': 'Destino no existente'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DestinoUpdateDetalleSerializer(destino, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensaje': 'Destino actualizado exitosamente',
                'data': DestinoSerializer(destino).data  # devuelve respuesta con todos los campos
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class GuiaAPIView(APIView):
        
        model = Guia
        permission_classes = [IsAuthenticatedOrReadOnly, TienePermisoModelo]  


        @swagger_auto_schema(
        operation_description="Obtiene todas las guías",
        responses={200: GuiaSerializer(many=True)}
        )
        def get(self,request):
            guia=Guia.objects.all()
            serializer = GuiaSerializer(guia,many=True)
            return Response(serializer.data)
        
        '''
        RELACIONES ONE TO ONE O ONE TO MANY

        guias = Guia.objects.select_related('destino').all()  recorre la lista de guias y trae info del destino asociado
        ahorra consultas a la BD
        
        guias_filtro = Guia.objects.select_related('destino).filter(destino__nombre__iexaxct='Asis')
        buscas y ademas agregas filtros
        'destino','imagenes' separas con comas

        guias o guias_filtro es lo que tendria que ir en el serializador  serializer = GuiaSerializer(guias_filtro,many=True)

        prefetch_related es para MANY TO MANY 


        '''


        @swagger_auto_schema(
        operation_description="Crea una nueva guía",
        request_body=GuiaSerializer,
        responses={201: GuiaSerializer}
        )
        def post(self,request):
            datos = request.data
            serializer = GuiaSerializer(data=datos)
            if serializer.is_valid():
                serializer.save()
                respuesta = {
                'mensaje':'Guia creado exitosamente',
                'datos': serializer.data
                }
                return Response(respuesta, status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        


        @swagger_auto_schema(
            operation_description="Actualiza todas las guías con los valores proporcionados",
            request_body=GuiaMasivaPutSerializer,
            responses={
                200: "Todas las guías fueron actualizadas exitosamente",
                400: "Error de validación"
            }
        )
        def put(self, request):
            serializer = GuiaMasivaPutSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            campos_actualizados = serializer.validated_data

            if not campos_actualizados:
                return Response({"error": "No se proporcionaron campos para actualizar."}, status=status.HTTP_400_BAD_REQUEST)

            actualizados = Guia.objects.update(**campos_actualizados)

            return Response({
                "mensaje": f"{actualizados} guías actualizadas exitosamente",
                "valores_aplicados": campos_actualizados
            }, status=status.HTTP_200_OK)

        


        @swagger_auto_schema(
        operation_description="Elimina todas las guías",
        responses={200: "Todas las guías fueron eliminadas correctamente"}
        )
        def delete(self, request):
            Guia.objects.all().delete()
            return Response({'mensaje': 'Todas las guías fueron eliminadas'}, status=status.HTTP_200_OK)


class GuiaDetalleAPIView(APIView):

    model = Guia
    permission_classes = [IsAuthenticatedOrReadOnly, TienePermisoModelo]

    @swagger_auto_schema(
        operation_description="Obtiene una guía específica por ID",
        responses={
            200: GuiaSerializer(),
            404: "Guía no existente"
        }
    )
    def get(self, request, id_guia):
        try:
            guia = Guia.objects.select_related('destino').get(pk=id_guia)
        except Guia.DoesNotExist:
            return Response({'ERROR': 'Guía no existente'}, status=status.HTTP_404_NOT_FOUND)

        serializer = GuiaSerializer(guia)
        return Response(serializer.data)



    @swagger_auto_schema(
    operation_description="Actualiza una guía existente por ID",
    request_body=GuiaUpdateDetalleSerializer,
    responses={
        200: GuiaSerializer,
        400: "Error de validación",
        404: "Guía no existente"
    }
)
    def put(self, request, id_guia):
        try:
            guia = Guia.objects.get(pk=id_guia)
        except Guia.DoesNotExist:
            return Response({'ERROR': 'Guía no existente'}, status=status.HTTP_404_NOT_FOUND)

        serializer = GuiaUpdateDetalleSerializer(guia, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensaje': 'Guía actualizada exitosamente',
                'data': GuiaSerializer(guia).data  # respuesta completa
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    @swagger_auto_schema(
        operation_description="Elimina una guía específica por ID",
        responses={
            200: "Guía eliminada correctamente",
            404: "Guía no existente"
        }
    )
    def delete(self, request, id_guia):
        try:
            guia = Guia.objects.get(pk=id_guia)
        except Guia.DoesNotExist:
            return Response({'ERROR': 'Guía no existente'}, status=status.HTTP_404_NOT_FOUND)

        guia.delete()
        return Response({'mensaje': 'La guía fue eliminada con éxito'}, status=status.HTTP_200_OK)





class ImagenAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    model = Imagen
    permission_classes = [IsAuthenticatedOrReadOnly, TienePermisoModelo]

    @swagger_auto_schema(
        operation_description="Obtiene la lista de todas las imágenes",
        responses={200: ImagenSerializer(many=True)}
    )
    def get(self, request):
        imagenes = Imagen.objects.select_related('destino').all()
        serializer = ImagenSerializer(imagenes, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Crea una nueva imagen",
        manual_parameters=[
            openapi.Parameter('destino', openapi.IN_FORM, description="ID del destino", type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('titulo', openapi.IN_FORM, description="Título de la imagen", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('imagen', openapi.IN_FORM, description="Archivo de imagen", type=openapi.TYPE_FILE, required=True),
        ],
        responses={201: ImagenSerializer},
    )
    def post(self, request):
        serializer = ImagenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'mensaje': 'Imagen creada exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Elimina todas las imágenes",
        responses={200: "Todas las imágenes fueron eliminadas"}
    )
    def delete(self, request):
        Imagen.objects.all().delete()
        return Response({'mensaje': 'Todas las imágenes fueron eliminadas'}, status=status.HTTP_200_OK)



class ImagenDetalleAPIView(APIView):
    model = Imagen
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticatedOrReadOnly, TienePermisoModelo]

    @swagger_auto_schema(
        operation_description="Obtiene una imagen por ID",
        responses={200: ImagenSerializer()}
    )
    def get(self, request, id_imagen):
        try:
            imagen = Imagen.objects.select_related('destino').get(pk=id_imagen)
        except Imagen.DoesNotExist:
            return Response({'ERROR': 'Imagen no existente'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ImagenSerializer(imagen)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Actualiza una imagen existente por ID",
        request_body=ImagenUpdateDetalleSerializer,
        responses={
            200: ImagenSerializer,
            400: "Error de validación",
            404: "Imagen no existente"
        }
    )
    def put(self, request, id_imagen):
        try:
            imagen = Imagen.objects.get(pk=id_imagen)
        except Imagen.DoesNotExist:
            return Response({'ERROR': 'Imagen no existente'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ImagenUpdateDetalleSerializer(imagen, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'mensaje': 'Imagen actualizada exitosamente',
                'data': ImagenSerializer(imagen).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Elimina una imagen por ID",
        responses={200: "Imagen eliminada correctamente"}
    )
    def delete(self, request, id_imagen):
        try:
            imagen = Imagen.objects.get(pk=id_imagen)
        except Imagen.DoesNotExist:
            return Response({'ERROR': 'Imagen no existente'}, status=status.HTTP_404_NOT_FOUND)

        imagen.delete()
        return Response({'mensaje': 'La imagen fue eliminada con éxito'}, status=status.HTTP_200_OK)
