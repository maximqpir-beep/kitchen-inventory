from django.conf import settings


def project(request):
    return {
        "site_title": settings.SITE_TITLE,
        "student_group": settings.STUDENT_GROUP,
    }
