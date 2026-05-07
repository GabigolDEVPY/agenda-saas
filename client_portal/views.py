from django.shortcuts import render
from django.views import View
from .services.services import HomeService


class PublicAgenda(View):
    def get(self, request, uid):
        context = HomeService.get_context_establishment(uid)
        if context.get("incomplete"):
            return render(request, 'unavailable.html', context=context)  
        return render(request, 'home.html', context=context)