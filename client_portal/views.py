from django.shortcuts import render
from django.views import View
from .services.services import HomeService
from appointment.models import Appointment


class PublicAgenda(View):
    def get(self, request, uid):
        if not request.session.session_key:
            request.session.save()
        context = HomeService.get_context_establishment(uid)
        if context.get("incomplete"):
            return render(request, 'unavailable.html', context=context)  
        request.session["uid"] = uid
        return render(request, 'home.html', context=context)
    
class Appointments(View):
    def get(self, request):
        if not request.session.session_key:
            request.session.save()
        print(request.session.items())
        print(request.session.session_key)
        # Implementation for displaying appointments
        return render(request, 'appointments_client.html', context={"appointments": Appointment.objects.filter(session_key=request.session.session_key)})
        pass