from django.http import HttpResponseForbidden

class OwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_owner:
            return HttpResponseForbidden("Você não tem permissão.")

        return super().dispatch(request, *args, **kwargs)