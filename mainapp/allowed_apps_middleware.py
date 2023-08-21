from urllib import parse

from django.core.handlers.wsgi import WSGIRequest

from mainapp.services import get_user_opportunities_apps, permission_denied_403


class AllowedAppsMiddleware:
    """ Служит для """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: WSGIRequest):
        # Получим из url строки имя приложения
        app_name_from_path = parse.urlsplit(request.get_full_path_info()).path.split('/')[1]
        # print(app_name_from_path, request.get_full_path_info())
        user_opportunities_apps = get_user_opportunities_apps(request)

        for app in user_opportunities_apps:
            if app_name_from_path == app[0] and not app[1]:
                return permission_denied_403(request)

        response = self.get_response(request)

        return response
