from rest_framework import serializers
from .models import Guia, Imagen, Usuario, Destino

class DestinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destino
        fields = '__all__'

def validate(self, data):
    nombre = data.get('nombre')

    # Si no se está modificando el nombre, no hace falta validar nada
    if not nombre:
        return data

    # Cuando se actualiza un destino existente
    if self.instance:
        # Si el nombre no cambió, no hay problema
        if self.instance.nombre.lower() == nombre.lower():
            return data
        # Si el nombre cambió, verificar si ya existe en otro
        if Destino.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({'nombre': "Ya existe un destino con ese nombre."})
    else:
        # Si es una creación nueva (POST)
        if Destino.objects.filter(nombre__iexact=nombre).exists():
            raise serializers.ValidationError({'nombre': "Ya existe un destino con ese nombre."})

    return data

class DestinoMasivoPutSerializer(serializers.Serializer):
    descripcion = serializers.CharField(required=True)

# se puede hacer una funcion validate que contemple varios campos a la vez

class DestinoUpdateDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destino
        fields = ['descripcion']  # solo el campo editable


"""
guia serializer
    # Serializador anidado. sirve para mostrar los campos que quiero de la relacion, con depth mostras todo.
    # guias=DestinoSerializer(many=True, read_only=True) 
            #depth = 1  # sirve para mostrar mas detalles del modulo destino

"""
class GuiaSerializer(serializers.ModelSerializer):

    
    class Meta: 
        model = Guia  
        fields = ['destino', 'documentacion', 'asistencia_viajero', 'equipaje_permitido'] 
        
    def validate_destino(self, value):
        if Guia.objects.filter(destino=value).exists():
            raise serializers.ValidationError("Este destino ya tiene una guía asignada.")
        return value

class GuiaMasivaPutSerializer(serializers.Serializer):
    documentacion = serializers.CharField(required=False)
    asistencia_viajero = serializers.CharField(required=False)
    equipaje_permitido = serializers.CharField(required=False)

class GuiaUpdateDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guia
        fields = ['documentacion', 'asistencia_viajero', 'equipaje_permitido']


class ImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen
        fields = ['id', 'destino', 'imagen', 'descripcion']

    def validate_imagen(self, value):
        if value.size > 5 * 1024 * 1024:  # 5 MB max
            raise serializers.ValidationError("La imagen no debe superar los 5MB.")
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("El archivo debe ser una imagen.")
        return value

class ImagenUpdateDetalleSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(required=False)

    class Meta:
        model = Imagen
        fields = ['descripcion', 'imagen']




class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

    # validacion personalizada, nombre validate_campo A Validar
    # def validate_nombre(self, value)
    #     if nombre=...:
    #         raise serializer.validationerror('el nombre no puede ser ...)
    #     return nombre
    # es para validaciones bastante rebuscadas, puede utilizarse si se cumple alguna otra condicion


class UsuarioNewsletterUpdateSerializer(serializers.Serializer):
    newsletter_suscripto = serializers.BooleanField()