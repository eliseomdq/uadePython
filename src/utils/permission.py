from rest_framework.permissions import BasePermission

class TienePermisoModelo(BasePermission):
#   verificar si el usuario tiene permiso para realizar una accion sobre el modelo asociado a la vista


    def has_permission(self, request, view):  # el parametro view hace referencia a la clase que yo quiero verificar
        #comprobar que la view tiene un atributo llamado model
        if not hasattr(view,'model'):
            return False
        model=view.model
        app_label=model._meta.app_label
        model_name=model._meta.model_name
        metodo_permiso={
            'GET' : f'{app_label}.view_{model_name}',
            'POST': f'{app_label}.add_{model_name}',
            'PUT': f'{app_label}.change_{model_name}',
            'PATH': f'{app_label}.change_{model_name}',
            'DELETE': f'{app_label}.delete_{model_name}',
        }
        # obtengo el metodo HTTP de la peticion
        permiso = metodo_permiso.get(request.method)

        if permiso:
            return request.user.has_perm(permiso)
        
        return False