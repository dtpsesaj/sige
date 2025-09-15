import os
import django
import pandas as pd
from datetime import datetime
from fuzzywuzzy import process

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sige.settings")
django.setup()

from sitio.models import CatMunicipios, CatEntidad, EntidadSistema, Historico


def to_int_or_default(value, default=0):
    """Convierte a int si es posible, si no devuelve default."""
    if pd.notna(value) and str(value).strip().isdigit():
        return int(value)
    return default


def map_choice(value, choices, default):
    """Mapea un texto a un valor de choices (CharField con choices)."""
    if pd.notna(value) and str(value).strip():
        txt = str(value).strip().lower()
        for choice, _ in choices:
            if choice.lower() in txt:
                return choice
    return default


def safe_date(value):
    """Convierte un valor a date o None."""
    if pd.notna(value) and str(value).strip():
        try:
            return pd.to_datetime(value).date()
        except Exception:
            return None
    return None


# === Configuración ===
EXCEL_FILE = "/home/ubu18/Desktop/A1.xlsx"

COLUMNS = {
    "NOMBRE": "ent_nombre",
    "REGION": "ent_region",
    "PERSONALIDAD JURÍDICA": "ent_pesonalidad",
    "PATRIMONIO PROPIO": "ent_patrimonio",
    "BASE LEGAL": "ent_base_legal",
    "AMBITO DE GOBIERNO": "ent_ambito_gobierno",
    "PODER": "ent_poder",
    "CLASIFICACIÓN": "ent_clasificacion",
    "Servidores Publicos": "ent_servidores_publicos",
    "Control Tribunal": "ent_control_tribunal",
    "ESTATUS": "ent_estatus",
    "NOMBRE DEL MUNICIPIO": "ent_municipio_nombre",
    "Sistema": "sistema",
    "Sistema Operativo": "sistema_operativo",
    "Versión": "version",
    "Fecha Interconexión S1": "pdn_conexion_fecha",
    "Forma de Conexion": "pdn_conexion_tipo",
    "URL": "url",
    "Observaciones": "observaciones",
    "Sistema S2": "s2",
    "Sistema S3": "s3",
    "Sistema S6": "s6",
    "Fecha Interconexión S2": "s2_fecha",
    "Fecha Interconexión S3": "s3_fecha",
    "Fecha Interconexión S6": "s6_fecha",
}

df = pd.read_excel(EXCEL_FILE).rename(columns=COLUMNS)

for _, row in df.iterrows():
    # Servidores públicos
    servidores_publicos = to_int_or_default(row.get("ent_servidores_publicos"))

    # Sistema S1 - Fuente y Modo
    sistemaFuente = "sin_informacion"
    sistemaModo = None
    sistemaS1 = row.get("sistema")
    if pd.notna(sistemaS1) and str(sistemaS1).strip():
        sistema_txt = str(sistemaS1).strip().lower()
        if "sideclara" in sistema_txt:
            sistemaFuente = "SESAJ"
        sistemaModo = map_choice(sistema_txt, EntidadSistema.MODO_CHOICES, None)

    # Tipo de conexión
    sistemaTipo = map_choice(row.get("pdn_conexion_tipo"), EntidadSistema.TIPO_CONEXION, "desconocido")

    # Municipio (fuzzy match)
    municipioObj = None
    mtxt = row.get("ent_municipio_nombre")
    if pd.notna(mtxt) and str(mtxt).strip():
        choices = CatMunicipios.objects.values_list("nombre", flat=True)
        best_match, score = process.extractOne(str(mtxt), choices)
        if score > 80:
            municipioObj = CatMunicipios.objects.filter(
                nombre=best_match, cat_entidades_federativas=14
            ).first()

    # Crear entidad
    entidadObj = CatEntidad.objects.create(
        nombre=row.get("ent_nombre"),
        personalidad=row.get("ent_pesonalidad"),
        region=row.get("ent_region"),
        patrimonio=row.get("ent_patrimonio"),
        base_legal=row.get("ent_base_legal"),
        ambito_gobierno=row.get("ent_ambito_gobierno"),
        poder=row.get("ent_poder"),
        clasificacion=row.get("ent_clasificacion"),
        servidores_publicos=servidores_publicos,
        control_tribunal=row.get("ent_control_tribunal"),
        estatus=row.get("ent_estatus"),
        municipio=municipioObj,
    )
    
    print("Creado:", row.get("ent_nombre"))

    # Registrar sistema S1
    EntidadSistema.objects.create(
        entidad=entidadObj,
        sistema="S1",
        fuente=sistemaFuente,
        operacion_modo=sistemaModo,
        sistema_operativo=row.get("sistema_operativo"),
        version=row.get("version"),
        pdn_fecha=safe_date(row.get("pdn_conexion_fecha")),
        pdn_tipo_conexion=sistemaTipo,
        url=row.get("url"),
    )
    print("S1 REGISTRADO")

    # Registrar sistemas S2, S3, S6 en bucle
    for sistema in ["s2", "s3", "s6"]:
        if to_int_or_default(row.get(sistema)) == 1:
            EntidadSistema.objects.create(
                entidad=entidadObj,
                sistema=sistema.upper(),
                fuente="SESAJ",
                operacion_modo="online",
                pdn_fecha=safe_date(row.get(f"{sistema}_fecha")),
            )
        print(sistema.upper()," REGISTRADO")

    # Registrar histórico
    Historico.objects.create(
        entidad=entidadObj,
        tipo_evento="default",
        descripcion=row.get("observaciones"),
    )
    print("HISTORICO CREADO")

