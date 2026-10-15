"""Понятный HTTP-ответ вместо трассировки при ошибке JSON."""

from django.utils.deprecation import MiddlewareMixin

from .source import DataUnavailable


class DataErrorMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, DataUnavailable):
            from homepage.views import data_unavailable
            return data_unavailable(request)
        return None
