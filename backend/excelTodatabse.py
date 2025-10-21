import os
import django
import locale
import re
import pandas as pd
from datetime import datetime, date
from fuzzywuzzy import process


locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sige.settings")
django.setup()

from django.contrib.auth.models import User
from sitio.models import CatMunicipios, CatEntidad, EntidadSistema, Historico, EtapasSistema, CatEtapas, ObservacionEtapa

SISTEMA_CHOICES = [
    ("S1", "S1"),
    ("S2", "S2"),
    ("S3", "S3"),
    ("S4", "S4"),
    ("S5", "S5"),
    ("S6", "S6"),
]

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
    """Extrae y convierte la primera fecha válida de un texto a date o None."""
    if pd.notna(value) and str(value).strip():
        text = str(value)
        
        # Regex para encontrar fechas en formatos comunes: dd/mm/yyyy o dd/mm/yy
        match = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})", text)
        if match:
            try:
                fecha = pd.to_datetime(match.group(1), errors="coerce", dayfirst=True)
                if pd.notna(fecha):
                    return fecha.date()
            except Exception:
                return None
    return None

def safe_date_date(value):
    """Convierte un valor a datetime.date o None. Soporta string, datetime, pandas.Timestamp, NaT."""
    if pd.isna(value) or not str(value).strip():
        return None

    try:
        # Si ya es datetime o Timestamp
        if isinstance(value, (datetime, pd.Timestamp)):
            return value.date()

        # Si es string u otro formato
        fecha = pd.to_datetime(value, errors="coerce", dayfirst=True)
        if pd.isna(fecha):
            return None
        return fecha.date()

    except Exception:
        return None

def crear_etapa(entidadSistema, fecha_etapa, sistema, order, codigo, es_padre=False, descripcion="Default"):
    if not fecha_etapa:
        return None  # No se crea nada si no hay fecha válida

    try:
        # --- Buscar la etapa en el catálogo ---
        if es_padre:
            # Etapa padre (order=0 y sin parent)
            etapa_catalogo = CatEtapas.objects.filter(
                sistema=sistema,
                codigo=codigo,
                order=0,
                parent__isnull=True
            ).first()
        else:
            # Buscar primero el padre (order=0 y sin parent)
            etapa_padre = CatEtapas.objects.filter(
                sistema=sistema,
                codigo=codigo,
                order=0,
                parent__isnull=True
            ).first()

            etapa_catalogo = None
            if etapa_padre:
                # Buscar hijo de ese padre con su order
                etapa_catalogo = CatEtapas.objects.filter(
                    sistema=sistema,
                    codigo=codigo,
                    order=order,
                    parent=etapa_padre
                ).first()

        if not etapa_catalogo:
            return f"No se encontró la etapa en catálogo: {sistema} - {codigo} - order {order} (es_padre={es_padre})"

        # --- Crear la etapa en EtapasSistema ---
        newEtapaSistema = EtapasSistema.objects.create(
            fecha_etapa=fecha_etapa,
            descripcion=descripcion if descripcion else str(fecha_etapa),
            completada=bool(fecha_etapa),
            aplica=True,
            etapa=etapa_catalogo,
            entidadSistema=entidadSistema
        )
        return newEtapaSistema

    except Exception as e:
        return f"Error al crear la etapa {sistema} - {codigo} - {entidadSistema}: {str(e)}"


"""
EXCEL_FILE2 = "/home/ubu18/Desktop/A2.xlsx"

COLUMNS2 = {
    "Institución requiriente":"ente_nombre",
    "Fecha de recepción ": "s1_fecha_recepcion_solicitud",
    "Ser firmado por el titular o representante legal del ente público y dirigido al titular de la SESAJ.": "s1_solicitud_completa", 
    "Fecha de envió de correo para el llenado de Checklist ":"s1_fecha_envio_checklist",
    "Evidenciar que el ente público solicitante cumple con los requerimientos mínimos de hardware y software que requiere el sistema para su correcta operación": "s1_cumplimiento_requermientos",
    "Datos de contacto técnico":"s1_contacto",
    "Videoconferencia de inicio a la implementacion del SiDeclara SESAJ": "s1_videollamada_capacitacion",
    "Liga de la grabacion de las videoconferencias": "s1_videollamada_capacitacion_liga",
    "Aceptar explícitamente los términos y condiciones de uso, por parte del ente público solicitante.": "s1_acepta_terminos",
    "La SESAJ verifica el cumplimiento de los requisitos administrativos y técnicos": "s1_validacion_requerimientos",
    "El responsable técnico se registra e ingresa al sitio de la SESAJ para obtener el software": "s1_envio_licencia",
    "El ente público realiza la instalación, ejecuta la configuración inicial, personaliza la apariencia del sistema, activa la instancia y ejecuta el plan de pruebas.": "s1_instalacion_sistema",
    "Solicitud de conexión con la PDN.": "s1_fecha_solicitud_pdn",
    "El plan de pruebas permitirá verificar el correcto funcionamiento del sistema y la interoperabilidad con la PDN.": "s1_pruebas_pdn",
    "Observaciones": "s1_observaciones",
    "Instituciones que Declaran con el Municipio": "s1_observaciones_instituciones",
    "Solicitud Incorporación S2": "s2_solicitud",
    "Solicitud Incorporación S3": "s3_solicitud",
}


df = pd.read_excel(EXCEL_FILE2).rename(columns=COLUMNS2)

for i, row in df.iterrows():
    try:
        enteObj = None
        entSisObj = None
        mtxt = row.get("ente_nombre")

        if pd.notna(mtxt) and str(mtxt).strip():
            choices = CatEntidad.objects.values_list("nombre", flat=True)
            best_match, score = process.extractOne(str(mtxt), choices)
            if score > 80:
                enteObj = CatEntidad.objects.filter(nombre=best_match).first()
                entSisObj = EntidadSistema.objects.filter(entidad=enteObj)
        
        print("Nombre en el excel: ", row.get('ente_nombre')," << -- >> entSisObj: ", entSisObj)
        if entSisObj:
            for sistema_entidad in entSisObj:
                try:
                    if sistema_entidad.sistema == "S1":
                        print(f"Procesando entidad: {sistema_entidad.entidad.nombre} - Sistema: {sistema_entidad.sistema}")
                        print("\n")
                        # -----------------------------
                        # Etapa 1
                        # -----------------------------
                        #Se crea etapa 1 paso 0 default
                        etapa_inicial = crear_etapa(sistema_entidad, date.today(), "S1", 0, "S1_E1", True, "Default inicial")
                        #Se crear el registro con las observaciones del ente como unico y default
                        ObservacionEtapa.objects.create(
                            fecha = date.today(),
                            descripcion = row.get("s1_observaciones"),
                            etapa = etapa_inicial,
                            autor = User.objects.get(username="alejandra"),
                            tipo_interaccion = "nota"
                        )
                        #Se crea registro con las observaciones de un campo que no pertenece a la raíz, es informativo
                        ObservacionEtapa.objects.create(
                            fecha = date.today(),
                            descripcion = row.get("s1_observaciones_instituciones"),
                            etapa = etapa_inicial,
                            autor = User.objects.get(username="alejandra"),
                            tipo_interaccion = "nota"
                        )
                        
                        paso_uno = row.get("s1_fecha_recepcion_solicitud")
                        fecha_etapa = safe_date_date(paso_uno)
                        #print("s1_fecha_recepcion_solicitud --> ",paso_uno)
                        #print("s1_fecha_recepcion_solicitud --> ",fecha_etapa)
                        if fecha_etapa:
                            #print("*********** E1 Paso 0")
                            descripcion = f"Inicial: Ser firmado...: {row.get('s1_solicitud_completa')}"
                            crear_etapa(sistema_entidad, fecha_etapa, "S1", 1, "S1_E1", False, descripcion)

                        paso_dos = row.get("s1_fecha_envio_checklist")
                        fecha_etapa = safe_date_date(paso_dos)
                        #print("s1_fecha_envio_checklist --> ",paso_dos)
                        #print("s1_fecha_envio_checklist --> ",fecha_etapa)
                        if fecha_etapa:
                            crear_etapa(sistema_entidad, fecha_etapa, "S1", 2, "S1_E1", False, "Ningún comentario inicial")

                        paso_tres = row.get("s1_cumplimiento_requermientos")
                        fecha_etapa = safe_date(paso_tres)
                        #print("s1_cumplimiento_requermientos --> ",paso_tres)
                        #print("s1_cumplimiento_requermientos --> ",fecha_etapa)
                        if fecha_etapa:
                            descripcion = f"{paso_tres}\nLa SESAJ verifica requisitos: {row.get('s1_validacion_requerimientos')}"
                            crear_etapa(sistema_entidad, fecha_etapa, "S1", 3, "S1_E1", False, descripcion)

                        paso_cuatro = row.get("s1_envio_licencia")
                        fecha_etapa = safe_date(paso_cuatro)
                        #print("s1_envio_licencia --> ",paso_cuatro)
                        #print("s1_envio_licencia --> ",fecha_etapa)
                        if fecha_etapa:
                            crear_etapa(sistema_entidad, fecha_etapa, "S1", 4, "S1_E1", False, paso_cuatro)

                            paso_cinco = "Default valor: registro automático al crear usuario"
                            crear_etapa(sistema_entidad, fecha_etapa, "S1", 5, "S1_E1", False, paso_cinco)

                        # -----------------------------
                        # Etapa 2
                        # -----------------------------
                        paso_cuatro = row.get("s1_videollamada_capacitacion")
                        fecha_etapa = safe_date_date(paso_cuatro)
                        #print("s1_videollamada_capacitacion --> ",paso_cuatro)
                        #print("s1_videollamada_capacitacion --> ",fecha_etapa)
                        if fecha_etapa:
                            crear_etapa(sistema_entidad, date.today(), "S1", 0, "S1_E2", True, "Default inicial etapa 2")
                            
                            descripcion = f"{paso_cuatro}\nLiga grabación: {row.get('s1_videollamada_capacitacion_liga')}\nAcepta términos: {row.get('s1_acepta_terminos')}"
                            crear_etapa(sistema_entidad, fecha_etapa, "S1", 1, "S1_E2", False, descripcion)

                            paso_cuatro = row.get("s1_instalacion_sistema")
                            crear_etapa(sistema_entidad, fecha_etapa, "S1", 2, "S1_E2", False, paso_cuatro)

                        # -----------------------------
                        # Etapa 3
                        # -----------------------------
                        paso_uno = row.get("s1_fecha_solicitud_pdn")
                        fecha_etapa = safe_date(paso_uno)
                        #print("s1_fecha_solicitud_pdn --> ",paso_uno)
                        #print("s1_fecha_solicitud_pdn --> ",fecha_etapa)
                        if fecha_etapa:
                            crear_etapa(sistema_entidad, fecha_etapa, "S1", 0, "S1_E3", True, "Default inicial etapa 3")
                            crear_etapa(sistema_entidad, fecha_etapa, "S1", 1, "S1_E3", False, paso_uno)

                            paso_dos = row.get("s1_pruebas_pdn")
                            fecha_etapa_p2 = safe_date(paso_dos)
                            #print("s1_pruebas_pdn --> ",paso_dos)
                            #print("s1_pruebas_pdn --> ",fecha_etapa)
                            if fecha_etapa_p2:
                                crear_etapa(sistema_entidad, fecha_etapa_p2, "S1", 2, "S1_E3", False, paso_dos)

                                descripcion_p3 = f"{paso_uno}\nPruebas aprobadas default"
                                crear_etapa(sistema_entidad, fecha_etapa_p2, "S1", 3, "S1_E3", False, descripcion_p3)

                    if sistema_entidad.sistema == "S2":
                        #Se crea etapa 1 paso 0 default
                        # -----------------------------
                        # Etapa 1
                        # -----------------------------
                        paso_uno = row.get("s2_solicitud")
                        fecha_etapa = safe_date(paso_uno)
                        etapa_inicial = crear_etapa(sistema_entidad, date.today(), "S2", 0, "S2_E1", True, "Default inicial")
                        etapa_paso_uno = crear_etapa(sistema_entidad, date.today(), "S2", 1, "S2_E1", False, paso_uno)
                        print("Se ha creado etapas iniciales del S2 ")
                    
                    if sistema_entidad.sistema == "S3":
                        #Se crea etapa 1 paso 0 default
                        # -----------------------------
                        # Etapa 1
                        # -----------------------------
                        paso_uno = row.get("s3_solicitud")
                        fecha_etapa = safe_date(paso_uno)
                        etapa_inicial = crear_etapa(sistema_entidad, date.today(), "S3", 0, "S3_E1", True, "Default inicial")
                        etapa_paso_uno = crear_etapa(sistema_entidad, date.today(), "S3", 1, "S3_E1", False, paso_uno)
                        print("Se ha creado etapas iniciales del S3 ")

                except Exception as e:
                    print(f"[ERROR] Procesando sistema_entidad {sistema_entidad}: {e}")

    except Exception as e:
        print(f"[ERROR] Procesando fila {i}: {e}")
"""

# === Configuración ===
'''EXCEL_FILE = "/home/ubu18/Desktop/A1.xlsx"

COLUMNS = {
    "NOM\nE": "ent_nombre",
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

# ----------------- COMENTADO
df_filtrado = df[df["ent_nombre"] == "H. AYUNTAMIENTO DEL MUNICIPIO DE CASIMIRO CASTILLO"]
print(df_filtrado)
fila = df_filtrado.iloc[0]
for col in df_filtrado.columns:
    if col == "pdn_conexion_fecha":
        tt = pd.to_datetime(fila[col], format="%d-%b-%y", errors="coerce")
        print(f"{col}: {fila[col]}")
        print(f"{col}: {tt}")
# ------------------ COMENTADO

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
    pdn_fecha = safe_date(row.get("pdn_conexion_fecha"))

    # Registrar sistema S1
    EntidadSistema.objects.create(
        entidad = entidadObj,
        sistema = "S1",
        fuente = sistemaFuente,
        operacion_modo = sistemaModo,
        sistema_operativo = row.get("sistema_operativo"),
        version = row.get("version"),
        pdn_conexion = True if pdn_fecha else False, 
        pdn_fecha = pdn_fecha,
        pdn_tipo_conexion = sistemaTipo,
        url = row.get("url"),
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
                pdn_tipo_conexion="online",
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
'''
