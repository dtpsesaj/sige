from django.shortcuts import get_object_or_404
from .models import CatEntidad, CatContacto, EntidadSistema, CatSolicitud, Historico, EtapasSistema, ObservacionEtapa

def get_entidad_detalles(entidad_id):
    """
    Obtiene los datos completos de una entidad, sin acoplarlos a DRF.
    Retorna un dict con los datos listos para usar.
    """
    entidad = get_object_or_404(CatEntidad, id=entidad_id)

    contactos = list(CatContacto.objects.filter(entidad=entidad).values(
        "id", "created_at","nombres", "apellido_paterno", "apellido_materno",
        "correo", "telefono_oficina", "extencion", "creado_por__username", "telefono_personal", "tipo", "puesto"
    ))

    sistemas = list(EntidadSistema.objects.filter(entidad=entidad).values(
        "id", "sistema", "version", "licencia", "licencia_fecha",
        "fuente", "operacion_modo", "operacion_fecha", "pdn_conexion",
        "pdn_fecha", "pdn_tipo_conexion", "url"
    ))

    sistemas_existentes = {s["sistema"]: s for s in sistemas}

    sistemas_completos = []
    for i in range(1, 7):
        clave = f"S{i}"
        if clave in sistemas_existentes:
            sistemas_completos.append({
                **sistemas_existentes[clave],
                "tiene_datos": True
            })
        else:
            sistemas_completos.append({
                "sistema": clave,
                "tiene_datos": False,
                "version": None,
                "licencia": None,
                "licencia_fecha": None,
                "fuente": None,
                "operacion_modo": None,
                "operacion_fecha": None,
                "pdn_conexion": None,
                "pdn_fecha": None,
                "pdn_tipo_conexion": None,
                "url": None
            })

    solicitudes = list(CatSolicitud.objects.filter(entidad_sistema__entidad=entidad).values(
        "id", "folio", "tipo_solicitud", "fecha_solicitud", "impreso"
    ))

    historicos = list(Historico.objects.filter(entidad=entidad)
                    .order_by("-created_at")[:5]
                    .values("id", "tipo_evento", "descripcion", "created_at"))

    return {
        "id": entidad.id,
        "entidad": {
            "id": entidad.id,
            "nombre": entidad.nombre,
            "region": entidad.region,
            "municipio": entidad.municipio.nombre if entidad.municipio else "Sin municipio",
            "personalidad": entidad.personalidad,
            "poder": entidad.poder,
            "patrimonio": entidad.patrimonio,
            "ambito_gobierno": entidad.ambito_gobierno,
            "control_tribunal": entidad.control_tribunal,
            "base_legal": entidad.base_legal,
            "clasificacion": entidad.clasificacion,
            "servidores_publicos": entidad.servidores_publicos,
            "usuario": entidad.usuario.username if entidad.usuario else False,
            "activo": entidad.activo,
        },
        "contactos": contactos,
        "sistemas": sistemas_completos,
        "solicitudes": solicitudes,
        "historicos": historicos,
    }

def get_etapas_por_sistema_entidad(entidad_sistema):
    """
    Obtiene las etapas de un sistema por entidad en un rango de fechas.
    """
    etapas_qs = EtapasSistema.objects.filter(etapa_sistema_entidad=entidad_sistema)

    etapas_data = []
    for etapa in etapas_qs:
        observaciones = ObservacionEtapa.objects.filter(etapa=etapa).values(
            "id", "descripcion", "tipo_interaccion", "fecha", "autor__username"
        )
        etapas_data.append({
            "id": etapa.id,
            "codigo": etapa.etapa.codigo,
            "nombre": etapa.etapa.nombre,
            "fecha_etapa": etapa.fecha_etapa,
            "descripcion": etapa.descripcion,
            "completada": etapa.completada,
            "observaciones": list(observaciones),
        })
    
    return etapas_data
