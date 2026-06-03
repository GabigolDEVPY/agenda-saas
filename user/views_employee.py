from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .forms import EmployeeCreationForm
from establishment.mixins.mixins import OwnerRequiredMixin




class EmployeeCreateView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def post(self, request):
        data = request.POST
        form = EmployeeCreationForm(data)
        
        if form.is_valid():
            response = super().form_valid(form)
            user = self.object
            user.establishment = request.user.establishment
            user.save()
            return response
