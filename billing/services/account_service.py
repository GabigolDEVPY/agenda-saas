from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout

class AccountService:
    @staticmethod
    @transaction.atomic
    def delete_account(request, user):
        """
        Permanently deletes the owner's user account and everything associated with it
        in cascade, then performs logout.
        """
        if not user or not user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado.")
            
        if not user.is_owner:
            raise PermissionDenied("Apenas o proprietário do estabelecimento pode excluir a conta permanentemente.")
            
        # Logging out the user first so their session is cleaned up
        logout(request)
        
        # Deleting the owner user triggers cascade delete for all associated resources:
        # User -> Establishment (OneToOne CASCADE)
        # Establishment -> other Users (employees) (ForeignKey CASCADE)
        # Users -> Preferences, Subscription, Services, Appointments, Availabilities (CASCADE)
        # Establishment -> Address, OperatingHours, GeneralPreference (CASCADE)
        user.delete()
        return True
