from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='/login')
def mesa_ayuda(request):
    """
    Vista principal de la mesa de ayuda.
    Solo renderiza la plantilla base.
    """
    return render(request, 'helpdesk/helpdesk_main.html')