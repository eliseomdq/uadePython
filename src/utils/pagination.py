from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size=3
    # page_size_query_param='page_size o tam_pagina'. sobreescribe lo de arriba, es lo que va en el navegador
    max_page_size=20 # limite del elementos q el user puede solicitar por medio de page_size

    def get_paginated_response(self, data):

        return Response({
            'total_items' : self.page.paginator.count,
            'total_pages' : self.page.paginator.num_pages,
            'current_page' : self.page.number,
            'next_page' : self.get_next_link(),
            'previous_page' : self.get_previous_link(),
            'data' : data
        })