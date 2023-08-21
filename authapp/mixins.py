from django.shortcuts import redirect

from mainapp.services import permission_denied_403


class IsAuthenticatedMixin:
    """ Для проверки аутентификации пользователя """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('authapp:login')
        return super().dispatch(request, *args, **kwargs)


class IsStaffUserMixin:
    """ Для проверки, что пользователь является персоналом и не суперпользователем """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return permission_denied_403(request)
        return super().dispatch(request, *args, **kwargs)


class IsActiveUserMixin:
    """ Для проверки, что пользователь активен """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_active:
            return permission_denied_403(request)
        return super().dispatch(request, *args, **kwargs)


class IsAdminUserMixin:
    """ Для проверки, что пользователь является суперпользователем """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return permission_denied_403(request)
        return super().dispatch(request, *args, **kwargs)
