from django.shortcuts import render
from django.views import View
from .services import HomeService


class PublicAgenda(View):
    def get(self, request, uid):
        try:
            context = HomeService.get_context_establishment(uid)
        except Exception as e:
            return render(request, 'unavailable.html')  
        return render(request, 'home.html', context=context)