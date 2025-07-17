from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    apellido = models.CharField(max_length=50, verbose_name="Apellido")
    email = models.EmailField(unique=True, verbose_name="Correo electronico")
    newsletter_suscripto = models.BooleanField(default=True) # campo solo para probar el PUT masivo

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['apellido']

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Destino(models.Model):
    nombre = models.CharField(max_length=100, unique=True,verbose_name="Nombre del destino", error_messages={
        'unique': "Ya existe un destino con ese nombre."
    })
    descripcion = models.TextField(verbose_name="Descripcion")
    imagen_principal = models.ImageField(upload_to='imagenes/', blank=True, null=True, verbose_name="Imagen principal")

    class Meta:
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"
        ordering = ['id']

    def __str__(self):
        return self.nombre


class Guia(models.Model):
    destino = models.OneToOneField(Destino, on_delete=models.CASCADE, verbose_name="Destino relacionado", related_name='guia')
    # Un destino tiene una sola guia. La relacion va aca porque la guia depende del destino
    # La relacion va en la clase del que depende del otro
    # va hacia abajo la flecha. la clase depende del campo. guia depende de destino

    documentacion = models.TextField(verbose_name="Documentacion requerida")
    asistencia_viajero = models.TextField(verbose_name="Asistencia al viajero")
    equipaje_permitido = models.TextField(verbose_name="Equipaje permitido")

    class Meta:
        verbose_name = "Guia"
        verbose_name_plural = "Guias"

    def __str__(self):
        return f"Guía de {self.destino.nombre}"


class Imagen(models.Model):
    destino = models.ForeignKey('Destino', on_delete=models.CASCADE, verbose_name="Destino", related_name='imagenes')
    imagen = models.ImageField(upload_to='imagenes_destinos/', blank=True, null=True, verbose_name="Imagen")
    descripcion = models.CharField(max_length=255, blank=True, verbose_name="Descripción de la imagen")

    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imágenes"

    def __str__(self):
        return f"Imagen de {self.destino.nombre}"