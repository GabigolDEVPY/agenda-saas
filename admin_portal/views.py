from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .services import AdminService



class ServicesView(LoginRequiredMixin, TemplateView):
    template_name = 'admin.html'

    def get_context_data(self, **kwargs):
        context = AdminService.get_context_admin(self, **kwargs)
        return context

