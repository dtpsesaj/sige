from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q
from django.db.models.functions import ExtractYear
from . import utils

from sitio.models import EntidadSistema, CatEntidad  # ajusta import si tu app/model están en otro lugar

# -- Vista HTML (template) --
def dashboard_estadisticas(request):
    return render(request, "estadisticas.html", {})


# -- API: cantidad de entidades por sistema (S1..S6) --
class EntidadesPorSistemaAPI(APIView):
    """
    Devuelve: { "systems": ["S1","S2"...], "counts": [12,34,...] }
    Cuenta entidades distintas por sistema (EntidadSistema.entidad).
    """
    permission_classes = []  # agrega permisos si hace falta

    def get(self, request, *args, **kwargs):
        qs = EntidadSistema.objects.all().exclude(sistema__isnull=True).exclude(sistema__exact="")
        # contar entidades distintas por sistema
        agg = qs.values("sistema").annotate(count=Count("entidad", distinct=True)).order_by("sistema")

        # Queremos garantizar orden S1..S6 aunque falte alguno
        sistemas_orden = ["S1","S2","S3","S4","S5","S6"]
        counts_map = {row["sistema"]: row["count"] for row in agg}
        counts = [counts_map.get(s, 0) for s in sistemas_orden]

        return Response({
            "systems": sistemas_orden,
            "counts": counts
        })


# -- API: entidades conectadas por año por sistema --
class EntidadesConectadasPorAnioAPI(APIView):
    """
    Devuelve:
    {
        "years": ["2019","2020","2021",...],
        "datasets": [
            {"label":"S1","data":[5,7,10,...]},
            ...
        ]
    }

    Usa 'pdn_fecha' si existe, si quieres cambiar a 'operacion_fecha' modifica la referencia.
    """
    permission_classes = []  # ajustar según sea necesario

    def get(self, request, *args, **kwargs):
        # elegir campo de fecha para "conectado": pdn_fecha preferido, si no usar operacion_fecha
        fecha_field = "pdn_fecha"  # puedes parametrizar por query param
        qs = EntidadSistema.objects.filter(**{f"{fecha_field}__isnull": False}).exclude(sistema__isnull=True).exclude(sistema__exact="")

        # obtener rango de años presentes
        years_qs = qs.annotate(year=ExtractYear(fecha_field)).values("year").distinct().order_by("year")
        years = [str(item["year"]) for item in years_qs if item["year"] is not None]

        # si no hay años, devolver vacío
        if not years:
            return Response({"years": [], "datasets": []})

        sistemas = ["S1","S2","S3","S4","S5","S6"]

        datasets = []
        for sistema in sistemas:
            # contar entidades por año para este sistema (contar entidades distintas)
            sub_qs = qs.filter(sistema=sistema).annotate(year=ExtractYear(fecha_field)).values("year").annotate(count=Count("entidad", distinct=True))
            # convertir a map year->count
            year_map = {row["year"]: row["count"] for row in sub_qs if row["year"] is not None}
            data = [year_map.get(int(y), 0) for y in years]  # years son strings
            datasets.append({
                "label": sistema,
                "data": data
            })

        return Response({
            "years": years,
            "datasets": datasets
        })


# -- API: distribución de un sistema por región --
class SistemasPorRegionAPI(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        sistema = request.GET.get("sistema", "S1")
        anio = request.GET.get("anio")
        region = request.GET.get("region")

        qs = EntidadSistema.objects.filter(sistema=sistema, activo=True).select_related("entidad")

        # filtros opcionales
        if anio:
            qs = qs.filter(pdn_fecha__year=anio)
        if region:
            qs = qs.filter(entidad__region=region)

        agg = qs.values("entidad__region").annotate(count=Count("entidad", distinct=True)).order_by("entidad__region")

        labels = [row["entidad__region"] or "Sin región" for row in agg]
        counts = [row["count"] for row in agg]

        return Response({
            "labels": labels,
            "counts": counts,
            "sistema": sistema
        })



# -- API: versiones del Sistema 1 (S1) --
class VersionesSistema1API(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        anio = request.GET.get("anio")
        region = request.GET.get("region")

        qs = EntidadSistema.objects.filter(sistema="S1", activo=True).exclude(version__isnull=True).exclude(version__exact="")

        # filtros opcionales
        if anio:
            qs = qs.filter(pdn_fecha__year=anio)
        if region:
            qs = qs.filter(entidad__region=region)

        agg = qs.values("version").annotate(count=Count("entidad", distinct=True)).order_by("version")

        labels = [row["version"] for row in agg]
        counts = [row["count"] for row in agg]

        return Response({
            "labels": labels,
            "counts": counts
        })