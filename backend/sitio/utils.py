from django.db.models import Q
from sitio.models import (CatEntidad, CatContacto, EntidadSistema, CatSolicitud,
                        Historico, EtapasSistema, ObservacionEtapa)


def entidad_datos(kwargs, modelo, entidad):
    agregar = kwargs.get("agregar", False)
    editar_id = kwargs.get("pk", False)

    q = Q(entidad=entidad)

    if agregar:
        data = None
    elif editar_id:
        data = modelo.objects.filter(
            Q(pk=editar_id) & q
            ).first()
    else:
        data = modelo.objects.filter(q).last()
    
    data_todos = modelo.objects.filter(q)

    return agregar, editar_id, data, data_todos