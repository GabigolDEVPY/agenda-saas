from urllib import request

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Establishment
from django.views import View
from . services import HomeService


class PublicAgenda(View):
    def get(self, request, uid):
        context = HomeService.get_context_establishment(uid)

        return render(request, 'home.html', context=context)
