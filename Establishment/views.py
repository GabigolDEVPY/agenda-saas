from django.shortcuts import render
from django.views import View
from .services import HomeService


class PublicAgenda(View):
    def get(self, request, uid):
        context = HomeService.get_context_establishment(uid)
        return render(request, 'home.html', context=context)