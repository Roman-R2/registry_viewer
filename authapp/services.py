def check_next_in_request(request):
    """
    Проверяет наличие слова 'next' в объекте запроса request методе POST
    :param request:
    :return:
    """
    return True if 'next' in request.POST else False


def get_client_ip(request):
    """ Вернет ip клиента. """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
