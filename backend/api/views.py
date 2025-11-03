from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from datetime import datetime

from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404

from sitio.models import (CatCategoria,CatRespuestaDefault,CatSolicitud,CatContacto,CatEntidad,
                    EntidadSistema,Historico, ObservacionEtapa, EtapasSistema)

from sitio.services import get_entidad_detalles, get_etapas_por_sistema_entidad


# Create your views here.
def modulo_estadisticas(request):

    return render(request, "dashboard/estadisticas.html", {})

def api_entidades(request):
    # Parámetros de DataTables
    draw = int(request.GET.get("draw", 1))
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 10))
    search_value = request.GET.get("search[value]", "").strip()
    order_column_index = request.GET.get("order[0][column]", 0)
    order_dir = request.GET.get("order[0][dir]", "asc")

    # Columnas en el mismo orden que tu tabla
    columns = ["id","nombre", "region", "personalidad", "municipio__nombre", "estatus"]
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
            e.pk,
        ])

    return JsonResponse({
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data,
    })


@api_view(["GET"])
def obtencion_datos_entidad_detalles(request, entidad_id):
    data = get_entidad_detalles(entidad_id)

    return Response(data)


@api_view(["GET"])
def obtencion_etapas_por_sistema_entidad(request, entidad_sistema):
    etapas_data = get_etapas_por_sistema_entidad(entidad_sistema)

    return Response(etapas_data)


@api_view(["GET"])
def entidad_vista_rapida(request, pk):
    entidad_id = int(pk)
    try:
        entidad = get_object_or_404(CatEntidad, pk=entidad_id)
        data = {
            "id": entidad.pk,
            "nombre": entidad.nombre,
            "region": entidad.region,
            "personalidad": entidad.personalidad,
            "municipio": entidad.municipio.nombre if entidad.municipio else "Sin municipio",
            "estatus": entidad.estatus,
            "sistemas": {}
        }

        if hasattr(entidad, 'entidad_sistemas'):
            for sistema in entidad.entidad_sistemas.all():
                data["sistemas"][sistema.sistema] = {
                    "version": sistema.version,
                    "licencia_fecha": sistema.licencia_fecha,
                    "licencia": sistema.licencia,
                    "fuente": sistema.fuente,
                    "operacion_fecha": sistema.operacion_fecha,
                    "operacion_modo": sistema.operacion_modo,
                    "licencia": sistema.licencia,
                    "pdn_conexion": sistema.pdn_conexion,
                    "pdn_fecha": sistema.pdn_fecha,
                    "pdn_tipo_conexion": sistema.pdn_tipo_conexion,
                }


        return JsonResponse(data)
    except CatEntidad.DoesNotExist:
        raise Http404("Entidad no encontrada")


@api_view(["GET"])
def entidad_detalle(request, pk):
    # Obtener la entidad o lanzar 404 automáticamente
    entidad = get_object_or_404(CatEntidad, pk=pk)

    # Contactos
    contactos = list(CatContacto.objects.filter(entidad=entidad).values(
        "id", "nombres", "apellido_paterno", "apellido_materno",
        "correo", "telefono_oficina", "telefono_personal", "tipo", "puesto"
    ))

    # Solicitudes
    solicitudes_qs = CatSolicitud.objects.filter(entidad_sistema__entidad=entidad).values(
        "id", "folio", "tipo_solicitud", "fecha_solicitud", "impreso"
    )
    solicitudes = [
        {
            **s,
            "fecha_solicitud": s["fecha_solicitud"].strftime("%Y-%m-%d") if s["fecha_solicitud"] else None
        } for s in solicitudes_qs
    ]

    # Histórico (últimos 5 registros)
    historicos_qs = Historico.objects.filter(entidad=entidad).order_by("-created_at")[:5].values(
        "id", "tipo_evento", "descripcion", "created_at"
    )
    historicos = [
        {
            **h,
            "created_at": h["created_at"].strftime("%Y-%m-%d %H:%M:%S") if h["created_at"] else None
        } for h in historicos_qs
    ]

    # Sistemas
    sistemas = {}
    for sistema in entidad.entidad_sistemas.all():
        sistemas[sistema.sistema] = {
            "version": sistema.version,
            "licencia_fecha": sistema.licencia_fecha.strftime("%Y-%m-%d") if sistema.licencia_fecha else None,
            "licencia": sistema.licencia,
            "fuente": sistema.fuente,
            "operacion_fecha": sistema.operacion_fecha.strftime("%Y-%m-%d") if sistema.operacion_fecha else None,
            "operacion_modo": sistema.operacion_modo,
            "pdn_conexion": sistema.pdn_conexion,
            "pdn_fecha": sistema.pdn_fecha.strftime("%Y-%m-%d") if sistema.pdn_fecha else None,
            "pdn_tipo_conexion": sistema.pdn_tipo_conexion,
        }

    data = {
        "id": entidad.id,
        "nombre": entidad.nombre,
        "region": entidad.region,
        "municipio": entidad.municipio.nombre if entidad.municipio else "Sin municipio",
        "personalidad": entidad.personalidad,
        "patrimonio": entidad.patrimonio,
        "clasificacion": entidad.clasificacion,
        "activo": entidad.activo,
        "sistemas": sistemas,
        "contactos": contactos,
        "solicitudes": solicitudes,
        "historicos": historicos
    }

    return JsonResponse(data)
