"""Понятная ошибка недоступного хранилища."""
from django.db import OperationalError, ProgrammingError
from django.utils.deprecation import MiddlewareMixin
from db.database import DataUnavailable


class DataErrorMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, (DataUnavailable, OperationalError,
                                  ProgrammingError)):
            from homepage.views import data_unavailable
            return data_unavailable(request)
        return None
