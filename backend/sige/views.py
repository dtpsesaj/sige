from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class DocsView(LoginRequiredMixin, TemplateView):
    template_name = 'docs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schema_url'] = 'api_schema'
        return context
    

class RedocView(LoginRequiredMixin, TemplateView):
    template_name = 'redoc.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schema_url'] = 'api_schema'
        return context