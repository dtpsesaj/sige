from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.viewsets import ModelViewSet

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from django.views import View
from django.urls import reverse_lazy, resolve
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.http import HttpResponseRedirect, Http404
from django.forms.models import model_to_dict

from .serializers import ( CatCategoriaSerializer, 
                    CatRespuestaDefaultSerializer, 
                    CatSolicitudSerializer, 
                    CatContactoSerializer, 
                    CatEntidadSerializer
                )
from .models import ( CatCategoria,
                    CatRespuestaDefault,
                    CatSolicitud,
                    CatContacto,
                    CatEntidad,
                    EntidadSistema,
                    Historico, 
                    ObservacionEtapa, 
                    EtapasSistema,
                    CatMunicipios
                )

from .services import get_entidad_detalles
from .forms import EntidadForm
from .utils import entidad_datos

User = get_user_model()


class EntidadView(View):
    """
    """
    template_name = 'entidades/entidad_detalles.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, id=None, *args, **kwargs):
            if id is None:  # Crear nueva
                entidad_form = EntidadForm()
                data = {"entidad": {}, "contactos": [], "sistemas": []}
                is_new = True
            else:  # Editar existente
                data = get_entidad_detalles(id)
                entidad_data = data.get("entidad", {})
                municipio_obj = CatMunicipios.objects.filter(nombre=entidad_data.get("municipio")).first()

                if entidad_data.get("usuario"):
                    usuario_obj = User.objects.filter(username=entidad_data.get("usuario")).first()
                    entidad_data["usuario"] = usuario_obj.id

                if municipio_obj:
                    entidad_data["municipio"] = municipio_obj.id

                # Se organizan los contactos por tipo
                contactos = data.get("contactos", [])
                contactos_tecnico = [c for c in contactos if c.get("tipo") == "Tecnico"]
                contactos_otros = [c for c in contactos if c.get("tipo") != "Tecnico"]

                data["contactos_tecnico"] = contactos_tecnico
                data["contactos_otros"] = contactos_otros
                del data["contactos"] # Se elimina llave principal de contactos

                entidad_form = EntidadForm(initial=entidad_data)
                is_new = False

            print("data --->", data)

            return render(request, self.template_name, {
                "form": entidad_form,
                "data": data,
                "is_new": is_new
        })

    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args, **kwargs):
        entidad_id = kwargs.get('id')

        if entidad_id == "nuevo":
            entidad_form = EntidadForm(request.POST)
        else:
            entidad = CatEntidad.objects.filter(id=entidad_id).first()
            if not entidad:
                return JsonResponse({'error': 'Entidad no encontrada'}, status=404)
            entidad_form = EntidadForm(request.POST, instance=entidad)

        if entidad_form.is_valid():
            entidad = entidad_form.save(commit=False)
            entidad.save()
            return JsonResponse({'success': True, 'id': entidad.id})
        else:
            return JsonResponse({'errors': entidad_form.errors}, status=400)

class EntidadCreateView(View):
    """
    Vista para crear una nueva entidad
    """
    template_name = 'entidades/entidad_detalles.html'

    @method_decorator(login_required(login_url='/login'))
    def get(self, request, *args, **kwargs):
        entidad_form = EntidadForm()
        context = {
            "form": entidad_form,
            "data": {
                "entidad": None,
                "contactos": [],
                "sistemas": []
            },
            "modo_creacion": True
        }
        return render(request, self.template_name, context)

    @method_decorator(login_required(login_url='/login'))
    def post(self, request, *args, **kwargs):
        entidad_form = EntidadForm(request.POST)
        if entidad_form.is_valid():
            entidad = entidad_form.save(commit=False)
            entidad.save()
            return JsonResponse({'success': True, 'id': entidad.id})
        else:
            return JsonResponse({'errors': entidad_form.errors}, status=400)


@csrf_exempt
def agregar_contacto_ajax(request, entidad_id):
    if request.method == "POST":
        entidad = get_object_or_404(CatEntidad, id=entidad_id)

        nombres = request.POST.get("nombres")
        apellido_paterno = request.POST.get("apellido_paterno")
        apellido_materno = request.POST.get("apellido_materno")
        correo = request.POST.get("correo")
        telefono_oficina = request.POST.get("telefono_oficina")
        extencion = request.POST.get("extencion")
        telefono_personal = request.POST.get("telefono_personal")
        puesto = request.POST.get("puesto")
        tipo = request.POST.get("tipo", "Otro")

        contacto = CatContacto.objects.create(
            entidad = entidad,
            nombres = nombres,
            apellido_paterno = apellido_paterno,
            apellido_materno = apellido_materno,
            correo = correo,
            telefono_oficina = telefono_oficina,
            extencion = extencion,
            telefono_personal = telefono_personal,
            puesto = puesto,
            tipo = tipo,
            creado_por = request.user 
        )

        return JsonResponse({"success": True, "message": "Contacto agregado correctamente."})

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=400)

@login_required
@csrf_exempt
def actualizar_contacto_ajax(request, entidad_id, contacto_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)

    try:
        contacto = CatContacto.objects.get(id=contacto_id, entidad_id=entidad_id)
    except CatContacto.DoesNotExist:
        return JsonResponse({"success": False, "error": "Contacto no encontrado"}, status=404)

    # Campos que pueden actualizarse
    campos_actualizables = [
        "nombres", "apellido_paterno", "apellido_materno", "puesto",
        "correo", "telefono_oficina", "extencion", "telefono_personal"
    ]
    for campo in campos_actualizables:
        valor = request.POST.get(campo)
        if valor is not None:
            setattr(contacto, campo, valor)

    contacto.save()
    return JsonResponse({"success": True, "id": contacto.id})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('entidades') 

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('sitio:entidades')  # Cambia por tu URL principal
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('sitio:login')

def password_reset_request(request):
    if request.method == "POST":
        identificador = request.POST.get("identificador")
        if "@" in identificador:
            email = identificador
        else:
            # Si es username, buscar el email del usuario
            user = User.objects.filter(username=identificador).first()
            if user:
                email = user.email
            else:
                email = None


        form = PasswordResetForm({'email': email})
        if email:
            if form.is_valid():
                user = User.objects.filter(email=email).first()
                if user:
                    subject = "Recuperar contraseña - SIGE"
                    html_message = render_to_string(
                        "mails/password_reset_email.html",
                        {
                            "email": user.email,
                            "domain": request.get_host(),
                            "site_name": "SIGE",
                            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                            "user": user,
                            "token": default_token_generator.make_token(user),
                            "protocol": "https" if request.is_secure() else "http",
                        },
                    )
                    text_message = strip_tags(html_message)  # Versión texto plano por seguridad
                    from_email = None  # Se tomará de DEFAULT_FROM_EMAIL en settings.py
                    try:
                        msg = EmailMultiAlternatives(subject, text_message, from_email, [user.email])
                        msg.attach_alternative(html_message, "text/html")  # Aquí va el HTML
                        msg.send()
                        return JsonResponse({"ok": True, "message": "Se envió un correo con las instrucciones."})
                    except Exception as e:
                        return JsonResponse({"ok": False, "message": f"Error enviando correo: {e}"})
                else:
                    return JsonResponse({"ok": False, "message": "No existe una cuenta con ese correo."})
            else:
                return JsonResponse({"ok": False, "message": "Correo inválido"})
        else:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        
    return JsonResponse({"ok": False, "message": "Método no permitido."})


def modulo_entidades(request):
    entidades = CatEntidad.objects.select_related("municipio").all()
    paginator = Paginator(entidades, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "dashboard/entidades.html", {
        "page_obj": page_obj,"entidades": entidades
    })


def modulo_estadisticas(request):

    return render(request, "dashboard/estadisticas.html", {})


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