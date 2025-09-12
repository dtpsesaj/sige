from django.shortcuts import render
from django.http import HttpResponse

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.viewsets import ModelViewSet

from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator

from .serializers import CatCategoriaSerializer, CatRespuestaDefaultSerializer, CatSolicitudSerializer, CatContactoSerializer, CatEntidadSerializer
from .models import CatCategoria,CatRespuestaDefault,CatSolicitud,CatContacto,CatEntidad,EntidadSistema,Historico

def home(request):
    return HttpResponse("¡Hola! Esta es la página principal de la app Sitio.")

def dashboard_entidades(request):
    entidades = CatEntidad.objects.select_related("municipio").all()
    paginator = Paginator(entidades, 20)  # 20 por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard/base.html", {
        "page_obj": page_obj,"entidades": entidades
    })

def api_entidades(request):
    # Parámetros de DataTables
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "").strip()
    order_column_index = request.GET.get("order[0][column]", 0)
    order_dir = request.GET.get("order[0][dir]", "asc")

    # Columnas en el mismo orden que tu tabla
    columns = ["nombre", "region", "personalidad", "municipio__nombre", "estatus"]
    order_column = columns[int(order_column_index)]

    if order_dir == "desc":
        order_column = "-" + order_column

    # Query base
    queryset = CatEntidad.objects.select_related("municipio")

    total_records = queryset.count()

    # Filtro global
    if search_value:
        queryset = queryset.filter(
            Q(nombre__icontains=search_value) |
            Q(region__icontains=search_value) |
            Q(personalidad__icontains=search_value) |
            Q(municipio__nombre__icontains=search_value) |
            Q(estatus__icontains=search_value)
        )

    filtered_records = queryset.count()

    # Orden y paginación
    entidades = queryset.order_by(order_column)[start:start+length]

    # Convertir resultados
    data = []
    for e in entidades:
        data.append([
            e.nombre,
            e.region,
            e.personalidad,
            e.municipio.nombre if e.municipio else "Sin municipio",
            e.estatus,
        ])

    return JsonResponse({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data,
    })

class CatCategoriaViewSet(ModelViewSet):
    serializer_class = CatCategoriaSerializer
    queryset = CatCategoria.objects.all()

    # GET: Get list from categoria
    @extend_schema(
        summary="Listar categorías",
        description="Obtiene todas las categorías. Puedes filtrar por `visible` o buscar por título.",
        parameters=[
            OpenApiParameter(
                name="visible",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filtra categorías visibles (true/false)."
            ),
            OpenApiParameter(
                name="titulo",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Busca categorías por título (coincidencia parcial)."
            ),
        ],
        responses={200: CatCategoriaSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Ejemplo de respuesta",
                summary="Listado de categorías",
                value=[
                    {"id": 1, "titulo": "Solicitud de usuario de acceso a sitio sesaj", "visible": True},
                    {"id": 2, "titulo": "Reporte de llamada por parte de un ente sobre un ticket", "visible": False},
                ],
            )
        ],
    )

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # POST: Create a new row in categoria
    @extend_schema(
        summary="Crear categoría",
        description="Crea una nueva categoría en el sistema.",
        request=CatCategoriaSerializer,
        responses={201: CatCategoriaSerializer},
        examples=[
            OpenApiExample(
                "Ejemplo de petición",
                summary="Nueva categoría",
                value={
                    "titulo": "Educación",
                    "visible": True
                },
            ),
            OpenApiExample(
                "Ejemplo de respuesta",
                response_only=True,
                value={
                    "id": 3,
                    "titulo": "Educación",
                    "visible": True,
                    "created_at": "2025-09-05T17:00:00Z",
                    "updated_at": "2025-09-05T17:00:00Z"
                },
            ),
        ],
    )
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Eliminar categoría",
        description="Elimina una categoría existente por ID.",
        responses={204: None},
        examples=[
            OpenApiExample(
                "Ejemplo de petición",
                summary="Eliminar categoría",
                value="DELETE /catalogos/categoria/3/"
            )
        ],
    )

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CatRespuestaDefaultViewSet(ModelViewSet):
    serializer_class = CatRespuestaDefaultSerializer
    queryset = CatRespuestaDefault.objects.all()

    @extend_schema(
        summary="Listar Respuestas",
        description="Obtiene todas las respuestas. Puedes filtrar por `visible` o buscar por título.",
        parameters=[
            OpenApiParameter(
                name="visible",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filtra respuestas default visibles (true/false)."
            ),
            OpenApiParameter(
                name="titulo",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Busca respuesta default por título (coincidencia parcial)."
            ),
        ],
        responses={200: CatRespuestaDefaultSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Ejemplo de respuesta",
                summary="Listado de respuestas default",
                value=[
                    {"id": 1, "titulo": "Borrar declaración", "respuesta": "Escribir aquí la respuesta adecuada para el problema", "visible": True},
                    {"id": 2, "titulo": "Como dar de alta un usuario", "respuesta":"Escribir aquí la respuesta adecuada para el problema", "visible": False},
                ],
            )
        ],
    )

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CatSolicitudViewSet(ModelViewSet):
    serializer_class = CatSolicitudSerializer
    queryset = CatSolicitud.objects.all()
    @extend_schema(
        description="Lista todas las categorías disponibles",
        responses={200: CatSolicitudSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    """schema = AutoSchema(
        tags=['CatSolicitud'],
        component_name='CatSolicitud',
        operation_id_base='CatSolicitud'
    )"""


class CatContactoViewSet(ModelViewSet):
    serializer_class = CatContactoSerializer
    queryset = CatContacto.objects.all()
    @extend_schema(
        description="Lista todas las categorías disponibles",
        responses={200: CatContactoSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    """schema = AutoSchema(
        tags=['CatContacto'],
        component_name='CatContacto',
        operation_id_base='CatContacto'
    )"""

class CatEntidadViewSet(ModelViewSet):
    serializer_class = CatEntidadSerializer
    queryset = CatEntidad.objects.all()
    @extend_schema(
        description="Lista todas las categorías disponibles",
        responses={200: CatEntidadSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    """schema = AutoSchema(
        tags=['CatEntidad'],
        component_name='CatEntidad',
        operation_id_base='CatEntidad'
    )"""